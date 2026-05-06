# core/services/purchase_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from schemas.track import TrackResponse
from core.repositories.purchase_repository import PurchaseRepository
from core.repositories.track import TrackRepository
from core.repositories.user import UserRepository
from core.services.contract_service import ContractService
from database.models import User, LicenseType, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PurchaseService:
    def __init__(self, session: AsyncSession, contract_service: ContractService):
        self.session = session
        self.purchase_repo = PurchaseRepository(session)
        self.track_repo = TrackRepository(session)
        self.user_repo = UserRepository(session)
        self.contract_service = contract_service

    def _get_price_for_license(self, track, license_type: LicenseType) -> float:
        """Определить цену в зависимости от типа лицензии.
           Здесь можно реализовать логику: например, стандартная = цена трека,
           расширенная = цена * 2, эксклюзивная = цена * 5.
        """
        if license_type == LicenseType.standard:
            return track.price
        elif license_type == LicenseType.extended:
            return track.price * 2
        else:  # exclusive
            return track.price * 5

    async def _get_or_create_guest_user(self, name: str, email: str) -> User:
        """Поиск пользователя по email, иначе создание гостя."""
        user = await self.user_repo.get_by_email(email)
        if user:
            return user
        # Создаём гостя
        hashed_password = pwd_context.hash("")  # пустой пароль, гость не может войти
        user = User(
            full_name=name,
            login=email.split('@')[0],  # может быть коллизия, но для гостя сойдёт
            password_hash=hashed_password,
            email=email,
            role=UserRole.user,
            is_active=True
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def purchase_track_with_data(
        self,
        track_id: int,
        buyer_name: str,
        buyer_email: str,
        license_type: LicenseType,
        comment: str = None,
        current_user: User = None
    ) -> dict:
        """Универсальный метод покупки, работающий как для авторизованных, так и для гостей."""
        # 1. Проверяем существование трека
        track = await self.track_repo.get(track_id)
        if track.is_exclusive_sold:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Трек уже продан по эксклюзивной лицензии и недоступен для покупки."
            )
        if not track:
            raise HTTPException(status_code=404, detail="Трек не найден")
        print(f"айди пользователя: {current_user.id}")
        print(f"айди автора: {track.author.user_id}")
        if current_user and track.author.user_id == current_user.id:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы не можете купить собственный трек"
            )
        # 3. Определяем пользователя
        if current_user:
            user = current_user
            # Дополнительно обновим имя/email, если они переданы и отличаются
            if buyer_name and buyer_name != user.full_name:
                user.full_name = buyer_name
            if buyer_email and buyer_email != user.email:
                user.email = buyer_email
                # Можно также обновить логин, но это сложнее, опустим
            self.session.add(user)
        else:
            user = await self._get_or_create_guest_user(buyer_name, buyer_email)

        # 4. Проверка, не покупал ли пользователь уже этот трек (если это не эксклюзив, можно купить повторно? Обычно нет)
        user_purchase = await self.purchase_repo.get_user_purchase_for_track(user.id, track_id)
        if user_purchase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже приобрели этот трек."
            )

        # 5. Вычисляем цену в зависимости от типа лицензии
        amount = self._get_price_for_license(track, license_type)

        # 6. Создаём запись покупки
        purchase = await self.purchase_repo.create(
            user_id=user.id,
            track_id=track.id,
            amount=amount,
            license_type=license_type,
            comment=comment
        )

        # 7. Генерируем договор
        try:
            document_url = await self.contract_service.generate_contract(purchase.id)
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Ошибка генерации договора: {str(e)}")

        # 8. Сохраняем ссылку на договор
        await self.contract_service.contract_repo.create(
            purchase_id=purchase.id,
            contract_number=f"BEAT-{purchase.id}",
            document_url=document_url
        )

        # 9. Если куплена эксклюзивная лицензия, помечаем трек как эксклюзивный (чтобы больше не продавался)
        if license_type == LicenseType.exclusive:
            track.is_exclusive_sold = True
            self.session.add(track)

        await self.session.commit()
        track_data = TrackResponse.model_validate(track).model_dump()
        # 10. Возвращаем результат
        return {
            "purchase_id": purchase.id,
            "track": track_data,
            "amount": amount,
            "purchase_date": purchase.purchase_date,
            "contract_url": document_url,
            "license_type": license_type.value
        }
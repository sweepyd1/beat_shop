
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.services.purchase_service import PurchaseService
from core.services.contract_service import ContractService
from core.services.file_service import FileService
from api.dependencies import get_current_user_optional, get_current_user_without_active, get_db_session, get_current_user
from database.models import LicenseType, User
from schemas.purchase import PurchaseRequest, PurchaseResponse
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/purchase", tags=["purchase"])

async def get_purchase_service(
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(lambda: FileService())
) -> PurchaseService:
    contract_service = ContractService(session, file_service)
    return PurchaseService(session, contract_service)


@router.post("/purchases", response_model=dict)
async def create_purchase(
    data: PurchaseRequest,
    current_user: Optional[User] = Depends(get_current_user),
    service: PurchaseService = Depends(get_purchase_service)
):
    """
    Создание покупки (для авторизованных и гостей).
    """
    try:
        result = await service.purchase_track_with_data(
            track_id=data.track_id,
            buyer_name=data.buyer_name,
            buyer_email=data.buyer_email,
            license_type=LicenseType(data.license_type),
            comment=data.comment,
            current_user=current_user
        )
        return result
    except HTTPException as e:
        
        raise e
    except Exception as e:
        
        print(f"Неожиданная ошибка при создании покупки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера. Попробуйте позже."
        )

@router.post("/{track_id}", response_model=dict)
async def purchase_track(
    track_id: int,
    current_user: User = Depends(get_current_user),
    service: PurchaseService = Depends(get_purchase_service)
):
    """Купить трек. Для эксклюзивных треков проверяет, что ещё никто не купил."""
    result = await service.purchase_track(current_user, track_id)
    return result
async def get_contract_file(
    purchase_id: int,
    current_user: User,
    session: AsyncSession,
    file_service: FileService
):
    contract_service = ContractService(session, file_service)
    contract = await contract_service.get_contract_by_purchase_id(purchase_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Договор не найден")

    from core.repositories.purchase import PurchaseRepository
    from database.models import Track, Author, UserRole
    
    purchase_repo = PurchaseRepository(session)
    purchase = await purchase_repo.get_by_id(purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Покупка не найдена")
    
    # Проверяем права доступа
    has_access = False
    
    # 1. Покупатель может скачать свой договор
    if purchase.user_id == current_user.id:
        has_access = True
    # 2. Администратор может скачать любой договор
    elif current_user.role == UserRole.admin:
        has_access = True
    # 3. Автор трека может скачать договор о продаже своего трека
    else:
        track = await session.get(Track, purchase.track_id)
        if track:
            author = await session.get(Author, track.author_id)
            if author and author.user_id == current_user.id:
                has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому договору")

    if not contract.document_url:
        raise HTTPException(status_code=404, detail="Файл договора не найден")

    file_path = os.path.join("uploads", contract.document_url.lstrip("/uploads/"))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл договора отсутствует на сервере")

    return FileResponse(file_path, media_type="application/pdf", filename=f"contract_{contract.contract_number}.pdf")


@router.get("/{purchase_id}/contract")
async def download_contract(
    purchase_id: int,
    current_user: User = Depends(get_current_user_without_active),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(lambda: FileService())
):
    return await get_contract_file(purchase_id, current_user, session, file_service)

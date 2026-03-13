from core.repositories.purchase import PurchaseRepository
from core.repositories.track import TrackRepository

class PurchaseService:
    def __init__(self, repo: PurchaseRepository, track_repo: TrackRepository = None):
        self.repo = repo
        self.track_repo = track_repo  # может понадобиться для проверки трека

    async def get_user_purchases(self, user_id: int):
        """Возвращает список покупок пользователя с деталями треков"""
        purchases = await self.repo.get_user_purchases(user_id)
        return purchases

    async def is_purchased(self, user_id: int, track_id: int) -> bool:
        return await self.repo.is_purchased(user_id, track_id)

    # Дополнительно: метод для создания покупки (при оплате)
    async def create_purchase(self, user_id: int, track_id: int, amount: float):
        # Здесь можно добавить бизнес-логику (например, проверка, что трек существует и не куплен ранее)
        purchase = await self.repo.create(
            user_id=user_id,
            track_id=track_id,
            amount=amount,
            status='completed'
        )
        return purchase
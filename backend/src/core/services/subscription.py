from core.repositories.subscription import SubscriptionRepository

class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository):
        self.repo = repo

    async def subscribe(self, user_id: int, author_id: int):
        # Проверить, не подписан ли уже
        existing = await self.repo.get_by_user_and_author(user_id, author_id)
        if existing:
            return existing  # уже подписан
        subscription = await self.repo.create(user_id=user_id, author_id=author_id)
        return subscription

    async def unsubscribe(self, user_id: int, author_id: int):
        subscription = await self.repo.get_by_user_and_author(user_id, author_id)
        if subscription:
            await self.repo.delete(subscription.id)
            return True
        return False
    
    async def get_user_subscriptions(self, user_id: int):
        """Возвращает список подписок пользователя с данными об авторах"""
        return await self.repo.get_user_subscriptions(user_id)
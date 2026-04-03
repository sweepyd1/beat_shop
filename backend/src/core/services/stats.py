from datetime import datetime, timedelta
from schemas.admin_stats import DailyUsersResponse
from schemas.stats import StatsResponse
from core.repositories.purchase import PurchaseRepository
from core.repositories.subscription import SubscriptionRepository

class StatsService:
    def __init__(self, purchase_repo: PurchaseRepository, subscription_repo: SubscriptionRepository):
        self.purchase_repo = purchase_repo
        self.subscription_repo = subscription_repo

    async def get_author_stats(self, author_id: int):
       
        # общая выручка (не используется в ответе StatsResponse, но может понадобиться для AuthorDetailResponse)
        total_earnings = await self.purchase_repo.get_author_total_earnings(author_id)
        # продажи и доход за месяц
        sales_count, monthly_earnings = await self.purchase_repo.get_author_monthly_stats(author_id)
        # график продаж за последние 7 дней
        chart = await self.purchase_repo.get_last_7_days_sales(author_id)

        # средний рейтинг – заглушка (можно вычислить из отзывов или соотношения лайков/прослушиваний)
        average_rating = 0.0

        return StatsResponse(
            sales_this_month=sales_count,
            monthly_earnings=monthly_earnings,
            average_rating=average_rating,
            sales_chart=chart,
            followers_count=0
        )
    async def get_total_earnings(self, author_id: int) -> float:
        """Общая выручка автора за всё время"""
        return await self.purchase_repo.get_author_total_earnings(author_id)
    async def get_daily_users(self, days: int = 7) -> list[DailyUsersResponse]:
        result = []
        for i in range(days-1, -1, -1):
            day = datetime.now().date() - timedelta(days=i)
            count = await self.user_repo.count_registered_on_date(day)
            result.append(DailyUsersResponse(date=day, count=count))
        return result
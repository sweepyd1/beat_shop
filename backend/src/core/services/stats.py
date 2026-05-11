from datetime import datetime, timedelta
from core.repositories.interaction import InteractionRepository
from core.repositories.track import TrackRepository
from schemas.author_stats import AuthorFullStatsResponse, LicenseSalesStats, MonthlyEarnings, TopTrackStats
from schemas.admin_stats import DailyUsersResponse
from schemas.stats import StatsResponse
from core.repositories.purchase import PurchaseRepository
from core.repositories.subscription import SubscriptionRepository

class StatsService:
    def __init__(self, purchase_repo: PurchaseRepository, subscription_repo: SubscriptionRepository, track_repo:TrackRepository, interaction_repo: InteractionRepository):
        self.purchase_repo = purchase_repo
        self.subscription_repo = subscription_repo
        self.track_repo = track_repo
        self.interaction_repo = interaction_repo
        

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
    
    async def get_author_full_stats(self, author_id: int) -> AuthorFullStatsResponse:
        # Параллельный вызов всех методов
        total_tracks = await self.track_repo.count_by_author(author_id)
        total_plays = await self.interaction_repo.count_plays_by_author(author_id)
        total_favorites = await self.interaction_repo.count_favorites_by_author(author_id)
        # total_subscribers = await self.subscription_repo.count_subscribers(author_id)
        total_earnings = await self.purchase_repo.get_author_total_earnings(author_id)
        sales_this_month, monthly_earnings = await self.purchase_repo.get_author_monthly_stats(author_id)
        sales_chart = await self.purchase_repo.get_last_7_days_sales_count(author_id)
        plays_chart = await self.interaction_repo.get_last_7_days_plays(author_id)
        earnings_by_month = await self.purchase_repo.get_monthly_earnings_last_n_months(author_id, 6)
        sales_by_license = await self.purchase_repo.get_sales_by_license_type(author_id)
        top_tracks_sales = await self.purchase_repo.get_top_tracks_by_sales(author_id, 5)
        top_tracks_plays = await self.track_repo.get_top_tracks_by_plays(author_id, 5)

        # Преобразуем в Pydantic модели
        sales_by_license_models = [
            LicenseSalesStats(license_type=item['license_type'], count=item['count'], total_amount=item['total_amount'])
            for item in sales_by_license
        ]
        top_tracks_sales_models = [
            TopTrackStats(
                track_id=item['track_id'], title=item['title'], cover_url=item.get('cover_url'),
                sales_count=item['sales_count'], plays=0,  # plays можно подтянуть отдельно или оставить 0
                revenue=item['revenue']
            ) for item in top_tracks_sales
        ]
        top_tracks_plays_models = [
            TopTrackStats(
                track_id=item['track_id'], title=item['title'], cover_url=item.get('cover_url'),
                sales_count=0, plays=item['plays'], revenue=0.0
            ) for item in top_tracks_plays
        ]
        monthly_earnings_models = [
            MonthlyEarnings(month=item['month'], amount=item['amount'])
            for item in earnings_by_month
        ]

        return AuthorFullStatsResponse(
            total_tracks=total_tracks,
            total_plays=total_plays,
            total_favorites=total_favorites,
            total_subscribers=0,
            total_earnings=total_earnings,
            sales_this_month=sales_this_month,
            monthly_earnings=monthly_earnings,
            sales_chart_last_7_days=sales_chart,
            plays_chart_last_7_days=plays_chart,
            earnings_last_6_months=monthly_earnings_models,
            sales_by_license=sales_by_license_models,
            top_tracks_by_sales=top_tracks_sales_models,
            top_tracks_by_plays=top_tracks_plays_models,
            average_rating=0.0  # заменить на реальный, когда появится
        )
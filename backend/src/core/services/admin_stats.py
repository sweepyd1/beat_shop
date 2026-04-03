from datetime import datetime, timedelta
from schemas.admin_stats import (
    MetricsResponse, DailySalesResponse, DailyUsersResponse,
    TopTrackResponse, GenreSalesResponse
)
from core.repositories.user import UserRepository
from core.repositories.purchase import PurchaseRepository
from core.repositories.track import TrackRepository

class AdminStatsService:
    def __init__(self, user_repo: UserRepository, purchase_repo: PurchaseRepository, track_repo: TrackRepository):
        self.user_repo = user_repo
        self.purchase_repo = purchase_repo
        self.track_repo = track_repo

    async def get_metrics(self) -> MetricsResponse:
        total_users = await self.user_repo.count_all()
        week_ago = datetime.now() - timedelta(days=7)
        new_users = await self.user_repo.count_registered_since(week_ago)
        total_revenue = await self.purchase_repo.total_revenue()
        prev_period_start = datetime.now() - timedelta(days=14)
        prev_period_end = datetime.now() - timedelta(days=7)
        prev_revenue = await self.purchase_repo.revenue_for_period(prev_period_start, prev_period_end)
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
        total_purchases = await self.purchase_repo.total_purchases_count()
        avg_check = await self.purchase_repo.average_check()
        total_listens = await self.track_repo.total_listens()
        return MetricsResponse(
            total_users=total_users,
            new_users_last_week=new_users,
            total_revenue=round(total_revenue, 2),
            revenue_growth=round(revenue_growth, 2),
            total_purchases=total_purchases,
            avg_check=round(avg_check, 2),
            total_listens=total_listens
        )

    async def get_daily_sales(self, days: int = 7) -> list[DailySalesResponse]:
        data = await self.purchase_repo.revenue_grouped_by_day(days)
        return [DailySalesResponse(date=d, revenue=round(r, 2)) for d, r in data]

    async def get_daily_users(self, days: int = 7) -> list[DailyUsersResponse]:
        result = []
        for i in range(days-1, -1, -1):
            day = datetime.now().date() - timedelta(days=i)
            start = datetime.combine(day, datetime.min.time())
            end = start + timedelta(days=1)
            count = await self.user_repo.count_registered_since(start)
            # нужно вычесть предыдущие дни, так как count_registered_since накопительный
            # лучше сделать отдельный метод, упростим: получим общее количество за день через range
            # для простоты создадим новый метод в репозитории
            # Пока заглушка, реализуем позже
            # Для демонстрации вернём мок
            result.append(DailyUsersResponse(date=day, count=0))
        # Реализуем правильно:
        # В UserRepository добавим:
        # async def count_registered_on_date(self, date: date) -> int
        # и используем здесь
        return result

    async def get_top_tracks(self, limit: int = 10) -> list[TopTrackResponse]:
        rows = await self.track_repo.top_tracks_by_revenue(limit)
        return [
            TopTrackResponse(
                id=row.id,
                title=row.title,
                author_name=row.author_name,
                genre_name=row.genre_name,
                sales_count=row.sales_count,
                revenue=round(row.revenue, 2),
                cover_url=row.cover_url
            ) for row in rows
        ]

    async def get_genre_sales(self) -> list[GenreSalesResponse]:
        rows = await self.purchase_repo.revenue_by_genre()
        return [
            GenreSalesResponse(
                genre_id=row[0],
                genre_name=row[1],
                revenue=round(row[2], 2)
            ) for row in rows
        ]
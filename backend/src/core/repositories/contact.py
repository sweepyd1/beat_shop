from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import ContactMessage

class ContactMessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message_data: dict) -> ContactMessage:
        message = ContactMessage(**message_data)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_all(self, skip: int = 0, limit: int = 100, only_unread: bool = False):
        query = select(ContactMessage)
        if only_unread:
            query = query.where(ContactMessage.is_read == False)
        query = query.order_by(ContactMessage.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def mark_as_read(self, message_id: int) -> bool:
        stmt = update(ContactMessage).where(ContactMessage.id == message_id).values(is_read=True)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return res.rowcount > 0
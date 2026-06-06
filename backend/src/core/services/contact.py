from core.repositories.contact import ContactMessageRepository
from schemas.contact import ContactMessageCreate

class ContactMessageService:
    def __init__(self, repo: ContactMessageRepository):
        self.repo = repo

    async def send_message(self, message_data: ContactMessageCreate, user_id: int | None = None) -> dict:
        data = message_data.model_dump()
        if user_id:
            data['user_id'] = user_id
        message = await self.repo.create(data)
        return {"id": message.id, "status": "sent"}

    async def get_messages(self, skip: int, limit: int, only_unread: bool = False):
        return await self.repo.get_all(skip, limit, only_unread)

    async def mark_read(self, message_id: int):
        return await self.repo.mark_as_read(message_id)
    async def delete_message(self, message_id: int) -> bool:
        return await self.repo.delete(message_id)
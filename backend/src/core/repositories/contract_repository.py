# core/repositories/contract_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Contract
import uuid

class ContractRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, purchase_id: int, contract_number: str, document_url: str | None = None) -> Contract:
        contract = Contract(
            purchase_id=purchase_id,
            contract_number=contract_number,
            document_url=document_url
        )
        self.session.add(contract)
        await self.session.flush()
        return contract

    async def get_by_purchase_id(self, purchase_id: int) -> Contract | None:
        stmt = select(Contract).where(Contract.purchase_id == purchase_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, contract_id: int) -> Contract | None:
        stmt = select(Contract).where(Contract.id == contract_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
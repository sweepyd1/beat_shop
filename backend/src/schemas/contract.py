# schemas/contract.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContractResponse(BaseModel):
    id: int
    purchase_id: int
    contract_number: str
    issued_at: datetime
    document_url: Optional[str] = None

    class Config:
        from_attributes = True
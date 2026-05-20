# api/routes/purchase.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.services.purchase_service import PurchaseService
from core.services.contract_service import ContractService
from core.services.file_service import FileService
from api.dependencies import get_current_user_optional, get_db_session, get_current_user
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
    Если пользователь авторизован, его данные приоритетнее.
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
    except Exception as e:
        # Логируем и возвращаем 500
        print(f"Ошибка при создании покупки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
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
    purchase_repo = PurchaseRepository(session)
    purchase = await purchase_repo.get_by_id(purchase_id)
    if not purchase or purchase.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому договору")

    if not contract.document_url:
        raise HTTPException(status_code=404, detail="Файл договора не найден")

    file_path = os.path.join("uploads", contract.document_url.lstrip("/uploads/"))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл договора отсутствует на сервере")

    return FileResponse(file_path, media_type="application/pdf", filename=f"contract_{contract.contract_number}.pdf")

# Эндпоинт для скачивания договора по ID покупки (используется клиентом)
@router.get("/{purchase_id}/contract")
async def download_contract(
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    file_service: FileService = Depends(lambda: FileService())
):
    return await get_contract_file(purchase_id, current_user, session, file_service)

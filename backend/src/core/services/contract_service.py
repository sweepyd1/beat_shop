import os
import uuid
from datetime import datetime
from fpdf import FPDF
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.contract_repository import ContractRepository
from core.repositories.purchase_repository import PurchaseRepository
from core.repositories.track import TrackRepository
from core.repositories.user import UserRepository
from core.services.file_service import FileService
from database.models import Contract


class PDFContract(FPDF):
    def __init__(self, font_path, bold_font_path):
        super().__init__()
        self.font_path = font_path
        self.bold_font_path = bold_font_path

        # Добавляем обычный шрифт
        if font_path and os.path.exists(font_path):
            self.add_font('DejaVu', '', font_path, uni=True)
        else:
            raise FileNotFoundError(f"Шрифт не найден: {font_path}")

        # Добавляем жирный шрифт, если есть
        if bold_font_path and os.path.exists(bold_font_path):
            self.add_font('DejaVu', 'B', bold_font_path, uni=True)

        # Устанавливаем шрифт по умолчанию
        self.set_font('DejaVu', '', 10)

    def header(self):
        self.set_font('DejaVu', '', 12)
        self.cell(0, 10, 'ДОГОВОР КУПЛИ-ПРОДАЖИ ИСКЛЮЧИТЕЛЬНЫХ ПРАВ', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Страница {self.page_no()}', 0, 0, 'C')


class ContractService:
    def __init__(self, session: AsyncSession, file_service: FileService):
        self.session = session
        self.contract_repo = ContractRepository(session)
        self.purchase_repo = PurchaseRepository(session)
        self.track_repo = TrackRepository(session)
        self.user_repo = UserRepository(session)
        self.file_service = file_service

        # Определяем пути к шрифтам относительно корня проекта
        # Файл находится в core/services/ – поднимаемся на два уровня вверх
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        fonts_dir = os.path.join(base_dir, "fonts")
        self.font_path = os.path.join(fonts_dir, "DejaVuSans.ttf")
        self.bold_font_path = os.path.join(fonts_dir, "DejaVuSans-Bold.ttf")

        # Проверяем наличие основного шрифта
        if not os.path.exists(self.font_path):
            raise FileNotFoundError(
                f"Шрифт не найден: {self.font_path}. "
                "Пожалуйста, поместите файлы DejaVuSans.ttf и DejaVuSans-Bold.ttf в папку fonts/ в корне проекта."
            )
        # Жирный шрифт не обязателен, но желателен
        if not os.path.exists(self.bold_font_path):
            # Можно продолжить, жирный будет отсутствовать, но текст останется читаемым
            pass

    async def generate_contract(self, purchase_id: int) -> str:
        """Генерирует PDF-договор и возвращает путь к файлу."""
        purchase = await self.purchase_repo.get_by_id(purchase_id)
        if not purchase:
            raise ValueError("Покупка не найдена")

        user = await self.user_repo.get(purchase.user_id)
        track = await self.track_repo.get(purchase.track_id)
        if not user or not track:
            raise ValueError("Данные пользователя или трека не найдены")

        # Номер договора
        contract_number = f"BEAT-{purchase.id}-{uuid.uuid4().hex[:8].upper()}"

        # Путь для сохранения
        filename = f"contract_{contract_number}.pdf"
        upload_dir = os.path.join("uploads", "contracts", datetime.now().strftime("%Y/%m"))
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        # Создаём PDF
        pdf = PDFContract(self.font_path, self.bold_font_path)

        # Добавляем страницу
        pdf.add_page()

        # Текст договора
        pdf.cell(0, 10, f"г. Москва                                    {datetime.now().strftime('%d.%m.%Y')}", 0, 1)
        pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, "1. СТОРОНЫ ДОГОВОРА", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, f"Продавец: {track.author.full_name} (Исполнитель)", 0, 1)
        pdf.cell(0, 10, f"Покупатель: {user.full_name}, {user.email}", 0, 1)
        pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, "2. ПРЕДМЕТ ДОГОВОРА", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, "Продавец передает, а Покупатель принимает исключительное право на музыкальное произведение:", 0, 1)
        pdf.cell(0, 10, f"Название: {track.title}", 0, 1)
        pdf.cell(0, 10, f"Автор: {track.author.full_name}", 0, 1)
        pdf.cell(0, 10, f"Стоимость: {track.price} руб.", 0, 1)
        pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, "3. ОСОБЫЕ УСЛОВИЯ", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        
        pdf.cell(0, 10, f"Лицензия:", 0, 1)
        
        pdf.ln(10)

        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, "4. ПОДПИСИ СТОРОН", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 10, "_________________________ /Продавец/", 0, 1)
        pdf.cell(0, 10, "_________________________ /Покупатель/", 0, 1)

        pdf.output(file_path)

        relative_url = f"/uploads/contracts/{datetime.now().strftime('%Y/%m')}/{filename}"
        return relative_url

    async def get_contract_by_purchase_id(self, purchase_id: int) -> Contract | None:
        return await self.contract_repo.get_by_purchase_id(purchase_id)
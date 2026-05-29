import os
import uuid
from datetime import datetime
from fpdf import FPDF
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.contract_repository import ContractRepository
from core.repositories.purchase import PurchaseRepository
from core.repositories.track import TrackRepository
from core.repositories.user import UserRepository
from core.services.file_service import FileService
from database.models import Contract


class PDFContract(FPDF):
    """Улучшенный класс для генерации официального PDF-договора с русскими шрифтами."""

    def __init__(self, font_path, bold_font_path, contract_number):
        super().__init__()
        self.font_path = font_path
        self.bold_font_path = bold_font_path
        self.contract_number = contract_number

        # Добавляем шрифты
        if font_path and os.path.exists(font_path):
            self.add_font('DejaVu', '', font_path, uni=True)
        else:
            raise FileNotFoundError(f"Обычный шрифт не найден: {font_path}")

        if bold_font_path and os.path.exists(bold_font_path):
            self.add_font('DejaVu', 'B', bold_font_path, uni=True)
        else:
            # Если жирного нет – будем использовать обычный
            self.add_font('DejaVu', 'B', font_path, uni=True)

        self.set_font('DejaVu', '', 10)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        """Верхний колонтитул: рамка с названием и номером."""
        self.set_y(10)
        self.set_font('DejaVu', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"ДОГОВОР № {self.contract_number}", 0, 0, 'L')
        self.cell(0, 5, "Экземпляр № 1", 0, 0, 'R')
        self.ln(8)
        # Линия
        self.set_draw_color(180, 180, 180)
        self.line(10, 18, 200, 18)
        self.set_y(22)

    def footer(self):
        """Нижний колонтитул: страница и дата создания."""
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"Страница {self.page_no()}", 0, 0, 'C')
        self.set_y(-10)
        self.cell(0, 5, f"Сформирован автоматически: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 0, 0, 'C')

    def section_title(self, title):
        """Форматированный заголовок раздела."""
        self.set_font('DejaVu', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(240, 240, 245)
        self.cell(0, 8, f"  {title}", 0, 1, 'L', 1)
        self.ln(3)
        self.set_font('DejaVu', '', 10)
        self.set_text_color(0, 0, 0)

    def official_line(self, label, value):
        """Строка вида «Название: значение»."""
        self.set_font('DejaVu', 'B', 10)
        self.cell(50, 6, label, 0, 0, 'L')
        self.set_font('DejaVu', '', 10)
        self.cell(0, 6, value, 0, 1, 'L')

    def paragraph(self, text):
        """Абзац текста с переносом по ширине."""
        self.set_font('DejaVu', '', 10)
        self.multi_cell(0, 5, text, 0, 'J')
        self.ln(2)


class ContractService:
    def __init__(self, session: AsyncSession, file_service: FileService):
        self.session = session
        self.contract_repo = ContractRepository(session)
        self.purchase_repo = PurchaseRepository(session)
        self.track_repo = TrackRepository(session)
        self.user_repo = UserRepository(session)
        self.file_service = file_service

        # Пути к шрифтам
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        fonts_dir = os.path.join(base_dir, "fonts")
        self.font_path = os.path.join(fonts_dir, "DejaVuSans.ttf")
        self.bold_font_path = os.path.join(fonts_dir, "DejaVuSans-Bold.ttf")

        if not os.path.exists(self.font_path):
            raise FileNotFoundError(
                f"Шрифт не найден: {self.font_path}. "
                "Поместите DejaVuSans.ttf в папку fonts/ в корне проекта."
            )

    async def generate_contract(self, purchase_id: int) -> str:
        purchase = await self.purchase_repo.get_by_id(purchase_id)
        if not purchase:
            raise ValueError("Покупка не найдена")

        user = await self.user_repo.get(purchase.user_id)
        track = await self.track_repo.get(purchase.track_id)
        if not user or not track:
            raise ValueError("Данные пользователя или трека не найдены")

        contract_number = f"БИТ-{purchase.id}-{uuid.uuid4().hex[:6].upper()}"
        current_date = datetime.now()

        pdf = PDFContract(self.font_path, self.bold_font_path, contract_number)
        pdf.add_page()

        # Шапка
        pdf.set_font('DejaVu', 'B', 16)
        pdf.cell(0, 12, "ДОГОВОР КУПЛИ-ПРОДАЖИ ИСКЛЮЧИТЕЛЬНЫХ ПРАВ", 0, 1, 'C')
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(0, 6, f"г. Москва                                    {current_date.strftime('%d.%m.%Y')}", 0, 1, 'C')
        pdf.ln(6)

        # Преамбула
        pdf.paragraph(
            "Общество с ограниченной ответственностью «БитМаркет», действующее через платформу beatmarket.ru, в интересах Продавца, "
            "и Покупатель, именуемые в дальнейшем «Стороны», заключили настоящий договор о нижеследующем:"
        )

        # 1. Предмет
        pdf.section_title("1. ПРЕДМЕТ ДОГОВОРА")
        pdf.paragraph(
            "Продавец передает, а Покупатель принимает исключительное право на использование музыкального произведения "
            "(далее – «Произведение») в порядке и на условиях, определенных настоящим договором."
        )
        pdf.official_line("Название:", track.title)
        pdf.official_line("Автор:", track.author.full_name)
        # Жанр: track.genre.name, но нужно быть уверенным, что жанр подгружен
        genre_name = track.genre.name if track.genre else "Не указан"
        pdf.official_line("Жанр:", genre_name)
        pdf.official_line("Длительность:", f"{track.duration_seconds or 0} сек.")
        pdf.ln(2)

        license_types = {
            "standard": "Стандартная неисключительная лицензия",
            "extended": "Расширенная неисключительная лицензия",
            "exclusive": "Эксклюзивная лицензия (полное отчуждение прав)"
        }
        license_str = license_types.get(purchase.license_type.value, purchase.license_type.value)
        pdf.official_line("Тип лицензии:", license_str)

        # 2. Цена
        pdf.section_title("2. ЦЕНА И ПОРЯДОК РАСЧЕТОВ")
        amount_text = self._amount_to_text(purchase.amount)
        pdf.paragraph(
            f"Цена передаваемого исключительного права составляет {purchase.amount} "
            f"({amount_text}) рублей 00 копеек, включая все налоги и сборы."
        )
        pdf.paragraph(
            "Расчет произведен Покупателем полностью в момент оформления заказа на платформе BeatMarket. "
            "Обязательства Покупателя по оплате считаются исполненными с момента зачисления денежных средств на расчетный счет Продавца."
        )
        pdf.official_line("Дата платежа:", purchase.purchase_date.strftime('%d.%m.%Y'))

        # 3. Передача прав
        pdf.section_title("3. ПЕРЕДАЧА ИСКЛЮЧИТЕЛЬНЫХ ПРАВ")
        pdf.paragraph(
            "Права считаются переданными с момента подписания Сторонами акта приема-передачи, который одновременно "
            "является неотъемлемой частью настоящего договора. Продавец предоставляет Покупателю доступ к высококачественной "
            "записи Произведения (WAV/MP3) и, при необходимости, к разделенным дорожкам (stems)."
        )
        pdf.paragraph(
            "Покупатель вправе использовать Произведение следующими способами (в рамках приобретенной лицензии): "
            "запись, воспроизведение, публичное исполнение, сообщение в эфир и по кабелю, переработка (создание ремиксов), "
            "а также использование в аудиовизуальных произведениях (YouTube, TikTok, Instagram Reels и др.)."
        )

        # 4. Ответственность
        pdf.section_title("4. ОТВЕТСТВЕННОСТЬ СТОРОН")
        pdf.paragraph(
            "Продавец гарантирует, что является законным правообладателем Произведения и что Произведение не нарушает "
            "интеллектуальных прав третьих лиц. В случае предъявления претензий со стороны третьих лиц Продавец обязуется "
            "урегулировать их самостоятельно и возместить Покупателю все понесенные убытки."
        )
        pdf.paragraph(
            "Покупатель несет ответственность за соблюдение территориальных и временных ограничений, указанных в лицензии. "
            "Любое использование Произведения за рамками предоставленных прав влечет ответственность в соответствии с "
            "действующим законодательством РФ."
        )

        # 5. Срок действия
        pdf.section_title("5. СРОК ДЕЙСТВИЯ И РАСТОРЖЕНИЕ")
        if purchase.license_type.value == "exclusive":
            pdf.paragraph(
                "Договор вступает в силу с даты его подписания Сторонами и действует бессрочно (полное отчуждение прав). "
                "Продавец не вправе в дальнейшем передавать или использовать Произведение каким-либо образом."
            )
        else:
            pdf.paragraph(
                "Договор вступает в силу с момента оплаты и действует бессрочно на территории всего мира. Продавец сохраняет "
                "право многократной продажи неисключительных лицензий на данное Произведение другим лицам."
            )

        # 6. Реквизиты и подписи
        pdf.section_title("6. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН")
        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 7, "ПРОДАВЕЦ:", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.official_line("Полное имя:", track.author.full_name)
        # ✅ Исправлено: email у пользователя
        pdf.official_line("Email:", track.author.user.email)
        # ✅ Исправлено: login вместо username
        login = track.author.user.login
        pdf.official_line("Аккаунт на BeatMarket:", f"beatmarket.ru/@{login}")
        pdf.ln(4)

        pdf.set_font('DejaVu', 'B', 10)
        pdf.cell(0, 7, "ПОКУПАТЕЛЬ:", 0, 1)
        pdf.set_font('DejaVu', '', 10)
        pdf.official_line("Полное имя:", user.full_name)
        pdf.official_line("Email:", user.email)
        pdf.ln(6)

        # Подписи
        pdf.set_font('DejaVu', '', 10)
        pdf.cell(80, 10, "Подпись Продавца: ____________________", 0, 0, 'L')
        pdf.cell(80, 10, "Подпись Покупателя: ____________________", 0, 1, 'L')
        pdf.cell(80, 10, "Расшифровка: _________________________", 0, 0, 'L')
        pdf.cell(80, 10, "Расшифровка: _________________________", 0, 1, 'L')
        pdf.ln(5)
        pdf.cell(0, 6, "Место для печати (при наличии)", 0, 1, 'C')

        # Сохранение
        upload_dir = os.path.join("uploads", "contracts", datetime.now().strftime("%Y/%m"))
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"contract_{contract_number}.pdf"
        file_path = os.path.join(upload_dir, filename)
        pdf.output(file_path)

        relative_url = f"/uploads/contracts/{datetime.now().strftime('%Y/%m')}/{filename}"
        return relative_url

    async def get_contract_by_purchase_id(self, purchase_id: int) -> Contract | None:
        return await self.contract_repo.get_by_purchase_id(purchase_id)

    @staticmethod
    def _amount_to_text(amount) -> str:
        """Преобразует сумму в рубли прописью (без копеек), поддерживает до 999 млн."""
        try:
            rub = int(amount)
        except (TypeError, ValueError):
            rub = 0

        if rub == 0:
            return "ноль рублей"

        # Словари для чисел
        units = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
        units_female = ["", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
        teens = ["десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
                "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
        tens = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят",
                "семьдесят", "восемьдесят", "девяносто"]
        hundreds = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот",
                    "семьсот", "восемьсот", "девятьсот"]

        def convert_three(n: int, female: bool = False) -> str:
            """Преобразует число от 1 до 999 в пропись, с учётом рода (для тысяч)."""
            if n == 0:
                return ""
            result = []
            if n >= 100:
                result.append(hundreds[n // 100])
                n %= 100
            if n >= 20:
                result.append(tens[n // 10])
                n %= 10
            elif 10 <= n < 20:
                result.append(teens[n - 10])
                n = 0
            if n > 0:
                result.append(units_female[n] if female else units[n])
            return " ".join(result)

        # Разбиваем на классы: миллионы, тысячи, единицы
        millions = rub // 1_000_000
        rub %= 1_000_000
        thousands = rub // 1_000
        rub %= 1_000

        parts = []

        # Миллионы
        if millions > 0:
            parts.append(convert_three(millions, female=False))
            if millions % 10 == 1 and millions % 100 != 11:
                parts.append("миллион")
            elif 2 <= millions % 10 <= 4 and (millions % 100 < 10 or millions % 100 >= 20):
                parts.append("миллиона")
            else:
                parts.append("миллионов")

        # Тысячи
        if thousands > 0:
            parts.append(convert_three(thousands, female=True))
            if thousands % 10 == 1 and thousands % 100 != 11:
                parts.append("тысяча")
            elif 2 <= thousands % 10 <= 4 and (thousands % 100 < 10 or thousands % 100 >= 20):
                parts.append("тысячи")
            else:
                parts.append("тысяч")

        # Единицы (рубли)
        if rub > 0:
            parts.append(convert_three(rub, female=False))
            if rub % 10 == 1 and rub % 100 != 11:
                parts.append("рубль")
            elif 2 <= rub % 10 <= 4 and (rub % 100 < 10 or rub % 100 >= 20):
                parts.append("рубля")
            else:
                parts.append("рублей")
        else:
            # Если сумма заканчивается на тысячи или миллионы, добавляем "рублей"
            parts.append("рублей")

        result = " ".join(parts)
        return result.capitalize()
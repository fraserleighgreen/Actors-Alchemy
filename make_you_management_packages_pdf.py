from pathlib import Path
from io import BytesIO
from math import sqrt

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "Actors Alchemy - YOU Management Development Packages.pdf"
LOGO = ROOT / "assets" / "actors-alchemy-logo-wordmark.png"
YOU_LOGO = ROOT / "assets" / "you-management-logo.png"

PARCHMENT = HexColor("#f8f3eb")
CARD = HexColor("#f4ecdf")
OAT = HexColor("#e8ddce")
OAT_DEEP = HexColor("#d4c4af")
CHARCOAL = HexColor("#3c3832")
MUTED = HexColor("#75675b")
RUST = HexColor("#9d693d")
RUST_DEEP = HexColor("#7e4d2c")
COPPER = HexColor("#a85f39")
SILVER = HexColor("#88847e")
GOLD = HexColor("#b18432")
YOU_RED = HexColor("#ed0000")

PACKAGES = [
    {"sessions": "03", "title": "Three Sessions", "purpose": ["GET STARTED, BUILD ON YOUR GOALS."], "price": "£135", "saving": "Save £15", "number": COPPER},
    {"sessions": "06", "title": "Six Sessions", "purpose": ["SET GOALS. ACHIEVE. REPEAT."], "price": "£255", "saving": "Save £45", "number": RUST},
    {"sessions": "10", "title": "Ten Sessions", "purpose": ["MAINTAIN MOMENTUM. CONTINUE GROWING."], "price": "£425", "saving": "Save £75", "number": GOLD},
]


def draw_tracking_text(c, text, x, y, font, size, colour, tracking, centered=False):
    c.setFont(font, size)
    c.setFillColor(colour)
    widths = [c.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    cursor = x - total / 2 if centered else x
    for ch, width in zip(text, widths):
        c.drawString(cursor, y, ch)
        cursor += width + tracking


def trimmed_logo(path):
    image = Image.open(path).convert("RGBA")
    alpha_bounds = image.getchannel("A").getbbox()
    if alpha_bounds:
        image = image.crop(alpha_bounds)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer), image.width / image.height


def draw_card(c, x, y, width, height, package):
    c.saveState()
    c.setFillAlpha(0.42)
    c.setFillColor(OAT_DEEP)
    c.roundRect(x + 1.25, y - 1.25, width, height, 2, fill=1, stroke=0)
    c.restoreState()

    c.setFillColor(CARD)
    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(1.15)
    c.roundRect(x, y, width, height, 2, fill=1, stroke=1)

    c.setStrokeColor(YOU_RED if package["sessions"] == "06" else package["number"])
    c.setLineWidth(3.2)
    c.line(x + 1.8, y + height - 1.8, x + width - 1.8, y + height - 1.8)

    content_center = x + width / 2
    is_exclusive = package["sessions"] == "06"
    right_column_center = x + width - 78

    if is_exclusive:
        exclusive_x = x + 22
        exclusive_y = y + height - 40
        exclusive_width = 190
        c.setFillColor(OAT)
        c.roundRect(exclusive_x, exclusive_y, exclusive_width, 22, 2, fill=1, stroke=0)
        c.setFillColor(YOU_RED)
        c.setFont("Helvetica-Bold", 8.3)
        c.drawCentredString(exclusive_x + exclusive_width / 2, y + height - 30.5, "EXCLUSIVE TO YOU MANAGEMENT CLIENTS")

    c.setFillColor(YOU_RED if is_exclusive else package["number"])
    c.setFont("Times-Roman", 22)
    c.drawRightString(x + width - 22, y + height - 34, package["sessions"])

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 28)
    c.drawString(x + 28, y + 72, package["title"])

    purpose_lines = package["purpose"]
    purpose_size = 9.8 if len(purpose_lines) > 1 else 10.5
    first_purpose_y = y + 36 if len(purpose_lines) == 1 else y + 41
    c.setFillColor(RUST_DEEP)
    c.setFont("Helvetica-Bold", purpose_size)
    for index, line in enumerate(purpose_lines):
        c.drawString(x + 28, first_purpose_y - index * 13, line)

    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(0.8)
    c.line(x + width - 156, y + 20, x + width - 156, y + height - 20)

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 32)
    c.drawCentredString(right_column_center, y + 70, package["price"])

    badge_width = 92
    badge_height = 26
    badge_x = right_column_center - badge_width / 2
    badge_y = y + 20
    c.setFillColor(OAT)
    c.roundRect(badge_x, badge_y, badge_width, badge_height, 2, fill=1, stroke=0)
    c.setFillColor(RUST_DEEP)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawCentredString(right_column_center, badge_y + 8, package["saving"])


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Actors Alchemy - YOU Management Development Packages")
    c.setAuthor("Actors Alchemy")

    c.setFillColor(PARCHMENT)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Subtle brand texture without using a flat white background.
    c.saveState()
    c.setFillAlpha(0.11)
    c.setFillColor(OAT_DEEP)
    for row in range(26):
        for col in range(19):
            if (row * 7 + col * 11) % 13 == 0:
                c.circle(25 + col * 31, 22 + row * 32, 0.55, fill=1, stroke=0)
    c.restoreState()

    logo, logo_ratio = trimmed_logo(LOGO)
    you_logo, you_logo_ratio = trimmed_logo(YOU_LOGO)
    logo_height = 32
    you_logo_height = logo_height * sqrt(logo_ratio / you_logo_ratio) * 0.55
    logo_width = logo_height * logo_ratio
    you_logo_width = you_logo_height * you_logo_ratio
    lockup_center_y = page_h - 55
    c.setFillColor(RUST)
    c.setFont("Times-Roman", 22)
    cross_center_x = page_w / 2
    lockup_clear_space = 35
    logo_x = cross_center_x - lockup_clear_space - logo_width
    title_text = "Development Packages"
    title_start_x = (page_w - c.stringWidth(title_text, "Times-Roman", 36)) / 2
    k_index = title_text.index("k")
    packages_k_center_x = title_start_x + c.stringWidth(title_text[:k_index], "Times-Roman", 36) + c.stringWidth("k", "Times-Roman", 36) / 2
    you_x = packages_k_center_x - you_logo_width / 2
    c.drawImage(logo, logo_x, lockup_center_y - logo_height / 2, width=logo_width, height=logo_height, mask="auto")
    c.drawCentredString(cross_center_x, lockup_center_y - 7, "×")
    c.drawImage(you_logo, you_x, lockup_center_y - you_logo_height / 2, width=you_logo_width, height=you_logo_height, mask="auto")

    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(0.7)
    c.line(108, page_h - 98, page_w - 108, page_h - 98)
    c.setFillColor(RUST)
    c.circle(page_w / 2, page_h - 98, 2.1, fill=1, stroke=0)

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 36)
    c.drawCentredString(page_w / 2, page_h - 143, title_text)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 12.5)
    c.drawCentredString(page_w / 2, page_h - 166, "Personalised coaching shaped around your goals")
    c.setFont("Helvetica", 9)
    c.drawCentredString(page_w / 2, page_h - 182, "Savings shown against our standard £50 one-to-one session rate.")

    margin_x = 48
    card_w = page_w - 2 * margin_x
    card_h = 135
    gap_y = 14
    top_card_y = 500

    positions = [
        (margin_x, top_card_y),
        (margin_x, top_card_y - card_h - gap_y),
        (margin_x, top_card_y - 2 * (card_h + gap_y)),
    ]
    for package, (x, y) in zip(PACKAGES, positions):
        draw_card(c, x, y, card_w, card_h, package)

    note_x = 68
    note_y = 54
    note_width = page_w - 2 * note_x
    note_height = 132
    c.setFillColor(OAT)
    c.roundRect(note_x, note_y, note_width, note_height, 3, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(page_w / 2, 154, "Every session is personalised for the performer and shaped around their goals.")
    c.drawCentredString(page_w / 2, 133, "Each package is structured around the work we aim to achieve together,")
    c.drawCentredString(page_w / 2, 112, "at an exclusive and accessible rate for YOU Management clients.")
    c.setFillColor(RUST_DEEP)
    c.setFont("Helvetica-Bold", 10.2)
    c.drawCentredString(page_w / 2, 84, "TO CHOOSE YOUR PACKAGE OR ASK ANY QUESTIONS, PLEASE EMAIL")
    c.setFont("Helvetica-Bold", 13.5)
    c.drawCentredString(page_w / 2, 65, "fraser@actorsalchemy.co.uk")

    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(0.7)
    c.line(48, 45, page_w - 48, 45)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(page_w / 2, 29, "Actors Alchemy · Development coaching rates")

    c.showPage()
    c.save()


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)

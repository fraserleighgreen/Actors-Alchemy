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

PARCHMENT = HexColor("#efe6d7")
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

PACKAGES = [
    {"sessions": "03", "title": "Three Sessions", "price": "£130", "saving": "Save £20", "number": COPPER},
    {"sessions": "05", "title": "Five Sessions", "price": "£215", "saving": "Save £35", "number": SILVER},
    {"sessions": "06", "title": "Six Sessions", "price": "£255", "saving": "Save £45", "number": RUST},
    {"sessions": "10", "title": "Ten Sessions", "price": "£425", "saving": "Save £75", "number": GOLD},
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

    c.setStrokeColor(package["number"])
    c.setLineWidth(3.2)
    c.line(x + 1.8, y + height - 1.8, x + width - 1.8, y + height - 1.8)

    c.setFillColor(package["number"])
    c.setFont("Times-Roman", 24)
    c.drawRightString(x + width - 25, y + height - 39, package["sessions"])

    content_center = x + width / 2
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 29)
    c.drawCentredString(content_center, y + height - 78, package["title"])

    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(0.8)
    c.line(x + 30, y + height - 98, x + width - 30, y + height - 98)

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 36)
    c.drawCentredString(content_center, y + height - 137, package["price"])

    badge_width = 92
    badge_height = 28
    badge_x = content_center - badge_width / 2
    badge_y = y + 26
    c.setFillColor(OAT)
    c.roundRect(badge_x, badge_y, badge_width, badge_height, 2, fill=1, stroke=0)
    c.setFillColor(RUST_DEEP)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(content_center, badge_y + 9, package["saving"])


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
    you_logo_height = logo_height * sqrt(logo_ratio / you_logo_ratio)
    logo_width = logo_height * logo_ratio
    you_logo_width = you_logo_height * you_logo_ratio
    lockup_center_y = page_h - 68
    c.setFillColor(RUST)
    c.setFont("Times-Roman", 22)
    cross_width = c.stringWidth("×", "Times-Roman", 22)
    lockup_gap = 18
    group_width = logo_width + lockup_gap + cross_width + lockup_gap + you_logo_width
    group_x = (page_w - group_width) / 2
    c.drawImage(logo, group_x, lockup_center_y - logo_height / 2, width=logo_width, height=logo_height, mask="auto")
    cross_x = group_x + logo_width + lockup_gap
    c.drawString(cross_x, lockup_center_y - 7, "×")
    you_x = cross_x + cross_width + lockup_gap
    c.drawImage(you_logo, you_x, lockup_center_y - you_logo_height / 2, width=you_logo_width, height=you_logo_height, mask="auto")

    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(0.7)
    c.line(108, page_h - 112, page_w - 108, page_h - 112)
    c.setFillColor(RUST)
    c.circle(page_w / 2, page_h - 112, 2.1, fill=1, stroke=0)

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 36)
    c.drawCentredString(page_w / 2, page_h - 158, "Development Packages")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(page_w / 2, page_h - 181, "Personalised coaching shaped around your goals")

    margin_x = 48
    gap_x = 20
    gap_y = 22
    card_w = (page_w - 2 * margin_x - gap_x) / 2
    card_h = 220
    top_y = page_h - 441
    bottom_y = top_y - card_h - gap_y

    positions = [
        (margin_x, top_y),
        (margin_x + card_w + gap_x, top_y),
        (margin_x, bottom_y),
        (margin_x + card_w + gap_x, bottom_y),
    ]
    for package, (x, y) in zip(PACKAGES, positions):
        draw_card(c, x, y, card_w, card_h, package)

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

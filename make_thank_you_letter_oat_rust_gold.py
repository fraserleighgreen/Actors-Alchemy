from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = Path(
    "/Users/fraserleighgreen/Documents/Codex/2026-05-17/lets-work-on-the-actors-alchemy"
)
OUT = ROOT / "output" / "pdf" / "Actors Alchemy Thank You Letter - Oat Rust Gold.pdf"
WORDMARK = ROOT / "assets" / "actors-alchemy-logo-wordmark.png"
SIGNATURE = ROOT / "assets" / "fraser-signature-white.png"
WATERMARK = SOURCE_ROOT / "actors-alchemy-graphite-watermark.png"

PAGE_W, PAGE_H = A4
PARCHMENT = colors.HexColor("#efe6d7")
CARD = colors.HexColor("#f4ecdf")
OAT = colors.HexColor("#e8ddce")
OAT_DEEP = colors.HexColor("#d4c4af")
CHARCOAL = colors.HexColor("#3c3832")
MUTED = colors.HexColor("#75675b")
RUST = colors.HexColor("#9d693d")
RUST_DEEP = colors.HexColor("#7e4d2c")
GOLD = colors.HexColor("#b18432")
RED = colors.HexColor("#ed0000")


def paragraph(c, html, x, y_top, width, size=17, leading=22.5, colour=CHARCOAL, align=TA_LEFT):
    style = ParagraphStyle(
        "letter",
        fontName="Times-Roman",
        fontSize=size,
        leading=leading,
        textColor=colour,
        alignment=align,
        spaceAfter=0,
    )
    p = Paragraph(html, style)
    _, height = p.wrap(width, PAGE_H)
    p.drawOn(c, x, y_top - height)
    return y_top - height


def centered_mixed(c, parts, y, size=12.8, font="Times-Italic"):
    widths = [stringWidth(value, font, size) for value, _ in parts]
    x = (PAGE_W - sum(widths)) / 2
    c.setFont(font, size)
    for (value, colour), width in zip(parts, widths):
        c.setFillColor(colour)
        c.drawString(x, y, value)
        x += width


def cropped_image(path):
    image = Image.open(path).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    if bounds:
        image = image.crop(bounds)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer), image.width / image.height


def tinted_image(path, rgb, opacity=1.0):
    image = Image.open(path).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    if bounds:
        image = image.crop(bounds)
    alpha = image.getchannel("A").point(lambda value: int(value * opacity))
    tint = Image.new("RGBA", image.size, (*rgb, 255))
    tint.putalpha(alpha)
    buffer = BytesIO()
    tint.save(buffer, format="PNG")
    buffer.seek(0)
    return ImageReader(buffer)


def draw_background(c):
    c.setFillColor(PARCHMENT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.saveState()
    c.setFillColor(CARD)
    c.setStrokeColor(OAT_DEEP)
    c.setLineWidth(1)
    c.roundRect(32, 22, PAGE_W - 64, PAGE_H - 52, 10, stroke=1, fill=1)
    c.setStrokeColor(RUST)
    c.setLineWidth(2.4)
    c.line(43, PAGE_H - 31, PAGE_W - 43, PAGE_H - 31)
    c.restoreState()

    watermark = tinted_image(WATERMARK, (126, 77, 44), 0.09)
    c.drawImage(watermark, PAGE_W - 188, 44, width=124, height=149, mask="auto")


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("A Thank You from Actors Alchemy - Oat Rust Gold")
    c.setAuthor("Fraser Leigh Green | Actors Alchemy")

    draw_background(c)

    logo, logo_ratio = cropped_image(WORDMARK)
    logo_height = 25
    logo_width = logo_height * logo_ratio
    c.drawImage(logo, 55, PAGE_H - 72, width=logo_width, height=logo_height, mask="auto")

    c.setFillColor(RUST_DEEP)
    c.setFont("Times-Roman", 8.8)
    c.drawString(83, PAGE_H - 82, "Find gold in your performance")

    c.setFillColor(CHARCOAL)
    c.setFont("Times-Italic", 26)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 116, "With appreciation")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(PAGE_W / 2 - 62, PAGE_H - 136, PAGE_W / 2 + 62, PAGE_H - 136)
    c.setFillColor(RED)
    c.circle(PAGE_W / 2, PAGE_H - 136, 1.6, fill=1, stroke=0)

    x = 54
    width = PAGE_W - 108
    y = 689
    y = paragraph(c, "<i>To our performers,</i>", x, y, width, 19, 23, RUST_DEEP, TA_CENTER)
    y -= 11
    y = paragraph(
        c,
        "Your time, hard work, openness and curiosity made these sessions what they were. It was a privilege to work with each of you and to see you trust the process and, most importantly, yourselves.",
        x,
        y,
        width,
        17,
        22.5,
        CHARCOAL,
        TA_CENTER,
    )
    y -= 10
    y = paragraph(
        c,
        "Madison, Katie/Natasha, Terence, Cameron and Caitlyn are deeply invested in your progress. Our work together has added another layer of focused, practical support, helping you build upon the encouragement already surrounding you.",
        x,
        y,
        width,
        17,
        22.5,
        CHARCOAL,
        TA_CENTER,
    )
    y -= 14

    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(PAGE_W / 2 - 36, y, PAGE_W / 2 + 36, y)
    c.setFillColor(RED)
    c.circle(PAGE_W / 2, y, 1.3, fill=1, stroke=0)
    y -= 19
    y = paragraph(
        c,
        "<font color='#7e4d2c'>WHAT COMES NEXT?</font>",
        x,
        y,
        width,
        13.5,
        17,
        RUST_DEEP,
        TA_CENTER,
    )
    y -= 8
    y = paragraph(
        c,
        "The response to these sessions has been overwhelmingly positive, with many of you asking what might come next. Together, the team and I are now developing ideas for packages and future workshops that build upon the work and reflect the support you have told us matters most.<br/><br/>As these ideas take shape, we welcome your thoughts. Please share any further suggestions with your agent so we can create support that remains useful, accessible and genuinely responsive to what you need.",
        x,
        y,
        width,
        15.8,
        20.8,
        CHARCOAL,
        TA_CENTER,
    )
    y -= 10
    c.setStrokeColor(GOLD)
    c.line(PAGE_W / 2 - 36, y, PAGE_W / 2 + 36, y)
    y -= 20
    closing_y = paragraph(
        c,
        "Good luck with the challenges we set together. I'll be cheering you on,<br/>and holding you accountable from afar!",
        x,
        y,
        width,
        16,
        21,
        RUST_DEEP,
        TA_CENTER,
    )
    closing_y -= 10
    paragraph(
        c,
        "Stay curious, and keep showing up for yourselves.",
        x,
        closing_y,
        width,
        16,
        21,
        RUST_DEEP,
        TA_CENTER,
    )

    signature = tinted_image(SIGNATURE, (126, 77, 44), 0.95)
    c.drawImage(
        signature,
        (PAGE_W - 76) / 2,
        78,
        width=76,
        height=59.3,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )
    c.setFillColor(RUST_DEEP)
    c.setFont("Times-Italic", 15.5)
    c.drawCentredString(PAGE_W / 2, 61, "Fraser Leigh Green")
    c.setFillColor(MUTED)
    c.setFont("Times-Roman", 11.2)
    c.drawCentredString(PAGE_W / 2, 43, "Director | Actors Alchemy")

    centered_mixed(
        c,
        [("actorsalchemy.co.uk", RUST), ("   |   ", GOLD), ("fraser@actorsalchemy.co.uk", CHARCOAL)],
        27,
    )

    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = Path(
    "/Users/fraserleighgreen/Documents/Codex/2026-05-17/lets-work-on-the-actors-alchemy"
)
OUT = ROOT / "output" / "pdf" / "Actors Alchemy Thank You Letter - Larger Text.pdf"
WORDMARK = ROOT / "assets" / "actors-alchemy-wordmark-gold-transparent.png"
SIGNATURE = ROOT / "assets" / "fraser-signature-white.png"
WATERMARK = SOURCE_ROOT / "actors-alchemy-graphite-watermark.png"

PAGE_W, PAGE_H = A4
GRAPHITE = colors.HexColor("#28241f")
OAT = colors.HexColor("#e8ddce")
WARM_WHITE = colors.HexColor("#f8f3eb")
GOLD = colors.HexColor("#d6b16a")
TAUPE = colors.HexColor("#cec2b2")


def draw_background(c):
    c.setFillColor(GRAPHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.saveState()
    c.setStrokeColor(colors.Color(0.84, 0.69, 0.42, alpha=0.26))
    c.setLineWidth(0.8)
    c.roundRect(32, 22, PAGE_W - 64, PAGE_H - 52, 10, stroke=1, fill=0)
    c.setStrokeColor(colors.Color(0.91, 0.86, 0.78, alpha=0.10))
    c.circle(PAGE_W - 116, 120, 66, stroke=1, fill=0)
    c.circle(PAGE_W - 132, 132, 92, stroke=1, fill=0)
    c.restoreState()

    c.drawImage(
        ImageReader(str(WATERMARK)),
        PAGE_W - 188,
        44,
        width=124,
        height=149,
        mask="auto",
    )


def paragraph(c, html, x, y_top, width, size=13.9, leading=19.2, colour=OAT, align=TA_LEFT):
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


def centered_mixed(c, parts, y, size=11.5, font="Times-Italic"):
    widths = [stringWidth(value, font, size) for value, _ in parts]
    x = (PAGE_W - sum(widths)) / 2
    c.setFont(font, size)
    for (value, colour), width in zip(parts, widths):
        c.setFillColor(colour)
        c.drawString(x, y, value)
        x += width


def cropped_website_wordmark():
    image = Image.open(WORDMARK).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    return ImageReader(image.crop(bounds))


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("A Thank You from Actors Alchemy")
    c.setAuthor("Fraser Leigh Green | Actors Alchemy")

    draw_background(c)
    c.drawImage(
        cropped_website_wordmark(),
        60,
        PAGE_H - 60,
        width=124,
        height=22,
        mask="auto",
    )

    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 8.4)
    c.drawString(84.5, PAGE_H - 72, "Find gold in your performance")

    c.setFillColor(WARM_WHITE)
    c.setFont("Times-Italic", 24)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 140, "With appreciation")
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(PAGE_W / 2 - 62, PAGE_H - 158, PAGE_W / 2 + 62, PAGE_H - 158)

    x = 84
    width = PAGE_W - 168
    y = 638
    y = paragraph(c, "<i>To our performers,</i>", x, y, width, 16, 20, GOLD, TA_CENTER)
    y -= 24
    y = paragraph(
        c,
        "Your time, hard work, openness and curiosity made these sessions what they were. It was a privilege to work with each of you and to see you trust the process and, most importantly, yourselves.",
        x,
        y,
        width,
        13.9,
        20.5,
        OAT,
        TA_CENTER,
    )
    y -= 19
    y = paragraph(
        c,
        "Madison, Katie/Natasha, Terence, Cameron and Caitlyn are deeply invested in your progress. Our work together has added another layer of focused, practical support, helping you build upon the encouragement already surrounding you.",
        x,
        y,
        width,
        13.9,
        20.5,
        OAT,
        TA_CENTER,
    )
    y -= 27

    c.setStrokeColor(colors.Color(0.84, 0.69, 0.42, alpha=0.50))
    c.setLineWidth(0.6)
    c.line(PAGE_W / 2 - 36, y, PAGE_W / 2 + 36, y)
    y -= 31
    y = paragraph(
        c,
        "<font color='#d6b16a'>WHAT COMES NEXT?</font>",
        x,
        y,
        width,
        11.8,
        15,
        GOLD,
        TA_CENTER,
    )
    y -= 19
    y = paragraph(
        c,
        "The response to these sessions has been overwhelmingly positive, with many of you asking what might come next. Terence and I are now developing ideas for packages and future workshops that build upon the work and reflect the support you have told us matters most.<br/><br/>As these ideas take shape, we welcome your thoughts. Please share any further suggestions with your agent so we can create support that remains useful, accessible and genuinely responsive to what you need.",
        x,
        y,
        width,
        13.1,
        18.2,
        OAT,
        TA_CENTER,
    )
    y -= 24
    c.setStrokeColor(colors.Color(0.84, 0.69, 0.42, alpha=0.50))
    c.line(PAGE_W / 2 - 36, y, PAGE_W / 2 + 36, y)
    y -= 5
    paragraph(
        c,
        "Good luck with the challenges we set together. I'll be cheering you on,<br/>and holding you accountable from afar!",
        x,
        y,
        width,
        13.4,
        18,
        OAT,
        TA_CENTER,
    )

    c.drawImage(
        ImageReader(str(SIGNATURE)),
        (PAGE_W - 60) / 2,
        84,
        width=60,
        height=46.8,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 13)
    c.drawCentredString(PAGE_W / 2, 64, "Fraser Leigh Green")
    c.setFillColor(TAUPE)
    c.setFont("Times-Roman", 9.5)
    c.drawCentredString(PAGE_W / 2, 47, "Director | Actors Alchemy")

    centered_mixed(
        c,
        [("actorsalchemy.co.uk", GOLD), ("   |   ", TAUPE), ("fraser@actorsalchemy.co.uk", OAT)],
        31,
    )

    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()

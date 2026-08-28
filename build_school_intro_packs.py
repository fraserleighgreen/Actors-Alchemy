from io import BytesIO
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFilter
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
SOURCE = Path("/Users/fraserleighgreen/Downloads/Actors Alchemy GSA Intro Pack.pdf")
LOGOS = ROOT / "tmp/pdfs/school-logos"
PROCESSED_LOGOS = ROOT / "tmp/pdfs/processed-logos"
OUT = ROOT / "output/pdf"

GOLD = HexColor("#B99455")
PAPER = HexColor("#F4EFE6")
DARK = HexColor("#24211D")
SOURCE_DARK = HexColor("#28241F")
PANEL = HexColor("#3B3832")
BORDER = HexColor("#4C4132")
MUTED = HexColor("#D5CBBE")
TOTAL_PAGES = 4

EXISTING_SCHOOLS = [
    ("Guildford School of Acting", "Kevin Cripps and GSA", "gsa.png"),
    ("ArtsEd", "the ArtsEd Musical Theatre team", "artsed.png"),
    ("Mountview", "the Mountview performance team", "mountview-official.png"),
    ("Trinity Laban", "Aaron Francis and Trinity Laban", "trinity-laban.png"),
    ("London Studio Centre", "Nikki Laurence and London Studio Centre", "london-studio-centre.jpg"),
    ("Italia Conti", "the Italia Conti Musical Theatre team", "italia-conti.png"),
    ("Performance Preparation Academy", "the PPA course team", None),
    ("Bird College", "the Bird College course team", "bird-official-white.png"),
    ("Performers College Essex", "Kieran Jae and Performers College Essex", "performers-college.png"),
    ("Emil Dale Academy", "the Emil Dale Academy team", "emil-dale-official.svg.png"),
    ("Laine Theatre Arts", "the Laine Theatre Arts team", "laine-theatre-arts.png"),
]

PROSPECT_SCHOOLS = [
    ("Goldsmiths, University of London", "Bradley Rogers and Goldsmiths", "goldsmiths.png"),
    ("University of West London - London College of Music", "the London College of Music Musical Theatre team", "uwl.png"),
    ("Buckinghamshire New University", "Jo Roots and BNU", "bnu.png"),
    ("University of Winchester", "Dr Adam Rush and Winchester", "winchester.png"),
    ("University of Chichester Conservatoire", "Andrew Wright and Chichester", "chichester.png"),
    ("Millennium Performing Arts", "Nigel West and Millennium Performing Arts", "mpa.png"),
    ("Anglia Ruskin University", "Pippa Duffy and ARU", "aru.png"),
    ("Urdang at City St George's", "Neil Kagan and Urdang", "urdang.png"),
    ("Associated Studios", "Leontine Hass and Associated Studios", "associated-studios.png"),
    ("LAMDA", "Gregory Haney and LAMDA", "lamda.png"),
    ("Royal Academy of Music", "Dan Bowling and the Royal Academy of Music", "royal-academy-music.png"),
]

# Generate only the new prospect packs. The existing approved PDFs remain untouched.
SCHOOLS = PROSPECT_SCHOOLS


def slugify(text):
    clean = re.sub(r"[^a-z0-9]+", "-", text.lower().replace("&", "and"))
    return clean.strip("-")


def fit_image(c, path, box, dark_background=True):
    x, y, w, h = box
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    px, py = x + (w - dw) / 2, y + (h - dh) / 2
    if dark_background:
        c.setFillColor(PAPER)
        c.roundRect(x, y, w, h, 3, stroke=0, fill=1)
    c.drawImage(ImageReader(str(path)), px, py, dw, dh, preserveAspectRatio=True, mask="auto")


def draw_circular_image(c, path, cx, cy, radius, offset_y=0):
    with Image.open(path) as image:
        width, height = image.size
    diameter = radius * 2
    scale = max(diameter / width, diameter / height)
    draw_width, draw_height = width * scale, height * scale
    c.saveState()
    clip = c.beginPath()
    clip.circle(cx, cy, radius)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(
        ImageReader(str(path)),
        cx - draw_width / 2,
        cy - draw_height / 2 + offset_y,
        draw_width,
        draw_height,
        preserveAspectRatio=True,
        mask="auto",
    )
    c.restoreState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.circle(cx, cy, radius, stroke=1, fill=0)


def processed_logo_path(logo_name):
    if not logo_name:
        return None
    return PROCESSED_LOGOS / f"{Path(logo_name).stem}.png"


def draw_vector_logo(c, path, box):
    """Draw outlined official artwork directly, preserving every letter counter."""
    data = json.loads(path.read_text())
    x0, top0, x1, bottom1 = data["bounds"]
    source_width = x1 - x0
    source_height = bottom1 - top0
    x, y, width, height = box
    scale = min(width / source_width, height / source_height)
    draw_width = source_width * scale
    draw_height = source_height * scale
    draw_x = x + (width - draw_width) / 2
    draw_y = y + (height - draw_height) / 2

    c.saveState()
    c.translate(draw_x, draw_y + draw_height)
    c.scale(scale, -scale)
    c.translate(-x0, -top0)
    for item in data["objects"]:
        vector_path = c.beginPath()
        for operation in item["path"]:
            command = operation[0]
            points = operation[1:]
            if command == "m":
                vector_path.moveTo(*points[0])
            elif command == "l":
                vector_path.lineTo(*points[0])
            elif command == "c":
                vector_path.curveTo(*(points[0] + points[1] + points[2]))
            elif command == "h":
                vector_path.close()
        fill = item["fill"]
        if len(fill) == 4:
            c.setFillColorCMYK(*fill)
        else:
            c.setFillColorRGB(*fill)
        c.drawPath(
            vector_path,
            stroke=0,
            fill=1,
            fillMode=0 if item["evenodd"] else 1,
        )
    c.restoreState()


def draw_school_lockup(c, page_height, logo_name):
    x, y, w, h = 333, page_height - 76, 222, 50
    c.setFillColor(DARK)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.65)
    c.roundRect(x, y, w, h, 9, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 7.2)
    c.drawString(x + 10, y + 22, "PREPARED FOR")
    c.setStrokeColor(BORDER)
    c.line(x + 83, y + 8, x + 83, y + h - 8)
    logo_box = (x + 88, y + (5 if logo_name == "gsa.png" else 6), 126, 40 if logo_name == "gsa.png" else 38)
    if logo_name == "bird-college-vector.json":
        draw_vector_logo(c, ROOT / "assets/bird-college-logo-vector.json", logo_box)
    elif logo_name:
        fit_image(c, processed_logo_path(logo_name), logo_box, dark_background=False)
    else:
        x, y, w, h = logo_box
        c.setFillColor(PAPER)
        c.setFont("Helvetica-Bold", 17)
        c.drawCentredString(x + w / 2, y + 13, "PPA")


def draw_page_number(c, page_width, number, cover_existing=False):
    number_y = 15
    if cover_existing:
        c.setFillColor(SOURCE_DARK)
        c.rect(page_width - 100, 12, 100, 55, stroke=0, fill=1)
        c.setStrokeColor(BORDER)
        c.setLineWidth(0.8)
        c.line(page_width - 100, 24, page_width - 25, 24)
        c.line(page_width - 25, 12, page_width - 25, 67)
        number_y = 29
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 9)
    c.drawRightString(page_width - 30, number_y, f"{number}/{TOTAL_PAGES}")


def overlay_for(page_width, page_height, school, prepared_for, logo_name, source_page, display_page):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))

    if source_page == 1:
        # A single cover lock-up avoids repeating the recipient mark as if it
        # were part of Actors Alchemy's permanent identity.
        draw_school_lockup(c, page_height, logo_name)
        # Replace the source strapline so workshops lead every description of
        # the offer, with coaching presented as the continuation.
        c.setFillColor(SOURCE_DARK)
        c.rect(92, 695, page_width - 184, 36, stroke=0, fill=1)
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 10.8)
        c.drawCentredString(
            page_width / 2,
            708,
            "Workshops for drama schools and one-to-one coaching with Fraser",
        )
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 9.2)
        c.drawCentredString(page_width / 2, 668, f"Tailored for {prepared_for}")
        c.setFillColor(white)
        c.setFont("Helvetica-Oblique", 8.4)
        c.drawCentredString(
            page_width / 2,
            651,
            "Workshop-led support, with one-to-one coaching when performers need to go further",
        )

    draw_page_number(c, page_width, display_page, cover_existing=True)

    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def paragraph(c, text, x, y_top, width, style):
    p = Paragraph(text, style)
    _, height = p.wrap(width, 1000)
    p.drawOn(c, x, y_top - height)
    return height


def custom_page_base(c, page_width, page_height, number):
    c.setFillColor(DARK)
    c.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.8)
    c.roundRect(25, 24, page_width - 50, page_height - 48, 8, stroke=1, fill=0)
    fit_image(
        c,
        ROOT / "assets/actors-alchemy-wordmark-gold-transparent.png",
        (39, page_height - 76, 155, 32),
        dark_background=False,
    )
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 9)
    c.drawString(39, 15, "ACTORSALCHEMY.CO.UK")
    draw_page_number(c, page_width, number)


def cover_page(page_width, page_height, prepared_for, logo_name):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 1)
    draw_school_lockup(c, page_height, logo_name)
    fit_image(
        c,
        PROCESSED_LOGOS / "actors-alchemy-watermark.png",
        (474, 825, 55, 82),
        dark_background=False,
    )

    c.setFillColor(PAPER)
    c.setFont("Times-Bold", 21)
    c.drawCentredString(page_width / 2, 872, "Welcome to Actors Alchemy!")
    title_style = ParagraphStyle(
        "cover-title",
        fontName="Times-Italic",
        fontSize=30,
        leading=36,
        textColor=PAPER,
        alignment=TA_CENTER,
    )
    paragraph(
        c,
        'Find <font color="#B99455">gold</font> in your performance.',
        60,
        782,
        page_width - 120,
        title_style,
    )
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 16.2)
    c.drawCentredString(page_width / 2, 714, "Bespoke workshops for drama schools and performers in training")

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(58, 166, page_width - 116, 458, 8, stroke=1, fill=1)
    c.setFillColor(white)
    c.setFont("Times-Roman", 30)
    c.drawCentredString(page_width / 2, 562, "WHO ARE WE FOR?")
    cover_copy = ParagraphStyle(
        "cover-copy", fontName="Times-Roman", fontSize=16.4, leading=23,
        textColor=PAPER, alignment=TA_CENTER,
    )
    paragraph(
        c,
        "Actors Alchemy creates specifically curated, performer-led workshops for drama schools. Each session is practical, supportive and shaped around where students are in their training - building confidence and helping them refine their audition process.<br/><br/>Although delivered in a workshop setting, the work remains personal - building from each performer's strengths and helping them strengthen their relationship to the work, to themselves and to the wider industry. Every workshop is designed to complement existing training while remaining adaptable, accessible and affordable.",
        80, 518, page_width - 160, cover_copy,
    )
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def overview_page(page_width, page_height):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 2)
    body = ParagraphStyle(
        "overview-body",
        fontName="Times-Roman",
        fontSize=15,
        leading=18.6,
        textColor=PAPER,
    )

    c.setFillColor(white)
    c.setFont("Times-Roman", 30)
    c.drawCentredString(page_width / 2, 934, "OUR WORKSHOPS")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 15.5)
    c.drawCentredString(page_width / 2, 900, "Bespoke Workshops for Drama Schools and performers in training")

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(58, 68, page_width - 116, 794, 8, stroke=1, fill=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.1)
    c.line(85, 91, 85, 822)
    c.setStrokeColor(BORDER)
    c.line(115, 823, 478, 823)

    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 13.2)
    c.drawString(109, 782, "01")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(146, 815, "HIGHLY RECOMMENDED")
    c.setFont("Times-Roman", 19.8)
    c.drawString(146, 782, "The West End Workshop Series")
    paragraph(
        c,
        "A realistic mock audition environment where performers build confidence, challenge themselves and grow in their understanding. Suitable for all performers looking to strengthen their audition technique, vocal confidence and versatility in the room. Bring a 32-bar cut, learn an intermediate-level movement combination, receive personalised feedback, observe others and finish with an industry Q&amp;A.",
        146,
        753,
        360,
        body,
    )

    c.setStrokeColor(BORDER)
    c.line(110, 580, 511, 580)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 13.2)
    c.drawString(109, 544, "02")
    c.setFont("Times-Roman", 19.8)
    c.drawString(146, 544, "Self-Tape Synthesis")
    paragraph(
        c,
        "A practical workshop on self-tapes as a key part of the audition process, covering tripod recording, cold reading and practical tape technique. Recordings may be used for Spotlight promotion at Fraser's and the practitioner's discretion.",
        146,
        516,
        360,
        body,
    )

    c.setStrokeColor(BORDER)
    c.line(110, 401, 511, 401)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 19.8)
    c.drawString(146, 365, "Further Workshops")
    other_style = ParagraphStyle(
        "other-workshops",
        fontName="Times-Roman",
        fontSize=15.5,
        leading=16.8,
        textColor=PAPER,
    )
    paragraph(
        c,
        '<font color="#B99455">03&nbsp;&nbsp;The Mock Audition</font> - 32 bars, movement, panel etiquette, redirection and confidence under pressure.<br/>'
        '<font color="#B99455">04&nbsp;&nbsp;The Mindset Mentor</font> - Grounding, emotional regulation, self-trust, rejection and resilience.<br/>'
        '<font color="#B99455">05&nbsp;&nbsp;The Company Code</font> - Company etiquette, communication, contracts, rates, networking and professional conduct.<br/>'
        '<font color="#B99455">06&nbsp;&nbsp;Ship Shape: Cruise 101</font> - Cruise audition structure, vocal and movement expectations, rehearsals and life onboard.<br/>'
        '<font color="#B99455">07&nbsp;&nbsp;The Q&amp;A</font> - Casting, representation, submissions, contracts, professional relationships and life after training.',
        130,
        331,
        386,
        other_style,
    )

    c.setStrokeColor(BORDER)
    c.line(110, 157, 511, 157)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11.2)
    c.drawString(146, 137, "TAILORED WITH YOU")
    tailored_style = ParagraphStyle(
        "tailored-workshops",
        fontName="Times-Roman",
        fontSize=15.5,
        leading=17.5,
        textColor=PAPER,
    )
    paragraph(
        c,
        "Each workshop can be tailored with the practitioner to suit their priorities and the current needs of their students.",
        146,
        119,
        360,
        tailored_style,
    )
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def west_end_page(page_width, page_height):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 3)
    body = ParagraphStyle("west-body", fontName="Helvetica", fontSize=8.8, leading=12.7, textColor=PAPER)

    c.setFillColor(white)
    c.setFont("Times-Roman", 27)
    c.drawCentredString(page_width / 2, 918, "THE WEST END WORKSHOP SERIES")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(page_width / 2, 944, "MOST POPULAR")
    c.setFont("Times-Italic", 11.5)
    c.drawCentredString(page_width / 2, 888, "Performer-led training for the room beyond training.")
    paragraph(
        c,
        "A flexible series for musical theatre students, bringing together audition craft, truthful performance, confidence and a grounded understanding of professional life.",
        82, 850, 431, ParagraphStyle("west-intro", parent=body, fontName="Times-Roman", fontSize=13, leading=19, alignment=TA_CENTER),
    )

    modules = [
        ("01  THE AUDITION ROOM", "Work through 32 bars, first impressions, panel etiquette and redirection. Students practise making clear choices while remaining responsive under pressure."),
        ("02  ACTING THROUGH SONG", "Move from technique into story. We explore given circumstances, character, thought changes, action and the relationship between lyric, music and intention."),
        ("03  CONFIDENCE AND MINDSET", "Practical tools for nerves, presence, self-trust, resilience and emotional regulation, helping performers trust their preparation when the room matters."),
        ("04  THE PROFESSIONAL WORLD", "An honest conversation about companies, conduct, agents, contracts, relationships, rejection and life after training, with space for the questions students need answered."),
    ]
    for (title, copy), (x, y) in zip(modules, ((48, 610), (307, 610), (48, 393), (307, 393))):
        c.setFillColor(PANEL)
        c.setStrokeColor(BORDER)
        c.roundRect(x, y, 240, 185, 8, stroke=1, fill=1)
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 14)
        c.drawString(x + 16, y + 150, title)
        paragraph(c, copy, x + 16, y + 127, 208, body)

    c.setFillColor(PANEL)
    c.setStrokeColor(GOLD)
    c.roundRect(48, 184, 499, 152, 8, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 16)
    c.drawString(66, 302, "FLEXIBLE DELIVERY")
    paragraph(
        c,
        "Book a focused session, combine modules into an intensive day, or build a progressive series across the term. Content is adapted to the students, the course and what they are preparing for.",
        66, 277, 463, ParagraphStyle("west-flex", parent=body, fontSize=9.5, leading=14),
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(page_width / 2, 139, "Built to complement existing training, never compete with it.")
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def self_tape_page(page_width, page_height):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 4)
    body = ParagraphStyle("tape-body", fontName="Helvetica", fontSize=9, leading=13.2, textColor=PAPER)
    small = ParagraphStyle("tape-small", parent=body, fontSize=8.2, leading=11.7, textColor=MUTED)

    c.setFillColor(white)
    c.setFont("Times-Roman", 28)
    c.drawCentredString(page_width / 2, 918, "SELF-TAPE STUDY")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 11.5)
    c.drawCentredString(page_width / 2, 888, "Clear choices. Practical technique. Truth on camera.")
    paragraph(
        c,
        "A practical workshop helping students understand the self-tape as both an acting exercise and a professional submission.",
        88, 850, 419, ParagraphStyle("tape-intro", parent=body, fontName="Times-Roman", fontSize=13, leading=19, alignment=TA_CENTER),
    )

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(48, 410, 240, 375, 8, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 17)
    c.drawString(66, 750, "FROM SETUP TO STORY")
    paragraph(
        c,
        "01 - Setup on a budget<br/><br/>02 - Lighting, sound and framing<br/><br/>03 - Cold reading and preparation<br/><br/>04 - Working with a reader<br/><br/>05 - Acting truthfully for the lens<br/><br/>06 - Choosing and refining a take<br/><br/>07 - Feedback without chasing perfection",
        66, 716, 204, body,
    )

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(307, 410, 240, 375, 8, stroke=1, fill=1)
    stages = [
        ("PREPARE", "Break down the text, identify what changes and make specific, playable choices."),
        ("RECORD", "Find a simple technical setup and remain connected to the reader, the story and the lens."),
        ("REVIEW", "Watch the work constructively, identify what communicates and decide what genuinely needs another take."),
    ]
    y = 746
    for title, copy in stages:
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 15)
        c.drawString(325, y, title)
        paragraph(c, copy, 325, y - 22, 204, small)
        y -= 112
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 11)
    c.drawString(325, 450, "Preparation over perfection.")

    c.setFillColor(PANEL)
    c.setStrokeColor(GOLD)
    c.roundRect(48, 207, 499, 150, 8, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 16)
    c.drawString(66, 322, "FOR DRAMA SCHOOLS")
    paragraph(
        c,
        "Self-Tape Study can be delivered as a standalone workshop or paired with the West End Workshop Series. It gives students repeatable tools they can take into future submissions, recalls and graduate showcases.",
        66, 294, 463, ParagraphStyle("tape-school", parent=body, fontSize=9.5, leading=14),
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(page_width / 2, 157, "Group learning can be followed by guided tape review and reflection.")
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def coaching_page(page_width, page_height):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 5)
    body = ParagraphStyle("coach-body", fontName="Helvetica", fontSize=9.3, leading=13.7, textColor=PAPER)
    small = ParagraphStyle("coach-small", parent=body, fontSize=8.4, leading=12, textColor=MUTED)

    c.setFillColor(white)
    c.setFont("Times-Roman", 28)
    c.drawCentredString(page_width / 2, 918, "ONE-TO-ONE COACHING")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 12)
    c.drawCentredString(page_width / 2, 888, "An affordable space to build on audition material and grow in confidence.")
    paragraph(
        c,
        "Workshops open the conversation. One-to-one coaching gives the performer room to apply it to their own material, goals and next audition.",
        82, 846, 431, ParagraphStyle("coach-intro", parent=body, fontName="Times-Roman", fontSize=13, leading=19, alignment=TA_CENTER),
    )

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(48, 430, 499, 350, 8, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 18)
    c.drawString(68, 744, "PERSONALISED AROUND THE PERFORMER")
    paragraph(c, "Bring an upcoming audition, a self-tape, new repertoire or an area of the craft that needs attention. The session begins with what will be most useful now.", 68, 713, 459, body)
    focuses = [
        ("AUDITION MATERIAL", "Break down text, sharpen choices and prepare work that feels specific and lived."),
        ("ACTING THROUGH SONG", "Connect character, thought and action so technique serves the story."),
        ("SELF-TAPE REVIEW", "Study what communicates on camera and leave with clear, practical next steps."),
        ("CONFIDENCE AND MINDSET", "Build preparation, self-trust and a healthier relationship with pressure."),
    ]
    for (title, copy), (x, y) in zip(focuses, ((68, 566), (310, 566), (68, 458), (310, 458))):
        c.setFillColor(DARK)
        c.setStrokeColor(BORDER)
        c.roundRect(x, y, 217, 88, 6, stroke=1, fill=1)
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 12.5)
        c.drawString(x + 13, y + 62, title)
        paragraph(c, copy, x + 13, y + 44, 191, small)

    c.setFillColor(PANEL)
    c.setStrokeColor(GOLD)
    c.roundRect(48, 220, 499, 160, 8, stroke=1, fill=1)
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 16)
    c.drawString(66, 345, "CONTINUITY AFTER THE WORKSHOP")
    paragraph(
        c,
        "Schools can make students aware of Actors Alchemy as an optional source of individual support. Coaching is online, flexible and designed to complement the teaching and pastoral structures already in place.",
        66, 317, 463, body,
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(page_width / 2, 168, "Support when it is useful - never pressure to purchase.")
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def testimonials_page(page_width, page_height, testimonials):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 3)

    c.setFillColor(white)
    c.setFont("Times-Roman", 29)
    c.drawCentredString(page_width / 2, 926, "PERFORMER SUCCESS")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 16.5)
    c.drawCentredString(page_width / 2, 888, "What performers are saying.")

    quote_style = ParagraphStyle(
        "testimonial-collection",
        fontName="Times-Roman",
        fontSize=16.8,
        leading=21.2,
        textColor=PAPER,
        alignment=TA_LEFT,
    )

    for (image_path, name, booking, quote), y in zip(testimonials, (605, 358, 111)):
        c.setFillColor(PANEL)
        c.setStrokeColor(BORDER)
        c.roundRect(58, y, page_width - 116, 235, 8, stroke=1, fill=1)

        image_offset_y = -10 if image_path.name == "patricia-kuhne.jpeg" else 0
        draw_circular_image(c, image_path, 107, y + 184, 38, image_offset_y)

        c.setFillColor(GOLD)
        c.setFont("Times-Bold", 20)
        c.drawString(160, y + 194, name)
        c.setFillColor(MUTED)
        c.setFont("Times-Roman", 14.6)
        c.drawString(160, y + 166, f"Booked: {booking}")

        paragraph(c, f'"{quote}"', 78, y + 137, page_width - 156, quote_style)

    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def partners_page(page_width, page_height):
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(page_width, page_height))
    custom_page_base(c, page_width, page_height, 4)

    c.setFillColor(white)
    c.setFont("Times-Roman", 24)
    c.drawCentredString(page_width / 2, 926, "OUR PARTNERSHIPS")
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 17)
    c.drawCentredString(page_width / 2, 888, "Solid foundations are built through trusted relationships.")

    c.setFillColor(PANEL)
    c.setStrokeColor(BORDER)
    c.roundRect(58, 610, page_width - 116, 195, 8, stroke=1, fill=1)
    c.setFillColor(DARK)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.65)
    c.roundRect(80, 721, page_width - 160, 60, 8, stroke=1, fill=1)
    fit_image(
        c,
        PROCESSED_LOGOS / "spotlight-logo-white.png",
        (104, 731, page_width - 208, 40),
        dark_background=False,
    )
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 19.8)
    c.drawCentredString(page_width / 2, 691, "SPOTLIGHT CASTING")
    partner_style = ParagraphStyle("partner", fontName="Times-Roman", fontSize=15, leading=19, textColor=PAPER, alignment=TA_CENTER)
    paragraph(
        c,
        "Supporting performers to refine their profiles and present their work with confidence.",
        92,
        664,
        page_width - 184,
        partner_style,
    )

    cards = [
        (58, 335, PROCESSED_LOGOS / "wilkes-academy-cropped.png", "WILKES ACADEMY", "Supporting performers in training as they prepare for the profession."),
        (315, 335, PROCESSED_LOGOS / "you-management-logo.png", "YOU MANAGEMENT", "Connecting Actors Alchemy with performers moving into professional work."),
    ]
    for x, y, image_path, title, copy in cards:
        c.setFillColor(PANEL)
        c.setStrokeColor(BORDER)
        c.roundRect(x, y, 222, 254, 8, stroke=1, fill=1)
        c.setFillColor(DARK)
        c.setStrokeColor(GOLD)
        c.setLineWidth(0.65)
        c.roundRect(x + 21, y + 118, 180, 102, 8, stroke=1, fill=1)
        fit_image(c, image_path, (x + 37, y + 132, 148, 74), dark_background=False)
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 19.8)
        c.drawCentredString(x + 111, y + 85, title)
        paragraph(c, copy, x + 18, y + 61, 186, partner_style)

    closing = ParagraphStyle("closing", fontName="Times-Roman", fontSize=16.4, leading=23, textColor=PAPER, alignment=TA_CENTER)
    paragraph(
        c,
        "Actors Alchemy values relationships with schools and industry partners who share a commitment to supportive, practical development for performers.",
        76, 300, 443, closing,
    )
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 17)
    c.drawCentredString(page_width / 2, 192, "Together, let's help shape the future of industry talent.")
    c.setFillColor(PAPER)
    c.setFont("Times-Roman", 15)
    c.drawCentredString(page_width / 2, 150, "fraser@actorsalchemy.co.uk")
    c.drawCentredString(page_width / 2, 124, "actorsalchemy.co.uk")
    c.save()
    stream.seek(0)
    return PdfReader(stream).pages[0]


def build_pack(school, prepared_for, logo_name):
    reader = PdfReader(SOURCE)
    writer = PdfWriter()
    width = float(reader.pages[0].mediabox.width)
    height = float(reader.pages[0].mediabox.height)
    writer.add_page(cover_page(width, height, prepared_for, logo_name))
    writer.add_page(overview_page(width, height))
    testimonials = [
        (
            ROOT / "assets/jamie-bailes.jpeg",
            "Jamie Bailes",
            "Original cast of Back to the Future",
            "Working with Fraser helped me to characterise and express freely, allowing me to connect with the material more than I ever had before. Fraser's guidance is insightful and encouraging, has developed my understanding of acting through song, and has provided me the tools to approach new material with confidence!",
        ),
        (
            ROOT / "assets/patricia-kuhne.jpeg",
            "Patricia Kühne",
            "TV & Film",
            "Working with Fraser as my acting coach was really transformative. We focused a lot on scene work, and I saw a big improvement in my skills and confidence. Fraser is a fantastic teacher, very supportive, clear, and he really helped me grow as an actor. I'm so thankful for his guidance.",
        ),
        (
            ROOT / "assets/testimonial-casey-martin-klein.jpg",
            "Casey Martin Klein",
            "Regional / Off-Broadway",
            "I've had the pleasure of knowing and working with Fraser for several years. His professionalism, creativity and talent are matched by his kindness and humour. He is a generous collaborator who brings light into every room, always arriving prepared with an idea, an opinion and a solution.",
        ),
    ]
    writer.add_page(testimonials_page(width, height, testimonials))

    writer.add_page(partners_page(width, height))

    writer.add_metadata({
        "/Title": f"Actors Alchemy - Introduction for {school}",
        "/Author": "Actors Alchemy",
        "/Subject": "Drama school workshops for performers in training",
    })
    path = OUT / f"actors-alchemy-intro-pack-{slugify(school)}.pdf"
    with path.open("wb") as fh:
        writer.write(fh)
    return path


def prepare_transparent_logo(source, destination, gold_silhouette=False, strengthen=False, crop_top_fraction=None):
    """Remove an edge-connected field and make a dark-page-safe logo.

    Flood filling from the corners removes only the surrounding white or black
    field, so enclosed white details (for example Bird's lettering) survive.
    A padded transparent canvas then protects every mark from clipping.
    """
    with Image.open(source) as source_image:
        if crop_top_fraction is not None:
            source_image = source_image.crop(
                (0, 0, source_image.width, round(source_image.height * crop_top_fraction))
            )
        image = source_image.convert("RGBA")
    corner_rgb = image.getpixel((0, 0))[:3]
    dark_background_source = image.getextrema()[3][0] == 255 and max(corner_rgb) < 80

    # Existing transparency is preserved. Baked-in JPEG/PNG backgrounds are
    # removed from every corner to catch edge-connected compression variants.
    if image.getextrema()[3][0] == 255:
        for seed in ((0, 0), (image.width - 1, 0), (0, image.height - 1), (image.width - 1, image.height - 1)):
            ImageDraw.floodfill(image, seed, (0, 0, 0, 0), thresh=52)

    pixels = image.load()
    paper_rgb = (244, 239, 230)
    gold_rgb = (185, 148, 85)
    for py in range(image.height):
        for px in range(image.width):
            red, green, blue, alpha = pixels[px, py]
            if alpha == 0:
                continue
            high = max(red, green, blue)
            low = min(red, green, blue)
            if high < 92:
                if dark_background_source:
                    pixels[px, py] = (0, 0, 0, 0)
                else:
                    replacement = gold_rgb if gold_silhouette else paper_rgb
                    pixels[px, py] = (*replacement, alpha)
            elif high > 224 and high - low < 24:
                if strengthen:
                    pixels[px, py] = (0, 0, 0, 0)
                else:
                    pixels[px, py] = (*paper_rgb, alpha)

    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        raise ValueError(f"Logo became empty: {source}")
    image = image.crop(bbox)
    if strengthen:
        # Fine circular seals lose their lettering at cover size. A restrained
        # one-pixel expansion keeps the official geometry visible when reduced.
        mask = image.getchannel("A").filter(ImageFilter.MaxFilter(3))
        strengthened = Image.new("RGBA", image.size, (*gold_rgb, 0))
        strengthened.putalpha(mask)
        image = strengthened
    pad_x = max(12, round(image.width * 0.08))
    pad_y = max(10, round(image.height * 0.12))
    padded = Image.new("RGBA", (image.width + pad_x * 2, image.height + pad_y * 2), (0, 0, 0, 0))
    padded.alpha_composite(image, (pad_x, pad_y))
    destination.parent.mkdir(parents=True, exist_ok=True)
    padded.save(destination)


def prepare_dark_logo_on_white(source, destination):
    """Convert a clean black-on-white logo into a crisp light transparent mark."""
    with Image.open(source) as source_image:
        grayscale = source_image.convert("L")
    alpha = grayscale.point(lambda value: 255 - value)
    bbox = alpha.getbbox()
    if not bbox:
        raise ValueError(f"Logo became empty: {source}")
    alpha = alpha.crop(bbox)
    image = Image.new("RGBA", alpha.size, (244, 239, 230, 0))
    image.putalpha(alpha)
    pad_x = max(12, round(image.width * 0.08))
    pad_y = max(10, round(image.height * 0.12))
    padded = Image.new("RGBA", (image.width + pad_x * 2, image.height + pad_y * 2), (0, 0, 0, 0))
    padded.alpha_composite(image, (pad_x, pad_y))
    destination.parent.mkdir(parents=True, exist_ok=True)
    padded.save(destination)


def prepare_all_logos():
    PROCESSED_LOGOS.mkdir(parents=True, exist_ok=True)
    names = {item[2] for item in SCHOOLS if item[2]}
    for name in names:
        if name == "bird-college-vector.json":
            continue
        if name in {"emil-dale-official.svg.png", "mountview-official.png"}:
            prepare_dark_logo_on_white(LOGOS / name, processed_logo_path(name))
            continue
        prepare_transparent_logo(
            LOGOS / name,
            processed_logo_path(name),
            gold_silhouette=(name in {"artsed.png", "gsa.png"}),
            strengthen=(name == "gsa.png"),
        )
    prepare_transparent_logo(
        LOGOS / "wilkes-academy-cropped.png",
        PROCESSED_LOGOS / "wilkes-academy-cropped.png",
    )
    prepare_transparent_logo(
        ROOT / "assets/you-management-logo.png",
        PROCESSED_LOGOS / "you-management-logo.png",
    )
    prepare_transparent_logo(
        ROOT / "assets/spotlight-logo-white.png",
        PROCESSED_LOGOS / "spotlight-logo-white.png",
        crop_top_fraction=0.66,
    )
    with Image.open(ROOT / "assets/actors-alchemy-logo-lockup.png") as source_image:
        watermark = source_image.convert("RGBA").crop((70, 30, 215, 215))
    alpha = watermark.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        raise ValueError("Actors Alchemy watermark became empty")
    watermark = watermark.crop(bbox)
    alpha = watermark.getchannel("A").point(lambda value: round(value * 0.18))
    tinted = Image.new("RGBA", watermark.size, (185, 148, 85, 0))
    tinted.putalpha(alpha)
    tinted.save(PROCESSED_LOGOS / "actors-alchemy-watermark.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prepare_all_logos()
    for item in SCHOOLS:
        print(build_pack(*item))


if __name__ == "__main__":
    main()

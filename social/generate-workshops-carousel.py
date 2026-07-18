from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ROOT / "social" / "workshops-carousel"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
PAD = 78

GRAPHITE = "#24211d"
GRAPHITE_SOFT = "#312d27"
LEAD = "#3c3832"
PARCHMENT = "#efe6d7"
WARM_WHITE = "#f8f3eb"
OAT = "#e8ddce"
OAT_DEEP = "#d4c4af"
RUST = "#9b512f"
RUST_DEEP = "#77391f"
COPPER = "#b86e43"
GOLD = "#c99a4a"
GOLD_SOFT = "#d8b66d"

GEORGIA = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def cover_image(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def add_texture(draw: ImageDraw.ImageDraw, dark: bool = False) -> None:
    base = (232, 221, 206, 255) if not dark else (36, 33, 29, 255)
    for y in range(0, H, 6):
      shade = 4 if y % 12 == 0 else 0
      colour = tuple(max(0, min(255, c - shade)) for c in base[:3]) + (36,)
      draw.line((0, y, W, y), fill=colour, width=1)


def new_slide(dark: bool = False, photo: bool = False) -> Image.Image:
    if photo:
        image = cover_image(ASSETS / "stage-reel-stage-1.jpg", (W, H)).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (36, 33, 29, 0))
        od = ImageDraw.Draw(overlay)
        for y in range(H):
            alpha = int(42 + (y / H) * 178)
            od.line((0, y, W, y), fill=(36, 33, 29, alpha))
        od.rectangle((0, 0, 310, H), fill=(119, 57, 31, 95))
        image.alpha_composite(overlay)
        return image

    image = Image.new("RGBA", (W, H), GRAPHITE if dark else OAT)
    draw = ImageDraw.Draw(image)
    add_texture(draw, dark=dark)
    draw.rectangle((0, 0, W, 26), fill=RUST if dark else RUST_DEEP)
    draw.rectangle((0, H - 26, W, H), fill=GOLD if dark else RUST)
    draw.ellipse((W - 155, -155, W + 250, 250), fill=(201, 154, 74, 52 if dark else 62))
    draw.ellipse((-170, H - 300, 245, H + 115), fill=(155, 81, 47, 60 if dark else 76))
    draw.line((PAD, 175, W - PAD, 175), fill=(216, 182, 109, 95) if dark else (119, 57, 31, 72), width=2)
    return image


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if current and text_size(draw, trial, fnt)[0] > width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill: str,
    width: int,
    line_spacing: int,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_spacing
    return y


def draw_brand(draw: ImageDraw.ImageDraw, dark: bool = False) -> None:
    icon_fill = GOLD_SOFT if dark else RUST_DEEP
    text_fill = PARCHMENT if dark else GRAPHITE
    x, y = PAD, PAD
    draw.ellipse((x, y + 11, x + 31, y + 42), outline=icon_fill, width=3)
    draw.polygon(((x + 15, y), (x + 22, y + 22), (x + 8, y + 22)), fill=icon_fill)
    draw.arc((x + 7, y + 20, x + 24, y + 36), 10, 170, fill=icon_fill, width=3)
    draw.text((x + 48, y + 1), "Actors", font=font(GEORGIA, 31), fill=text_fill)
    draw.text((x + 144, y + 1), "Alchemy", font=font(GEORGIA, 31), fill=icon_fill)


def draw_count(draw: ImageDraw.ImageDraw, count: str, dark: bool = False) -> None:
    x0, y0, size = W - PAD - 76, PAD, 76
    outline = (239, 230, 215, 90) if dark else (117, 103, 91, 90)
    draw.ellipse((x0, y0, x0 + size, y0 + size), outline=outline, width=2)
    fnt = font(GEORGIA_BOLD, 31)
    tw, th = text_size(draw, count, fnt)
    draw.text((x0 + (size - tw) / 2, y0 + (size - th) / 2 - 4), count, font=fnt, fill=GOLD_SOFT if dark else RUST_DEEP)


def draw_footer(draw: ImageDraw.ImageDraw, left: str, right: str, dark: bool = False) -> None:
    fnt = font(ARIAL_BOLD, 20)
    fill = (248, 243, 235, 190) if dark else (60, 56, 50, 180)
    draw.text((PAD, H - PAD - 28), left.upper(), font=fnt, fill=fill)
    rw, _ = text_size(draw, right.upper(), fnt)
    draw.text((W - PAD - rw, H - PAD - 28), right.upper(), font=fnt, fill=fill)


def draw_pills(draw: ImageDraw.ImageDraw, x: int, y: int, pills: list[str], dark: bool = False, max_width: int = 850) -> int:
    fnt = font(ARIAL_BOLD, 24)
    cx, cy = x, y
    for pill in pills:
        tw, th = text_size(draw, pill, fnt)
        pw, ph = tw + 42, 48
        if cx + pw > x + max_width:
            cx = x
            cy += ph + 16
        fill = (232, 221, 206, 245) if dark else (248, 243, 235, 155)
        outline = (239, 230, 215, 75) if dark else (117, 103, 91, 75)
        text_fill = GRAPHITE if dark else LEAD
        draw.rounded_rectangle((cx, cy, cx + pw, cy + ph), radius=5, fill=fill, outline=outline, width=2)
        draw.text((cx + 21, cy + 10), pill, font=fnt, fill=text_fill)
        cx += pw + 16
    return cy + 66


def duration(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, dark: bool = False) -> None:
    fnt = font(ARIAL_BOLD, 25)
    tw, th = text_size(draw, text, fnt)
    fill = GOLD if dark else GRAPHITE
    text_fill = GRAPHITE if dark else WARM_WHITE
    draw.rounded_rectangle((x, y, x + tw + 44, y + 56), radius=5, fill=fill)
    draw.text((x + 22, y + 15), text, font=fnt, fill=text_fill)


def workshop_slide(number: int, kicker: str, title: str, lede: str, supporting: str, pills: list[str], length: str, dark: bool) -> Image.Image:
    image = new_slide(dark=dark)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, dark=dark)
    draw_count(draw, f"{number + 2:02d}", dark=dark)

    x, y, width = PAD, 255, 780
    draw.text((x, y), kicker.upper(), font=font(ARIAL_BOLD, 21), fill=GOLD_SOFT if dark else RUST_DEEP)
    y += 58
    y = draw_wrapped(draw, (x, y), title, font(GEORGIA_BOLD, 86 if len(title) > 24 else 94), PARCHMENT if dark else GRAPHITE, width, 6)
    y += 26
    y = draw_wrapped(draw, (x, y), lede, font(ARIAL_BOLD, 35), (248, 243, 235, 230) if dark else (60, 56, 50, 222), width, 11)
    y += 20
    y = draw_wrapped(draw, (x, y), supporting, font(ARIAL, 29), (248, 243, 235, 198) if dark else (60, 56, 50, 205), width, 10)
    y += 30
    y = draw_pills(draw, x, y, pills, dark=dark, max_width=820)
    duration(draw, x, min(y + 10, H - 205), length, dark=dark)

    mark = f"{number:02d}"
    mark_fnt = font(GEORGIA_BOLD, 285)
    mw, mh = text_size(draw, mark, mark_fnt)
    mark_fill = (201, 154, 74, 72) if dark else (119, 57, 31, 74)
    draw.text((W - PAD - mw, 785), mark, font=mark_fnt, fill=mark_fill)
    draw_footer(draw, "Workshop offerings", f"{number + 2:02d} / 09", dark=dark)
    return image


slides = [
    {
        "kind": "cover",
        "title": "Your bridge between training and the industry.",
        "lede": "Practical, caring and no-nonsense workshops for performers in training.",
    },
    {
        "kind": "aim",
        "title": "Refine the work. Ready the performer.",
        "lede": "Created by industry-leading performers, these sessions help students strengthen their relationship to the work, themselves and the industry ahead.",
        "pills": ["deep dives", "performer-led", "mock audition simulation", "clearer choices", "professional confidence"],
    },
]

workshops = [
    (
        1,
        "Workshop 01",
        "The Mock Audition",
        "A simulated audition experience helping students understand the room and their place in it.",
        "We explore 32 bars, a movement combination and the practical choices that help performers stay present under pressure.",
        ["32 bars", "movement", "text work", "panel etiquette", "redirection", "nerves"],
        "Proposed length: 2 hrs",
        True,
    ),
    (
        2,
        "Workshop 02",
        "The Mindset Mentor",
        "A practical workshop for nerves, pressure, self-trust and performance anxiety.",
        "Students begin to understand their own programming, build grounded confidence and trust the preparation they have already done.",
        ["grounding tools", "confidence", "emotional regulation", "presence", "resilience"],
        "Proposed length: 1 hr",
        False,
    ),
    (
        3,
        "Workshop 03",
        "The Company Code",
        "Professional conduct for performers entering rehearsal rooms, contracts and companies.",
        "A no-nonsense look at the practical realities around etiquette, communication, pay, scams and self-promotion.",
        ["company etiquette", "chain of command", "Equity rates", "exposure pay", "online scams", "networking"],
        "Proposed length: 1 hr",
        True,
    ),
    (
        4,
        "Workshop 04",
        "Self-Tape Synthesis",
        "A practical session on self-tapes as a key part of the audition process.",
        "Students work through setup, tripod recording, cold reading and tape technique, with recordings usable for Spotlight promotion at Fraser's and the practitioner's discretion.",
        ["budget setup", "lighting", "sound", "framing", "reader work", "truth on camera"],
        "Proposed length: 2 hrs",
        False,
    ),
    (
        5,
        "Workshop 05",
        "Ship Shape: Cruise 101",
        "A practical introduction to cruise auditions and life inside the contract.",
        "Tailored upon request for singers or dancers, covering performance and organisation from auditions, visas and rehearsals through to life onboard.",
        ["singers or dancers", "audition structure", "movement", "vocal expectations", "visas", "life onboard"],
        "Proposed length: 2 hrs",
        True,
    ),
]


def render_cover() -> Image.Image:
    image = new_slide(photo=True)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, dark=True)
    draw_count(draw, "01", dark=True)
    x, y = PAD, 620
    draw.text((x, y), "DRAMA SCHOOL TO THE INDUSTRY", font=font(ARIAL_BOLD, 22), fill=GOLD_SOFT)
    y += 62
    y = draw_wrapped(draw, (x, y), slides[0]["title"], font(GEORGIA_BOLD, 98), PARCHMENT, 880, 6)
    y += 28
    draw_wrapped(draw, (x, y), slides[0]["lede"], font(ARIAL_BOLD, 36), (248, 243, 235, 232), 815, 12)
    draw_footer(draw, "Workshop offerings", "Photo: Mark Senior", dark=True)
    return image


def render_aim() -> Image.Image:
    image = new_slide(dark=False)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, dark=False)
    draw_count(draw, "02", dark=False)
    x, y = PAD, 300
    draw.text((x, y), "THE AIM", font=font(ARIAL_BOLD, 22), fill=RUST_DEEP)
    y += 64
    y = draw_wrapped(draw, (x, y), slides[1]["title"], font(GEORGIA_BOLD, 96), GRAPHITE, 880, 6)
    y += 34
    y = draw_wrapped(draw, (x, y), slides[1]["lede"], font(ARIAL_BOLD, 36), (60, 56, 50, 222), 850, 12)
    y += 46
    draw_pills(draw, x, y, slides[1]["pills"], dark=False, max_width=850)
    draw_footer(draw, "Actors Alchemy", "02 / 09", dark=False)
    return image


def render_qa() -> Image.Image:
    image = new_slide(dark=False)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, dark=False)
    draw_count(draw, "08", dark=False)
    x, y = PAD, 282
    draw.text((x, y), "ADD-ON OR STANDALONE", font=font(ARIAL_BOLD, 22), fill=RUST_DEEP)
    y += 64
    y = draw_wrapped(draw, (x, y), "The Q&A", font(GEORGIA_BOLD, 104), GRAPHITE, 850, 6)
    y += 34
    y = draw_wrapped(draw, (x, y), "An honest conversation connected to any workshop, giving students space to ask the industry questions they actually need answered.", font(ARIAL_BOLD, 36), (60, 56, 50, 222), 840, 12)
    y += 42
    y = draw_pills(draw, x, y, ["casting", "agents", "contracts", "auditions", "self-tapes", "relationships", "rejection", "life after training"], max_width=850)
    duration(draw, x, y + 12, "Length: flexible")
    draw_footer(draw, "Workshop offerings", "08 / 09", dark=False)
    return image


def render_cta() -> Image.Image:
    image = new_slide(dark=True)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, dark=True)
    draw_count(draw, "09", dark=True)
    x, y = PAD, 270
    draw.text((x, y), "BRING ACTORS ALCHEMY TO YOUR SCHOOL", font=font(ARIAL_BOLD, 22), fill=GOLD_SOFT)
    y += 64
    y = draw_wrapped(draw, (x, y), "Let's shape the right support for your students.", font(GEORGIA_BOLD, 92), PARCHMENT, 860, 6)
    y += 44
    box_h = 258
    draw.rounded_rectangle((x, y, W - PAD, y + box_h), radius=5, fill=OAT, outline=(239, 230, 215, 58), width=2)
    ty = y + 36
    ty = draw_wrapped(draw, (x + 36, ty), "Workshops can be booked individually, mixed and matched, combined with The Q&A or expanded into weekly sessions.", font(ARIAL_BOLD, 35), LEAD, 770, 12)
    ty += 18
    draw_wrapped(draw, (x + 36, ty), "Each format can be scaled up or down depending on the course leader's needs.", font(ARIAL, 29), LEAD, 760, 10)
    y += box_h + 46
    draw_pills(draw, x, y, ["acting", "musical theatre", "screen acting", "agents", "auditions", "professional rooms"], dark=True, max_width=850)
    draw_footer(draw, "fraser@actorsalchemy.co.uk", "actorsalchemy.co.uk/workshops", dark=True)
    return image


rendered = [render_cover(), render_aim()]
for item in workshops:
    rendered.append(workshop_slide(*item))
rendered.append(render_qa())
rendered.append(render_cta())

for index, image in enumerate(rendered, start=1):
    image.convert("RGB").save(OUT / f"actors-alchemy-workshops-carousel-{index:02d}.png", quality=95)

thumb_w = 270
thumb_h = int(H * (thumb_w / W))
contact = Image.new("RGB", (thumb_w * 3, thumb_h * 3), "#171411")
for index, image in enumerate(rendered):
    thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    contact.paste(thumb, ((index % 3) * thumb_w, (index // 3) * thumb_h))
contact.save(OUT / "actors-alchemy-workshops-carousel-contact-sheet.png", quality=95)

print(f"Exported {len(rendered)} slides to {OUT}")

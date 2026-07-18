const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "social", "workshop-offerings-carousel");
fs.mkdirSync(outDir, { recursive: true });

const assetsDir = path.join(root, "assets");
const wordmark = path.join(assetsDir, "actors-alchemy-logo-wordmark.png");
const wordmarkParchment = path.join(assetsDir, "actors-alchemy-logo-wordmark-parchment.png");
const wordmarkRust = path.join(assetsDir, "actors-alchemy-wordmark-rust-transparent.png");
const wordmarkGold = path.join(assetsDir, "actors-alchemy-wordmark-gold-transparent.png");
const icon = path.join(assetsDir, "actors-alchemy-icon.svg");

const palette = {
  graphite: "#3c3832",
  charcoal: "#28241f",
  parchment: "#efe6d7",
  warm: "#f8f3eb",
  oat: "#d4c4af",
  rust: "#9d693d",
  deepRust: "#7e4d2c",
  gold: "#d6b16a",
  taupe: "#75675b",
  chocolate: "#6b5948",
  mutedChocolate: "#8d7660",
};

const toneRamp = [
  {
    bg: "#f8f3eb",
    wash: "#efe6d7",
    primary: palette.graphite,
    muted: palette.taupe,
    accent: palette.rust,
    border: palette.oat,
    inner: palette.gold,
    panel: palette.warm,
    panelOpacity: 0.68,
    curve: palette.oat,
    circle: palette.gold,
    markOpacity: 0.05,
    darkLogo: false,
  },
  {
    bg: "#f1e7d9",
    wash: "#e7d8c6",
    primary: palette.graphite,
    muted: "#6f6256",
    accent: palette.rust,
    border: "#cdbba4",
    inner: palette.gold,
    panel: "#fbf4e9",
    panelOpacity: 0.62,
    curve: "#c7b39d",
    circle: "#d8c5ad",
    markOpacity: 0.052,
    darkLogo: false,
  },
  {
    bg: "#e1d0bb",
    wash: "#d5c0a8",
    primary: palette.graphite,
    muted: "#625449",
    accent: palette.deepRust,
    border: "#bfa88f",
    inner: palette.gold,
    panel: "#f3e5d4",
    panelOpacity: 0.55,
    curve: "#b59d84",
    circle: "#c7ad92",
    markOpacity: 0.056,
    darkLogo: false,
  },
  {
    bg: "#cdb89f",
    wash: "#bda68e",
    primary: "#322c27",
    muted: "#5a4d43",
    accent: palette.deepRust,
    border: "#a38a72",
    inner: palette.gold,
    panel: "#eadcc9",
    panelOpacity: 0.46,
    curve: "#9d856e",
    circle: "#ae9379",
    markOpacity: 0.06,
    darkLogo: false,
  },
  {
    bg: "#b89f87",
    wash: "#a98f77",
    primary: palette.graphite,
    muted: "#55483e",
    accent: palette.deepRust,
    border: "#927864",
    inner: palette.gold,
    panel: "#e8d7c4",
    panelOpacity: 0.62,
    curve: "#816c5a",
    circle: "#9a8069",
    markOpacity: 0.062,
    darkLogo: false,
  },
  {
    bg: "#9f8871",
    wash: "#8f7965",
    primary: palette.graphite,
    muted: "#4f433a",
    accent: palette.deepRust,
    border: "#7d6958",
    inner: palette.gold,
    panel: "#dfcdb8",
    panelOpacity: 0.62,
    curve: "#705e4f",
    circle: "#806c5a",
    markOpacity: 0.064,
    darkLogo: false,
  },
  {
    bg: "#846f5c",
    wash: "#735f50",
    primary: palette.charcoal,
    muted: "#493d35",
    accent: palette.deepRust,
    border: "#6f5b4d",
    inner: palette.gold,
    panel: "#d8c2aa",
    panelOpacity: 0.64,
    curve: "#604f43",
    circle: "#6b5948",
    markOpacity: 0.066,
    darkLogo: false,
  },
];

const oatBackground = {
  bg: "#f1e7d9",
  wash: "#eadfce",
  primary: palette.graphite,
  muted: "#5f544b",
  accent: palette.rust,
  border: "#cdbba4",
  inner: palette.gold,
  panel: "#fbf4e9",
  panelOpacity: 0.58,
  curve: "#c3ad94",
  circle: "#d8c5ad",
  darkLogo: false,
};

toneRamp.forEach((tone, index) => {
  Object.assign(tone, oatBackground, {
    markOpacity: 0.048 + index * 0.003,
    circle: index % 2 === 0 ? "#d8c5ad" : "#cfbaa1",
    curve: index % 2 === 0 ? "#c3ad94" : "#b99f84",
  });
});

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function wrap(text, maxChars) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if (next.length > maxChars && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

function textLines(lines, { x, y, size, lineHeight, cls = "body", anchor = "middle", weight = 400, color, italic = false, opacity = 1 }) {
  return lines
    .map((line, index) => {
      const attrs = [
        `class="${cls}"`,
        `x="${x}"`,
        `y="${y + index * lineHeight}"`,
        `font-size="${size}"`,
        `font-weight="${weight}"`,
        `fill="${color}"`,
        `text-anchor="${anchor}"`,
        `opacity="${opacity}"`,
      ];
      if (italic) attrs.push(`font-style="italic"`);
      return `<text ${attrs.join(" ")}>${esc(line)}</text>`;
    })
    .join("\n");
}

function bulletGrid(items, { x, y, columns = 3, columnWidth = 268, rowHeight = 27, size = 15, color = palette.charcoal }) {
  if (!items?.length) return "";
  return items
    .map((item, index) => {
      const col = index % columns;
      const row = Math.floor(index / columns);
      const itemX = x + col * columnWidth;
      const itemY = y + row * rowHeight;
      return `<g>
        <circle cx="${itemX}" cy="${itemY - 8}" r="5" fill="${color}" opacity="0.95"/>
        <text class="heading" x="${itemX + 20}" y="${itemY}" font-size="${size}" font-weight="500" fill="${color}" opacity="0.97">${esc(item)}</text>
      </g>`;
    })
    .join("\n");
}

function logo(y = 118, scale = 0.86, dark = false) {
  if (!dark && fs.existsSync(wordmark)) {
    return `<image href="${esc(wordmark)}" x="${540 - 292 * scale}" y="${y - 64 * scale}" width="${584 * scale}" height="${126 * scale}" preserveAspectRatio="xMidYMid meet"/>`;
  }
  if (dark && fs.existsSync(wordmarkGold)) {
    return `<image href="${esc(wordmarkGold)}" x="${540 - 255 * scale}" y="${y - 55 * scale}" width="${510 * scale}" height="${110 * scale}" preserveAspectRatio="xMidYMid meet"/>`;
  }
  const actors = dark ? palette.warm : palette.graphite;
  const alchemy = dark ? palette.gold : palette.rust;
  const iconMarkup = fs.existsSync(icon)
    ? `<image href="${esc(icon)}" x="${Math.round(-190 * scale)}" y="${Math.round(-55 * scale)}" width="${Math.round(68 * scale)}" height="${Math.round(94 * scale)}" preserveAspectRatio="xMidYMid meet" opacity="0.95"/>`
    : "";

  return `<g transform="translate(540 ${y})">
    ${iconMarkup}
    <text class="brand" x="${Math.round(34 * scale)}" y="0" font-size="${Math.round(43 * scale)}" text-anchor="middle" fill="${actors}">Actors <tspan fill="${alchemy}" font-style="italic">Alchemy</tspan></text>
  </g>`;
}

function logoMark(x, y, size, dark = false, opacity = 0.035) {
  if (!fs.existsSync(icon)) return "";
  return `<image href="${esc(icon)}" x="${x}" y="${y}" width="${size}" height="${Math.round(size * 1.48)}" opacity="${opacity}" preserveAspectRatio="xMidYMid meet"/>`;
}

function rightArrow({ x = 782, y = 900, width = 168, color = palette.rust }) {
  return `<g opacity="0.9">
    <line x1="${x}" y1="${y}" x2="${x + width}" y2="${y}" stroke="${palette.gold}" stroke-width="3" stroke-linecap="round" opacity="0.34"/>
    <line x1="${x}" y1="${y}" x2="${x + width}" y2="${y}" stroke="${color}" stroke-width="5" stroke-linecap="round"/>
    <path d="M${x + width - 28} ${y - 24} L${x + width} ${y} L${x + width - 28} ${y + 24}" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  </g>`;
}

function shell(slide) {
  const tone = toneRamp[slide.number - 1] || toneRamp.at(-1);
  const dark = tone.darkLogo;
  const bg = tone.bg;
  const wash = tone.wash;
  const primary = tone.primary;
  const muted = tone.muted;
  const accent = tone.accent;
  const bodyColor = slide.bodyColor || primary;
  const border = tone.border;
  const inner = tone.inner;
  const panel = tone.panel;
  const panelOpacity = tone.panelOpacity;
  const number = String(slide.number).padStart(2, "0");
  const headlineLines = Array.isArray(slide.title) ? slide.title : wrap(slide.title, slide.titleWrap || 18);
  const bodyLines = slide.body ? (Array.isArray(slide.body) ? slide.body : wrap(slide.body, slide.bodyWrap || 28)) : [];
  const leadLines = slide.lead ? (Array.isArray(slide.lead) ? slide.lead : wrap(slide.lead, slide.leadWrap || 27)) : [];
  const taglineLines = slide.tagline ? (Array.isArray(slide.tagline) ? slide.tagline : wrap(slide.tagline, slide.taglineWrap || 30)) : [];
  const supportLines = slide.support ? (Array.isArray(slide.support) ? slide.support : wrap(slide.support, slide.supportWrap || 52)) : [];
  const detailLines = slide.detail ? (Array.isArray(slide.detail) ? slide.detail : wrap(slide.detail, slide.detailWrap || 38)) : [];
  const sideX = slide.number % 2 === 0 ? 205 : 875;
  const watermarkX = slide.watermarkX ?? (slide.number % 2 === 0 ? 642 : 44);
  const watermarkY = slide.watermarkY ?? (slide.number === 1 ? 444 : 510);
  const watermarkSize = slide.watermarkSize ?? 310;
  const textY = slide.textY || (slide.kicker ? (headlineLines.length > 1 ? 378 : 430) : (headlineLines.length > 1 ? 388 : 420));
  const titleSize = slide.titleSize || (headlineLines.length > 2 ? 64 : headlineLines.length > 1 ? 78 : 90);
  const bodyOffset = slide.bullets?.length ? 12 : 46;
  const bodyY = textY + headlineLines.length * (titleSize * 0.9) + bodyOffset;
  const bodySize = slide.bodySize || 29;
  const bodyLineHeight = slide.bodyLineHeight || 38;
  const leadSize = slide.leadSize || 30;
  const leadLineHeight = slide.leadLineHeight || 38;
  const supportSize = slide.supportSize || 22;
  const supportLineHeight = slide.supportLineHeight || 28;
  const hasPanelContent = !slide.hidePanel && (leadLines.length || bodyLines.length || detailLines.length);
  const panelHeight = leadLines.length
    ? Math.max(250, 60 + leadLines.length * leadLineHeight + 20 + supportLines.length * supportLineHeight + 50)
    : detailLines.length
      ? 286
      : Math.max(214, 52 + bodyLines.length * bodyLineHeight + 42);
  const bulletStartY = bodyY + panelHeight + 42;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  <defs>
    <filter id="paper">
      <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="4" seed="${slide.number + 90}"/>
      <feColorMatrix values="0 0 0 0 0.12 0 0 0 0 0.10 0 0 0 0 0.08 0 0 0 0.07 0"/>
    </filter>
    <linearGradient id="goldLine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="${palette.gold}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="${palette.gold}" stop-opacity="0.82"/>
      <stop offset="1" stop-color="${palette.gold}" stop-opacity="0"/>
    </linearGradient>
    <style>
      .brand, .heading { font-family: Georgia, "Times New Roman", serif; letter-spacing: 0; }
      .note { font-family: Georgia, "Times New Roman", serif; font-style: italic; font-weight: 500; letter-spacing: 0; }
      .body { font-family: "DM Sans", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; letter-spacing: 0; }
      .eyebrow { font-family: "DM Sans", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; font-weight: 700; letter-spacing: 4px; }
    </style>
  </defs>

  <rect width="1080" height="1080" fill="${bg}"/>
  <rect width="1080" height="1080" fill="${wash}" opacity="${dark ? 0.18 : 0.28}" filter="url(#paper)"/>
  <circle cx="124" cy="170" r="250" fill="${tone.circle}" opacity="${dark ? 0.16 : 0.13}"/>
  <circle cx="918" cy="880" r="310" fill="${tone.circle}" opacity="${dark ? 0.18 : 0.13}"/>
  <path d="M${sideX} 172 C${sideX - 34} 292 ${sideX + 36} 402 ${sideX} 530 C${sideX - 34} 654 ${sideX + 36} 770 ${sideX} 908" fill="none" stroke="${palette.gold}" stroke-width="2" stroke-opacity="${dark ? 0.62 : 0.5}"/>
  <path d="M${sideX + 38} 176 C${sideX + 4} 300 ${sideX + 60} 414 ${sideX + 32} 540 C${sideX - 2} 660 ${sideX + 58} 780 ${sideX + 30} 910" fill="none" stroke="${tone.curve}" stroke-width="1.5" stroke-opacity="${dark ? 0.48 : 0.72}"/>
  ${logoMark(watermarkX, watermarkY, watermarkSize, dark, tone.markOpacity)}

  <rect x="58" y="58" width="964" height="964" fill="none" stroke="${border}" stroke-width="2" opacity="${dark ? 0.72 : 1}"/>
  <rect x="88" y="88" width="904" height="904" fill="none" stroke="${inner}" stroke-opacity="${dark ? 0.46 : 0.38}" stroke-width="1"/>
  ${logo(126, slide.number === 1 ? 1 : 0.82, dark)}

  ${
    slide.kicker
      ? `<text class="eyebrow" x="540" y="246" font-size="21" fill="${accent}" text-anchor="middle">${esc(slide.kicker.toUpperCase())}</text>
  <line x1="328" y1="284" x2="752" y2="284" stroke="url(#goldLine)" stroke-width="3"/>`
      : ""
  }

  <g transform="translate(0 ${textY})">
    ${textLines(headlineLines, { x: 540, y: 0, size: titleSize, lineHeight: Math.round(titleSize * 0.92), cls: "heading", color: primary, weight: 500 })}
  </g>

  ${taglineLines.length ? textLines(taglineLines, { x: 540, y: slide.taglineY || 704, size: slide.taglineSize || 38, lineHeight: slide.taglineLineHeight || 48, cls: "note", color: bodyColor, italic: true, weight: 500 }) : ""}

  ${hasPanelContent ? `<g transform="translate(128 ${bodyY})">
    <rect width="824" height="${panelHeight}" fill="${panel}" fill-opacity="${slide.panelOpacity ?? 0.2}" stroke="${accent}" stroke-opacity="${dark ? 0.5 : 0.38}" stroke-width="1.5"/>
    ${
      leadLines.length
        ? `${textLines(leadLines, { x: 412, y: 68, size: leadSize, lineHeight: leadLineHeight, cls: "note", color: bodyColor, italic: true })}
    ${supportLines.length ? textLines(supportLines, { x: 412, y: 68 + leadLines.length * leadLineHeight + 24, size: supportSize, lineHeight: supportLineHeight, cls: "body", color: muted, weight: 700, opacity: 0.92 }) : ""}`
        : `<line x1="292" y1="33" x2="460" y2="33" stroke="${accent}" stroke-width="3" stroke-linecap="round" opacity="0.86"/>
    ${textLines(bodyLines, { x: 376, y: 68, size: bodySize, lineHeight: bodyLineHeight, cls: "body", color: bodyColor, weight: slide.bodyWeight || 600, opacity: 0.96 })}`
    }
    ${
      detailLines.length
        ? `<line x1="166" y1="${slide.detailRuleY || 166}" x2="586" y2="${slide.detailRuleY || 166}" stroke="url(#goldLine)" stroke-width="2"/>
    ${textLines(detailLines, { x: 376, y: slide.detailY || 204, size: slide.detailSize || 20, lineHeight: slide.detailLineHeight || 26, cls: "body", color: muted, weight: 500, opacity: dark ? 0.86 : 0.9 })}`
        : ""
    }
  </g>` : ""}

  ${slide.bullets?.length ? bulletGrid(slide.bullets, { x: 144, y: bulletStartY, columns: slide.bulletColumns || 2, columnWidth: slide.bulletColumnWidth || 410, rowHeight: slide.bulletRowHeight || 58, size: slide.bulletSize || 31, color: palette.rust }) : ""}

  ${slide.arrow ? rightArrow(slide.arrow) : ""}

  ${slide.footer ? `<text class="note" x="540" y="902" font-size="27" fill="${accent}" text-anchor="middle">${esc(slide.footer)}</text>` : ""}
  ${
    slide.showMeta === false
      ? ""
      : `<text class="body" x="116" y="964" font-size="18" fill="${muted}" opacity="0.88">Actors Alchemy</text>
  <text class="body" x="964" y="964" font-size="18" fill="${muted}" text-anchor="end" opacity="0.88">${slide.number}/${slides.length}</text>`
  }
</svg>`;
}

const slides = [
  {
    number: 1,
    title: "Drama School Workshops",
    titleSize: 96,
    textY: 348,
    tagline: ["Your bridge between", "training and the industry."],
    taglineY: 674,
    taglineSize: 40,
    taglineLineHeight: 52,
    bodyColor: palette.rust,
    watermarkX: 82,
    watermarkY: 590,
    watermarkSize: 200,
    arrow: { x: 776, y: 900, width: 174 },
    variant: "light",
  },
  {
    number: 2,
    kicker: "Workshop 01",
    title: "The Mock Audition",
    lead: "A simulated audition experience helping students understand the audition room, their place in it, their 32 bars and a movement combination.",
    leadWrap: 48,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 62,
    watermarkY: 622,
    watermarkSize: 190,
    bullets: ["audition practice", "panel etiquette", "redirection", "managing nerves", "breaking down text", "confidence"],
    showMeta: false,
    variant: "light",
  },
  {
    number: 3,
    kicker: "Workshop 02",
    title: "The Mindset Mentor",
    lead: "A workshop exploring nerves, pressure, self-trust and performance anxiety, helping students understand their own programming and build confidence.",
    leadWrap: 48,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 830,
    watermarkY: 620,
    watermarkSize: 190,
    bullets: ["grounding tools", "self-trust", "emotional regulation", "presence", "handling rejection", "building confidence"],
    showMeta: false,
    variant: "dark",
  },
  {
    number: 4,
    kicker: "Workshop 03",
    title: "The Company Code",
    lead: "A professional conduct workshop for performers entering rehearsal rooms, contracts and companies.",
    leadWrap: 38,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 70,
    watermarkY: 614,
    watermarkSize: 190,
    bullets: ["company etiquette", "communication", "Equity rates", "online scams", "networking", "self-promotion"],
    showMeta: false,
    variant: "light",
  },
  {
    number: 5,
    kicker: "Workshop 04",
    title: "Self-Tape Synthesis",
    lead: "A practical workshop on self-tapes as part of the audition process, covering tripod recording, cold reading and tape technique.",
    leadWrap: 48,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 828,
    watermarkY: 620,
    watermarkSize: 190,
    bullets: ["budget setup", "lighting", "sound & framing", "reader work", "cold reading", "preparation"],
    showMeta: false,
    variant: "dark",
  },
  {
    number: 6,
    kicker: "Workshop 05",
    title: ["Ship Shape:", "Cruise 101"],
    titleSize: 80,
    lead: "A practical introduction to cruise auditions and life inside the contract, tailored towards singers and dancers.",
    leadWrap: 46,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 64,
    watermarkY: 620,
    watermarkSize: 190,
    bullets: ["performance quality", "recall material", "visa & travel", "life on board", "working with movement", "exploring rehearsals"],
    showMeta: false,
    variant: "light",
  },
  {
    number: 7,
    kicker: "Add-on or standalone",
    title: "The Q&A",
    lead: "A flexible conversation connected to any workshop, giving students space to ask honest questions about the industry and life after training.",
    leadWrap: 48,
    leadSize: 31,
    leadLineHeight: 38,
    bodyColor: palette.rust,
    watermarkX: 830,
    watermarkY: 620,
    watermarkSize: 190,
    bullets: ["casting", "auditions", "agents", "contracts", "relationships", "life after training"],
    showMeta: false,
    variant: "dark",
  },
];

for (const slide of slides) {
  const svg = shell(slide);
  fs.writeFileSync(path.join(outDir, `actors-alchemy-workshops-${String(slide.number).padStart(2, "0")}.svg`), svg, "utf8");
}

const proofImages = slides
  .map((slide, index) => {
    const col = index % 4;
    const row = Math.floor(index / 4);
    return `<image href="actors-alchemy-workshops-${String(slide.number).padStart(2, "0")}.svg" x="${col * 360}" y="${row * 360}" width="360" height="360"/>`;
  })
  .join("\n");

fs.writeFileSync(
  path.join(outDir, "actors-alchemy-workshops-proof-sheet.svg"),
  `<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="720" viewBox="0 0 1440 720">
    <rect width="1440" height="720" fill="${palette.warm}"/>
    ${proofImages}
  </svg>`,
  "utf8",
);

console.log(`Created ${slides.length} Actors Alchemy workshop slides in ${outDir}`);

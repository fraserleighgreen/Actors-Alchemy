const fs = require('fs');
const path = require('path');

const root = __dirname;
const outputDir = path.join(root, 'coaching-options-carousel');
const uploadDir = path.join(outputDir, 'instagram-upload');
const logoPath = path.join(root, '..', 'assets', 'actors-alchemy-logo-wordmark.png');
const iconPath = path.join(root, '..', 'assets', 'actors-alchemy-icon.svg');
const sharp = require('/Users/fraserleighgreen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

fs.mkdirSync(outputDir, { recursive: true });
fs.mkdirSync(uploadDir, { recursive: true });

const logoData = `data:image/png;base64,${fs.readFileSync(logoPath).toString('base64')}`;
const iconData = `data:image/svg+xml;base64,${fs.readFileSync(iconPath).toString('base64')}`;

const palette = {
  oat: '#efe6d7',
  oatLight: '#f8f3eb',
  oatDeep: '#e8ddce',
  line: '#d4c4af',
  charcoal: '#3c3832',
  taupe: '#75675b',
  rust: '#9d693d',
  rustDeep: '#7e4d2c',
  gold: '#d6b16a',
  red: '#a34a3d',
};

const slides = [
  {
    file: '01-coaching-and-support',
    label: 'Cover',
    cover: true,
  },
  {
    file: '02-career-check-in',
    label: 'Career Check-In',
    number: '01',
    eyebrow: 'COMPLIMENTARY STARTING POINT',
    title: 'Career Check-In',
    price: 'Complimentary',
    duration: '20 minutes',
    description: ['A dedicated space to define your goals', 'and decide your next move.'],
    detail: 'Clarity first. No cost. No pressure.',
    accent: palette.gold,
  },
  {
    file: '03-standard-session',
    label: 'Standard One-to-One Session',
    number: '02',
    eyebrow: 'PERSONALISED ONE-TO-ONE COACHING',
    title: 'Standard Session',
    price: '£50',
    duration: '60 minutes',
    description: ['Explore your craft, strengthen the work', 'and keep growing.'],
    detail: 'Self-tapes · auditions · scene work · acting through song',
    accent: palette.rust,
  },
  {
    file: '04-priority-coaching',
    label: 'Priority Coaching',
    number: '03',
    eyebrow: 'LAST-MINUTE AUDITION SUPPORT',
    title: 'Priority Coaching',
    price: '£65',
    duration: '60 minutes',
    description: ['Refine a self-tape or prepare for an', 'in-person audition with focused support.'],
    detail: 'Where preparation meets confidence.',
    accent: palette.red,
  },
  {
    file: '05-spotlight-surgery',
    label: 'Spotlight Surgery',
    number: '04',
    eyebrow: 'YOUR INDUSTRY PROFILE, REFINED',
    title: 'Spotlight Surgery',
    price: '£35',
    duration: '35 minutes',
    description: ['Understand how you are being seen and', 'present your unique talents at their best.'],
    detail: 'Headshots · showreel · credits · skills',
    accent: palette.rust,
  },
];

function defs() {
  return `<defs>
    <filter id="paper">
      <feTurbulence type="fractalNoise" baseFrequency="0.016" numOctaves="3" seed="114"/>
      <feColorMatrix values="0 0 0 0 0.16 0 0 0 0 0.13 0 0 0 0 0.10 0 0 0 0.028 0"/>
    </filter>
    <style>
      .heading { font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif; font-weight: 500; }
      .body { font-family: "DM Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; }
      .eyebrow { font-family: "DM Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; font-weight: 700; letter-spacing: 3px; }
    </style>
  </defs>`;
}

function ground() {
  return `<rect width="1080" height="1080" fill="${palette.oat}"/>
  <rect width="1080" height="1080" fill="${palette.oatDeep}" opacity="0.14" filter="url(#paper)"/>`;
}

function logo(width = 405, y = 61) {
  return `<image href="${logoData}" x="${(1080 - width) / 2}" y="${y}" width="${width}" height="${width * 0.217}" preserveAspectRatio="xMidYMid meet"/>`;
}

function coverSvg() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  ${defs()}
  ${ground()}
  ${logo(437, 72)}
  <image href="${iconData}" x="724" y="692" width="270" height="287" opacity="0.10" preserveAspectRatio="xMidYMid meet"/>
  <line x1="386" y1="286" x2="424" y2="286" stroke="${palette.rust}" stroke-width="1.5"/>
  <text class="eyebrow" x="444" y="293" font-size="20" fill="${palette.rust}">COACHING &amp; SUPPORT</text>
  <text class="heading" x="540" y="449" font-size="101" fill="${palette.charcoal}" text-anchor="middle">Support for</text>
  <text class="heading" x="540" y="548" font-size="101" fill="${palette.charcoal}" text-anchor="middle">your next move.</text>
  <text class="heading" x="540" y="642" font-size="36" font-style="italic" fill="${palette.rust}" text-anchor="middle">Personalised support, from complimentary to £65.</text>
  <text class="eyebrow" x="540" y="866" font-size="20" fill="${palette.rust}" text-anchor="middle">SWIPE TO FIND YOUR SESSION  →</text>
</svg>`;
}

function optionSvg(slide, index) {
  const page = String(index + 1).padStart(2, '0');
  const priceSize = slide.price.length > 8 ? 78 : 102;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  ${defs()}
  ${ground()}
  ${logo(375, 48)}
  <text class="body" x="1008" y="84" font-size="17" fill="${palette.taupe}" text-anchor="end">${page} / 05</text>
  <rect x="108" y="193" width="864" height="735" fill="${palette.oatLight}" fill-opacity="0.38" stroke="${palette.line}" stroke-width="1.5"/>
  <rect x="108" y="193" width="864" height="11" fill="${slide.accent}"/>
  <text class="eyebrow" x="540" y="282" font-size="19" fill="${palette.rust}" text-anchor="middle">${slide.eyebrow}</text>
  <text class="heading" x="896" y="330" font-size="54" fill="${slide.accent}" text-anchor="end">${slide.number}</text>
  <text class="heading" x="540" y="424" font-size="75" fill="${palette.charcoal}" text-anchor="middle">${slide.title}</text>
  <line x1="180" y1="474" x2="900" y2="474" stroke="${palette.line}"/>
  <text class="heading" x="540" y="603" font-size="${priceSize}" fill="${palette.charcoal}" text-anchor="middle">${slide.price}</text>
  <text class="eyebrow" x="540" y="654" font-size="20" fill="${palette.rust}" text-anchor="middle">${slide.duration.toUpperCase()}</text>
  <text class="body" x="540" y="742" font-size="33" font-weight="700" fill="${palette.rustDeep}" text-anchor="middle">${slide.description.map((line, lineIndex) => `<tspan x="540" dy="${lineIndex === 0 ? 0 : 43}">${line}</tspan>`).join('')}</text>
  <rect x="220" y="832" width="640" height="58" fill="${palette.oatDeep}"/>
  <text class="body" x="540" y="869" font-size="23" font-weight="700" fill="${palette.rustDeep}" text-anchor="middle">${slide.detail}</text>
</svg>`;
}

function previewHtml() {
  const cards = slides.map((slide, index) => {
    const page = String(index + 1).padStart(2, '0');
    return `    <a href="${slide.file}.png?v=20260819-1"><img src="${slide.file}.png?v=20260819-1" alt="${slide.label}"><span>${page} · ${slide.label}</span></a>`;
  }).join('\n');

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Actors Alchemy Coaching Carousel</title>
  <style>
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #28241f; color: #f8f3eb; font-family: "DM Sans", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif; }
    header { position: sticky; top: 0; z-index: 2; padding: 18px 22px; border-bottom: 1px solid rgba(248,243,235,.14); background: rgba(40,36,31,.96); }
    h1 { margin: 0; font-family: Georgia, serif; font-size: 22px; font-weight: 500; }
    p { margin: 5px 0 0; color: rgba(248,243,235,.68); font-size: 13px; }
    main { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; padding: 20px; }
    a { display: block; overflow: hidden; border: 1px solid rgba(214,177,106,.42); background: #f8f3eb; color: inherit; text-decoration: none; transition: border-color 180ms ease, transform 180ms ease; }
    a:hover, a:focus-visible { border-color: #d6b16a; transform: translateY(-2px); outline: none; }
    img { display: block; width: 100%; height: auto; }
    span { display: block; padding: 10px 12px; background: #7e4d2c; font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
  </style>
</head>
<body>
  <header><h1>Coaching &amp; Support carousel</h1><p>Click any slide to open it full-size.</p></header>
  <main>
${cards}
  </main>
</body>
</html>`;
}

async function build() {
  const images = [];
  for (let index = 0; index < slides.length; index += 1) {
    const slide = slides[index];
    const svg = slide.cover ? coverSvg() : optionSvg(slide, index);
    const svgPath = path.join(outputDir, `${slide.file}.svg`);
    const pngPath = path.join(outputDir, `${slide.file}.png`);
    const uploadPath = path.join(uploadDir, `${slide.file}.png`);
    fs.writeFileSync(svgPath, svg);
    await sharp(Buffer.from(svg)).png({ compressionLevel: 9, quality: 100 }).toFile(pngPath);
    fs.copyFileSync(pngPath, uploadPath);
    images.push({ input: await sharp(pngPath).resize(540, 540).toBuffer(), left: (index % 3) * 540, top: Math.floor(index / 3) * 540 });
  }

  const contactSheet = sharp({ create: { width: 1620, height: 1080, channels: 4, background: '#28241f' } });
  await contactSheet.composite(images.map((item) => ({
    input: item.input,
    left: item.left,
    top: item.top,
    blend: 'over',
    tile: false,
  }))).png().toFile(path.join(outputDir, 'coaching-options-contact-sheet.png'));

  fs.writeFileSync(path.join(outputDir, 'carousel-preview.html'), previewHtml());
  fs.writeFileSync(path.join(uploadDir, 'README.txt'), 'Instagram carousel: upload the five PNG files in numerical order. Each image is 1080 × 1080 pixels.\n');
  console.log(`Created ${slides.length} Instagram-ready slides in ${outputDir}`);
}

build().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});

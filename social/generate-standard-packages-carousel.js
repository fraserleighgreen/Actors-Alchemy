const fs = require('fs');
const path = require('path');

const root = __dirname;
const outputDir = path.join(root, 'standard-packages-carousel');
const logo = path.join(root, '..', 'assets', 'actors-alchemy-logo-wordmark.png');
const icon = path.join(root, '..', 'assets', 'actors-alchemy-icon.svg');

fs.mkdirSync(outputDir, { recursive: true });

const packages = [
  { sessions: '03', name: 'Three', count: 3, usual: '£150', rate: '£145', perSession: '£48.33', saving: 'Save £5', savingWidth: 150, metal: '#a85f39', descriptionLines: ['An accessible place to begin'] },
  { sessions: '05', name: 'Five', count: 5, usual: '£250', rate: '£225', perSession: '£45', saving: 'Save £25', savingWidth: 170, metal: 'url(#silver)', descriptionLines: ['Define your trajectory. Set goals.', 'Achieve. Repeat.'] },
  { sessions: '10', name: 'Ten', count: 10, usual: '£500', rate: '£430', perSession: '£43', saving: 'Save £70', savingWidth: 170, metal: '#b18432', descriptionLines: ['For clients committed to', 'continuous development.'] },
];

function defs() {
  return `
  <defs>
    <filter id="paper">
      <feTurbulence type="fractalNoise" baseFrequency="0.016" numOctaves="3" seed="114"/>
      <feColorMatrix values="0 0 0 0 0.16 0 0 0 0 0.13 0 0 0 0 0.10 0 0 0 0.028 0"/>
    </filter>
    <linearGradient id="silver" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#5f5b57"/><stop offset="0.30" stop-color="#aaa6a0"/><stop offset="0.48" stop-color="#f4efe7"/><stop offset="0.62" stop-color="#b8b4ae"/><stop offset="1" stop-color="#68645f"/>
    </linearGradient>
    <style>
      .heading { font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif; font-weight: 500; }
      .body { font-family: "DM Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; }
      .eyebrow { font-family: "DM Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; font-weight: 700; letter-spacing: 3px; }
    </style>
  </defs>`;
}

function ground() {
  return `
  <rect width="1080" height="1080" fill="#efe6d7"/>
  <rect width="1080" height="1080" fill="#e8ddce" opacity="0.14" filter="url(#paper)"/>`;
}

const cover = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  ${defs()}
  ${ground()}
  <image href="${logo}" x="321.5" y="71.85" width="437" height="94.3" preserveAspectRatio="xMidYMid meet"/>
  <image href="${icon}" x="710" y="650" width="320" height="340" opacity="0.11" preserveAspectRatio="xMidYMid meet"/>
  <line x1="411" y1="282" x2="449" y2="282" stroke="#9d693d" stroke-width="1.5"/>
  <text class="eyebrow" x="469" y="289" font-size="20" fill="#9d693d">OUR PACKAGES</text>
  <text class="heading" x="540" y="432" font-size="104" fill="#3c3832" text-anchor="middle">Development</text>
  <text class="heading" x="540" y="535" font-size="104" fill="#3c3832" text-anchor="middle">Packages</text>
  <text class="heading" x="540" y="625" font-size="38" font-style="italic" fill="#9d693d" text-anchor="middle">Personalised toward your goals.</text>
  <text class="eyebrow" x="540" y="855" font-size="20" fill="#9d693d" text-anchor="middle">SWIPE TO VIEW PACKAGES  →</text>
</svg>`;

fs.writeFileSync(path.join(outputDir, 'actors-alchemy-packages-01.svg'), cover);

packages.forEach((item, index) => {
  const slideNumber = String(index + 2).padStart(2, '0');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
  ${defs()}
  ${ground()}
  <image href="${logo}" x="72" y="43.1" width="345" height="74.75" preserveAspectRatio="xMinYMid meet"/>
  <text class="body" x="1008" y="88" font-size="17" fill="#75675b" text-anchor="end">${slideNumber} / 04</text>
  <line x1="72" y1="168" x2="110" y2="168" stroke="#9d693d" stroke-width="1.5"/>
  <text class="eyebrow" x="130" y="175" font-size="19" fill="#9d693d">DEVELOPMENT PACKAGE</text>

  <rect x="112" y="235" width="856" height="620" fill="#efe6d7" fill-opacity="0.90" stroke="${item.count === 5 ? '#9d693d' : '#d4c4af'}" stroke-width="${item.count === 5 ? '2.5' : '1.5'}"/>
  <line x1="176" y1="320" x2="214" y2="320" stroke="#9d693d" stroke-width="1.5"/>
  <text class="eyebrow" x="234" y="327" font-size="20" fill="#9d693d">GOLD #${item.count}</text>
  <text class="heading" x="890" y="360" font-size="62" fill="${item.metal}" text-anchor="end">${item.sessions}</text>
  <text class="heading" x="176" y="445" font-size="72" fill="#3c3832">${item.name} Sessions</text>
  <line x1="176" y1="490" x2="904" y2="490" stroke="#d4c4af"/>

  <text class="heading" x="176" y="620" font-size="88" fill="#3c3832">${item.rate}</text>
  <text class="body" x="176" y="676" font-size="32" font-weight="700" fill="#7e4d2c">${item.descriptionLines.map((line, lineIndex) => `<tspan x="176" dy="${lineIndex === 0 ? 0 : 42}">${line}</tspan>`).join('')}</text>
  <rect x="176" y="${item.descriptionLines.length === 1 ? 706 : 749}" width="${item.savingWidth}" height="52" fill="#e8ddce"/>
  <text class="body" x="${176 + item.savingWidth / 2}" y="${item.descriptionLines.length === 1 ? 740 : 783}" font-size="25" font-weight="700" fill="#7e4d2c" text-anchor="middle">${item.saving}</text>
</svg>`;
  fs.writeFileSync(path.join(outputDir, `actors-alchemy-packages-${slideNumber}.svg`), svg);
});

console.log(`Created ${packages.length + 1} carousel slides in ${outputDir}`);

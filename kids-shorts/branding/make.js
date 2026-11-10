// Render channel branding PNGs: node branding/make.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  for (const [kind, w, h, transparent] of [['avatar', 800, 800], ['banner', 2560, 1440], ['watermark', 300, 300, true]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.resolve(__dirname, 'brand.html'));
    await p.evaluate(k => window.make(k), kind);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(__dirname, `${kind}.png`), omitBackground: !!transparent });
  }
  await b.close();
})();

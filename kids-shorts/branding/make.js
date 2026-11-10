const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); 
  for (const [kind, w, h] of [['avatar', 800, 800], ['banner', 2560, 1440]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.resolve(__dirname, 'brand.html'));
    await p.evaluate(k => window.make(k), kind); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(__dirname, `${kind}.png`) });
  }
  await b.close();
})();

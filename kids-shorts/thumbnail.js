// Episode thumbnails (1280x720 JPEG) for YouTube.
// Usage: node thumbnail.js <episode.json> <out.jpg>
const { chromium } = require('playwright');
const path = require('path');

// "ABC Adventures: Letters K to O" -> headline "ABC Adventures", sub "Letters K to O"
function thumbText(ep) {
  const m = ep.title.match(/^(.*?[!?:])\s*(.*)$/);
  const head = (m ? m[1] : ep.title).replace(/:$/, '').trim();
  const sub = (m && m[2]) || (ep.learn || []).slice(0, 2).join(' • ');
  return { head, sub };
}

async function renderThumbnail(ep, out, browser) {
  const own = !browser;
  browser = browser || await require('playwright').chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const { head, sub } = thumbText(ep);
  const hue = [...ep.id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 7);
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto('file://' + path.join(__dirname, 'scenes', 'thumbnail.html') + `?title=${encodeURIComponent(head)}&sub=${encodeURIComponent(sub)}&hue=${hue}`);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out, type: 'jpeg', quality: 90 });
  await page.close(); if (own) await browser.close();
  return out;
}

module.exports = { renderThumbnail, thumbText };

if (require.main === module) {
  const [epFile, out] = process.argv.slice(2);
  renderThumbnail(require(path.resolve(epFile)), out).then(o => console.log('wrote', o)).catch(e => { console.error(e); process.exit(1); });
}

// Render one topic of an HTML scene (window.setup(id), window.render(t), window.DURATION) to an MP4 Short.
// Usage: node render.js <scene.html> <topicId> <out.mp4> [--audio a.wav] [--preview] [--fps 30]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

async function renderTopic({ scene, topic, out, audio, fps = 30, preview = false, browser }) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const own = !browser;
  browser = browser || await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(scene) + '?topic=' + encodeURIComponent(topic));
  await page.evaluate(() => document.fonts.ready);
  const timeline = await page.evaluate(() => window.TIMELINE);
  const duration = await page.evaluate(() => window.DURATION);

  if (preview) {
    const shots = [];
    for (const t of [4, 7.6, 10.5, 18.5]) {
      await page.evaluate(x => window.render(x), t);
      const p = out.replace(/\.mp4$/, `-${t}s.png`);
      await page.screenshot({ path: p });
      shots.push(p);
    }
    await page.close(); if (own) await browser.close();
    return { timeline, shots };
  }

  const ff = spawn('ffmpeg', [
    '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    ...(audio ? ['-i', audio] : []),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    ...(audio ? ['-c:a', 'aac', '-b:a', '192k', '-shortest'] : []),
    out,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(duration * fps);
  for (let i = 0; i < frames; i++) {
    await page.evaluate(x => window.render(x), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  const code = await new Promise(r => ff.on('close', r));
  await page.close(); if (own) await browser.close();
  if (code !== 0) throw new Error('ffmpeg failed for ' + topic);
  return { timeline };
}

async function getTimeline(scene, topic, browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(scene) + '?topic=' + encodeURIComponent(topic));
  const tl = await page.evaluate(() => window.TIMELINE);
  await page.close();
  return tl;
}

module.exports = { renderTopic, getTimeline };

if (require.main === module) {
  const a = process.argv.slice(2);
  const flag = n => a.includes(n) ? a[a.indexOf(n) + 1] : undefined;
  const [scene, topic, out] = a.filter((x, i) => !x.startsWith('--') && !(i > 0 && a[i - 1].startsWith('--') && a[i - 1] !== '--preview'));
  renderTopic({ scene, topic, out, audio: flag('--audio'), fps: Number(flag('--fps')) || 30, preview: a.includes('--preview') })
    .then(r => console.log(JSON.stringify(r)));
}

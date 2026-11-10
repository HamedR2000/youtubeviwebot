// Render an HTML scene (exposing window.render(t) and window.DURATION) to an MP4 Short.
// Usage: node render.js scenes/draw-circle.html out/draw-circle.mp4 [audio.wav] [--fps 30] [--preview]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const args = process.argv.slice(2);
  const [scene, outFile, audio] = args.filter(a => !a.startsWith('--') && !/^\d+$/.test(a));
  const fps = Number(args[args.indexOf('--fps') + 1]) || 30;
  const preview = args.includes('--preview');
  fs.mkdirSync(path.dirname(outFile), { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.resolve(scene));
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.DURATION);

  if (preview) { // a few stills for quick review
    for (const t of [1, 4, 7.6, 10.5, 15.8, 18.5]) {
      await page.evaluate(x => window.render(x), t);
      await page.screenshot({ path: outFile.replace(/\.mp4$/, `-${t}s.png`) });
    }
    await browser.close();
    return;
  }

  const ff = spawn('ffmpeg', [
    '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    ...(audio ? ['-i', audio] : []),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    ...(audio ? ['-c:a', 'aac', '-b:a', '192k', '-shortest'] : []),
    outFile,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  const frames = Math.round(duration * fps);
  for (let i = 0; i < frames; i++) {
    await page.evaluate(x => window.render(x), i / fps);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stderr.write(`frame ${i}/${frames}\r`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('\nwrote', outFile);
})();

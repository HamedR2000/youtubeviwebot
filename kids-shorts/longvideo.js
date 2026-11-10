// Build a long (16:9) episode: voices + music + timeline, then render frames and mux.
// Usage: node longvideo.js episodes/01-birthday.json out/ep.mp4 [--preview t1,t2,...] [--fps 30]
// Needs KOKORO_DIR (narration model) like daily.js.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

async function buildEpisode(episodeFile, outFile, { fps = 30, preview = null, browser = null } = {}) {
  const work = outFile.replace(/\.mp4$/, '') + '.work';
  fs.mkdirSync(work, { recursive: true });
  execFileSync('python3', [path.join(__dirname, 'audio', 'episode_audio.py'), episodeFile, work], { stdio: 'inherit' });
  const timeline = JSON.parse(fs.readFileSync(path.join(work, 'timeline.json'), 'utf8'));

  const own = !browser;
  browser = browser || await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'scenes', 'episode.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(tl => window.setup(tl), timeline);

  if (preview) {
    for (const t of preview) {
      await page.evaluate(x => window.render(x), t);
      await page.screenshot({ path: outFile.replace(/\.mp4$/, `-${t}s.png`) });
    }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-i', path.join(work, 'audio.wav'), '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p',
      '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '192k', '-shortest', outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
    const frames = Math.round(timeline.duration * fps);
    for (let i = 0; i < frames; i++) {
      await page.evaluate(x => window.render(x), i / fps);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 900 === 0) console.log(`  frame ${i}/${frames}`);
    }
    ff.stdin.end();
    const code = await new Promise(r => ff.on('close', r));
    if (code !== 0) throw new Error('ffmpeg failed');
  }
  await page.close(); if (own) await browser.close();
  return timeline;
}

module.exports = { buildEpisode };

if (require.main === module) {
  const a = process.argv.slice(2);
  const pv = a.includes('--preview') ? a[a.indexOf('--preview') + 1].split(',').map(Number) : null;
  buildEpisode(a[0], a[1], { preview: pv }).then(tl => console.log(`done: ${tl.title} (${tl.duration.toFixed(1)}s)`)).catch(e => { console.error(e); process.exit(1); });
}

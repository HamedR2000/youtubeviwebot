// End card: render scenes/outro.html once per orientation and append it to finished videos.
// Usage (test): node outro.js <portrait|landscape> <out.mp4> [--preview t1,t2,...]
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const SIZE = { portrait: [1080, 1920], landscape: [1920, 1080] };

async function renderOutro(orientation, out, { fps = 30, preview = null, browser = null } = {}) {
  const [w, h] = SIZE[orientation];
  const own = !browser;
  browser = browser || await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  await page.goto('file://' + path.join(__dirname, 'scenes', 'outro.html') + '?topic=' + orientation);
  await page.evaluate(() => document.fonts.ready);
  const duration = await page.evaluate(() => window.DURATION);
  try {
    if (preview) {
      for (const t of preview) {
        await page.evaluate(x => window.render(x), t);
        await page.screenshot({ path: out.replace(/\.mp4$/, `-${t}s.png`) });
      }
      return;
    }
    const wav = out.replace(/\.mp4$/, '.wav');
    execFileSync('python3', [path.join(__dirname, 'audio', 'outro_audio.py'), wav, String(duration)], { stdio: 'inherit' });
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
      '-ar', '44100', '-ac', '2', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < Math.round(duration * fps); i++) {
      await page.evaluate(x => window.render(x), i / fps);
      if (!ff.stdin.write(await page.screenshot({ type: 'png' }))) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    if (await new Promise(r => ff.on('close', r)) !== 0) throw new Error('ffmpeg failed for outro');
    fs.rmSync(wav);
  } finally {
    await page.close(); if (own) await browser.close();
  }
}

// video + outro -> video (in place). Re-encodes so both parts share one stream layout.
function appendOutro(video, outro) {
  const tmp = video.replace(/\.mp4$/, '.with-outro.mp4');
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', video, '-i', outro, '-filter_complex',
    '[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]fps=30,format=yuv420p,setsar=1[v1];' +
    '[0:a]aresample=44100,aformat=channel_layouts=stereo[a0];[1:a]aresample=44100,aformat=channel_layouts=stereo[a1];' +
    '[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]',
    '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', tmp], { stdio: 'inherit' });
  fs.renameSync(tmp, video);
}

module.exports = { renderOutro, appendOutro };

if (require.main === module) {
  const a = process.argv.slice(2);
  const pv = a.includes('--preview') ? a[a.indexOf('--preview') + 1].split(',').map(Number) : null;
  renderOutro(a[0], a[1], { preview: pv }).then(() => console.log('done')).catch(e => { console.error(e); process.exit(1); });
}

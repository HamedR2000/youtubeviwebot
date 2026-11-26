// Bedtime video (16:9, ~30 min) for the evening slot: "Good night, cow… good night, train…" with a calm narrator over a
// music-box lullaby, then the Doodle Pals asleep under a starry sky while the lullaby plays on. Published at 17:00 Berlin.
const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const TOPICS = require('./topics');

const FPS = 24, INTRO = 16, SEG = 20, OUTRO = 24, LOOP = 60;
const PHRASES = ['Sleep tight.', 'Sweet dreams.', 'Close your eyes.', 'Time to rest.', 'Snuggle up.', 'Night night.'];
const cap = w => w.toLowerCase().replace(/\b[a-z]/g, c => c.toUpperCase());

function pickSubjects(used, n = 8) {
  const pool = TOPICS.filter(t => ['animal', 'vehicle'].includes(t.template));
  const fresh = pool.filter(t => !used['bed:' + t.id]);
  const list = fresh.length >= n ? fresh : pool; // once everything was used, start over
  const an = list.filter(t => t.template === 'animal'), ve = list.filter(t => t.template === 'vehicle');
  const out = [];
  while (out.length < n && (an.length || ve.length)) { // mostly animals, a vehicle every third
    const src = out.length % 3 === 2 && ve.length ? ve : an.length ? an : ve;
    out.push(src.shift());
  }
  return out;
}

async function renderClip(browser, opts, seconds, out) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'scenes', 'bedtime.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(o => window.setup(o), opts);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-g', String(FPS * 4), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < Math.round(seconds * FPS); i++) {
    await page.evaluate(x => window.render(x), i / FPS + (opts.t0 || 0));
    if (!ff.stdin.write(await page.screenshot({ type: 'png' }))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  if (await new Promise(r => ff.on('close', r)) !== 0) throw new Error('ffmpeg failed: ' + out);
  await page.close();
}

async function buildBedtime({ used, DATE, OUT, browser, minutes = 14 }) {
  const subjects = pickSubjects(used);
  const id = `bedtime-${DATE}`, work = path.resolve(OUT, id + '.work'); // absolute: the concat list resolves paths itself
  fs.mkdirSync(work, { recursive: true });
  const total = minutes * 60;
  const names = subjects.map(t => t.word.toLowerCase());

  // what is said, and when
  const lines = [{ t: 2, text: "The sun has gone to sleep. The moon is up in the sky. It's time for bed, little one." }];
  subjects.forEach((t, i) => lines.push({ t: INTRO + i * SEG + 2, text: `Good night, ${names[i]}. ${PHRASES[i % PHRASES.length]}` }));
  const o0 = INTRO + subjects.length * SEG;
  lines.push({ t: o0 + 2, text: 'Good night, Penny. Good night, Ellie. Good night, Coco.' });
  lines.push({ t: o0 + 12, text: 'Good night, little one. Sweet dreams.' });

  // pictures: intro sky, one clip per friend, the pals saying good night, then a long loop of the pals asleep
  const clips = [];
  const clip = async (name, opts, secs) => { const f = path.join(work, name + '.mp4'); await renderClip(browser, opts, secs, f); clips.push([f, secs]); return f; };
  await clip('intro', { seed: 3, text: "It's time for bed…" }, INTRO);
  for (const [i, t] of subjects.entries()) { await clip(`s${i}`, { seed: 5 + i, subject: t.id, text: `Good night, ${names[i]}.` }, SEG); console.log(`  [bedtime] ${t.id}`); }
  await clip('outro', { seed: 2, pals: true, text: 'Good night, Doodle Pals.' }, OUTRO);
  const loop = path.join(work, 'loop.mp4'); await renderClip(browser, { seed: 9, pals: true, text: '', t0: 30 }, LOOP, loop);
  let at = clips.reduce((a, c) => a + c[1], 0);
  while (at < total) { clips.push([loop, LOOP]); at += LOOP; }
  fs.writeFileSync(path.join(work, 'list.txt'), clips.map(([f]) => `file '${f}'`).join('\n'));

  const wav = path.join(work, 'audio.wav'), linesFile = path.join(work, 'lines.json');
  fs.writeFileSync(linesFile, JSON.stringify(lines));
  const seed = [...DATE].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 9973, 7);
  execFileSync('python3', [path.join(__dirname, 'audio', 'bedtime_audio.py'), wav, String(total), linesFile, String(seed)], { stdio: 'inherit' });
  const out = path.join(OUT, `${id}.mp4`);
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(work, 'list.txt'), '-i', wav,
    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-ac', '2', '-t', String(total), '-movflags', '+faststart', out], { stdio: 'inherit' });
  const subs = JSON.parse(fs.readFileSync(wav + '.subs.json', 'utf8'));
  fs.rmSync(work, { recursive: true, force: true });

  const who = subjects.slice(0, 3).map(t => cap(t.word));
  const title = `Good Night ${who.join(', ')} and Friends 🌙 ${minutes} Min Bedtime Lullaby for Babies and Toddlers`.slice(0, 100);
  return {
    subjects: subjects.map(t => t.id), subs,
    video: {
      id, file: path.basename(out), long: true, schedule: '17:00', title,
      description: [
        `A calm bedtime video 🌙 Say good night to ${names.slice(0, -1).join(', ')} and ${names[names.length - 1]} with the Doodle Pals, then drift off to a gentle music-box lullaby under the stars ✨`,
        '',
        `0:00 It's time for bed`, `0:${String(INTRO).padStart(2, '0')} Good night, friends`, `${Math.floor(o0 / 60)}:${String(o0 % 60).padStart(2, '0')} Good night, Doodle Pals`,
        `${Math.floor((o0 + OUTRO) / 60)}:${String((o0 + OUTRO) % 60).padStart(2, '0')} Lullaby music`,
        '',
        `${minutes} minutes of soft, slow music for babies and toddlers — for bedtime, nap time and quiet time.`,
        '',
        '#lullaby #bedtime #babysleepmusic #lullabiesforbabies #goodnight #sleepmusic #toddlers #kids #doodlepals',
      ].join('\n'),
      tags: ['lullaby', 'bedtime lullaby', 'baby sleep music', 'lullabies for babies', 'bedtime songs', 'good night', 'sleep music for kids',
        'music box lullaby', 'nap time music', 'Doodle Pals'],
      categoryId: '10', // Music
      madeForKids: true,
    },
  };
}

module.exports = { buildBedtime, pickSubjects };

// Compilation videos (16:9, about 5-8 minutes): several already-published Shorts of one category, re-rendered
// without their end card, framed for TV (title, "3 of 12" counter, the pals) and joined behind a title card.
// The owner chose this to give the Shorts' topics a second life as long videos (Shorts get few views).
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const TOPICS = require('./topics');

const KEY = t => ({ 'draw-shape': 'shape' }[t.template || 'draw-shape'] || t.template);
const cap = w => String(w).toLowerCase().replace(/\b[a-z]/g, c => c.toUpperCase());
const name = t => t.template === 'colormix' ? `${cap(t.a.name)} + ${cap(t.b.name)} = ${cap(t.c.name)}` : t.template === 'abc' ? `${t.letter} is for ${cap(t.word)}` : t.template === 'count' ? `Number ${t.n}` : cap(t.template === 'draw-shape' || !t.template ? t.becomes : t.word);
const list = (ts, k = 4) => ts.slice(0, k).map(name).join(', ');

const SERIES = {
  abc: { frame: 'ABC Time!', seg: 20, intro: ts => `Hi friends! Let's learn the letters ${ts[0].letter} to ${ts[ts.length - 1].letter}!`,
    title: ts => `Learn the ABC: Letters ${ts[0].letter} to ${ts[ts.length - 1].letter}! 🔤 ${ts.length} Letters and First Words for Toddlers`,
    learn: ts => [`the letters ${ts[0].letter} to ${ts[ts.length - 1].letter}`, 'first words', 'phonics'], tags: ['abc', 'alphabet', 'phonics'] },
  animal: { frame: 'Animal Sounds!', seg: 20, intro: () => "Hi friends! Who says moo? Let's learn animal sounds!",
    title: ts => `Animal Sounds for Kids! 🐮 ${ts.slice(0, 4).map(t => cap(t.word)).join(', ')} and More | ${ts.length} Animals`, learn: () => ['animal names', 'animal sounds'], tags: ['animalsounds', 'animals'] },
  count: { frame: "Let's Count!", seg: 22, intro: ts => `Hi friends! Let's count from ${Math.min(...ts.map(t => t.n))} to ${Math.max(...ts.map(t => t.n))}!`,
    title: ts => `Let's Count from ${Math.min(...ts.map(t => t.n))} to ${Math.max(...ts.map(t => t.n))}! 🔢 Numbers for Toddlers`, learn: () => ['numbers', 'counting', 'number words'], tags: ['counting', 'numbers'] },
  color: { frame: 'Colors with Coco!', seg: 20, intro: () => "Hi friends! Let's learn colors with Coco!",
    title: ts => `Learn Colors for Kids! 🎨 ${ts.slice(0, 4).map(t => cap(t.word)).join(', ')} and More | ${ts.length} Colors`, learn: () => ['colors', 'color words'], tags: ['colors', 'learncolors'] },
  shape: { frame: 'Shapes!', seg: 20, intro: () => "Hi friends! Let's draw shapes with Penny!",
    title: ts => `Learn Shapes for Kids! ✏️ Circle, Square, Triangle and More | ${ts.length} Shapes`, learn: () => ['shapes', 'drawing'], tags: ['shapes', 'drawingforkids'] },
  drawalong: { frame: "Let's Draw!", seg: 29, intro: () => "Hi friends! Get your crayons. Let's draw together!",
    title: ts => `How to Draw ${ts.length} Easy Things! ✏️ ${list(ts, 3)} and More | Drawing for Kids`, learn: () => ['drawing', 'shapes', 'first words'], tags: ['howtodraw', 'drawingforkids', 'easydrawing'] },
  vehicle: { frame: 'Vehicle Sounds!', seg: 20, intro: () => "Hi friends! Beep beep! Choo choo! Let's learn vehicle sounds!",
    title: ts => `Vehicle Sounds for Kids! 🚒 ${ts.slice(0, 4).map(t => cap(t.word)).join(', ')} and More | ${ts.length} Vehicles`, learn: () => ['vehicle names', 'vehicle sounds'], tags: ['vehiclesounds', 'vehicles'] },
  colormix: { frame: 'Mixing Colors!', seg: 21, intro: () => "Hi friends! Let's mix colors with Coco! What will we make?",
    title: ts => `Mixing Colors for Kids! 🎨 ${ts.length} Color Mixes with Coco the Crayon | Learn Colors`, learn: () => ['color mixing', 'colors', 'color words'], tags: ['colormixing', 'colors'] },
  bodyparts: { frame: 'My Body!', seg: 20, intro: () => "Hi friends! Let's learn about our bodies! Get ready to touch and wiggle!",
    title: ts => `Body Parts for Kids! 👃 ${ts.slice(0, 4).map(t => cap(t.word)).join(', ')} and More | Touch Your Nose!`, learn: () => ['body parts', 'first words'], tags: ['bodyparts', 'bodypartsforkids'] },
  feelings: { frame: 'How Do You Feel?', seg: 20, intro: () => "Hi friends! How do you feel today? Let's learn about feelings!",
    title: ts => `Feelings for Kids! 😊 ${ts.slice(0, 4).map(t => cap(t.word)).join(', ')} and More | How Do You Feel?`, learn: () => ['feelings', 'emotions', 'first words'], tags: ['feelings', 'emotions', 'feelingsforkids'] },
  shadow: { frame: 'Who Is Hiding?', seg: 20, intro: () => "Hi friends! Let's play a game. Who is hiding? Can you guess?",
    title: ts => `Guess the Shadow! 🔦 Who Is Hiding? ${ts.length} Guessing Games for Kids`, learn: () => ['guessing game', 'first words', 'animal names'], tags: ['guesstheshadow', 'guessinggame'] },
};

// a category with enough published-but-not-yet-compiled Shorts (at least 6)
function pickCompilation(used, today) {
  const pools = {};
  for (const t of TOPICS) {
    const k = KEY(t);
    // only Shorts from earlier days (today's batch is not published yet)
    if (SERIES[k] && used[t.id] && used[t.id] < today && !used['mix:' + t.id]) (pools[k] ||= []).push(t);
  }
  const lastMix = k => Object.entries(used).filter(([id, d]) => id.startsWith('mix:') && KEY(TOPICS.find(t => 'mix:' + t.id === id) || {}) === k).map(([, d]) => d).sort().pop() || '';
  const ok = Object.keys(pools).filter(k => pools[k].length >= 6).sort((x, y) => lastMix(x).localeCompare(lastMix(y)) || pools[y].length - pools[x].length);
  if (!ok.length) return null;
  const k = ok[0];
  const n = Math.min(pools[k].length, Number(process.env.MIX_MAX) || 15, Math.max(6, Math.round(360 / SERIES[k].seg)));
  return { key: k, topics: pools[k].slice(0, n) };
}

// when no category has enough published Shorts left: new, never-used topics rendered straight into the long video
// (the owner's choice: long videos get the views). They count as used, so they never come back as a Short.
const FRESH_ORDER = ['abc', 'count', 'shape', 'color', 'animal', 'vehicle', 'bodyparts', 'feelings', 'colormix', 'drawalong', 'shadow'];
function pickFreshCompilation(used) {
  const pools = {};
  for (const t of TOPICS) { const k = KEY(t); if (SERIES[k] && !used[t.id]) (pools[k] ||= []).push(t); }
  const lastMix = k => Object.entries(used).filter(([id]) => id.startsWith('mix:') && KEY(TOPICS.find(t => 'mix:' + t.id === id) || {}) === k).map(([, d]) => d).sort().pop() || '';
  // core topics first; a category compiled in the last 3 days waits so the daily mixes vary
  const recent = k => lastMix(k) >= new Date(Date.now() - 3 * 864e5).toISOString().slice(0, 10) ? 1 : 0;
  const ok = FRESH_ORDER.filter(k => (pools[k] || []).length >= 6).sort((x, y) => recent(x) - recent(y) || FRESH_ORDER.indexOf(x) - FRESH_ORDER.indexOf(y));
  if (!ok.length) return null;
  const k = ok[0];
  return { key: k, topics: pools[k].slice(0, Math.max(6, Math.min(12, Math.round(300 / SERIES[k].seg)))), fresh: true };
}

const ff = args => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' });
const dur = f => Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

async function shot(browser, query, out) {
  for (let attempt = 0; ; attempt++) { // a fresh page per try: Chromium occasionally refuses a capture
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    try {
      await page.goto('file://' + path.join(__dirname, 'scenes', 'frame.html') + '?' + new URLSearchParams(query));
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({ path: out });
      return;
    } catch (e) {
      if (attempt >= 2) throw e;
    } finally {
      await page.close();
    }
  }
}

// renderShort(topic, mp4) -> { subs, len }: the same Short render daily.js uses, without the end card
async function buildCompilation({ pick, DATE, OUT, browser, renderShort, outroMp4, outroSubs }) {
  const { key, topics } = pick, S = SERIES[key];
  const id = `mix-${key}-${DATE}`, work = path.join(OUT, id + '.work');
  fs.mkdirSync(work, { recursive: true });
  const hue = [...id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 11);
  const parts = [], subs = [], chapters = [];
  let at = 0;

  // title card
  const introText = S.intro(topics), introWav = path.join(work, 'intro.wav'), introPng = path.join(work, 'intro.png'), introMp4 = path.join(work, 'intro.mp4');
  execFileSync('python3', [path.join(__dirname, 'audio', 'card_audio.py'), introWav, '5', introText], { stdio: 'inherit' });
  await shot(browser, { mode: 'intro', title: S.frame, sub: `${topics.length} fun videos with the Doodle Pals!`, hue }, introPng);
  ff(['-loop', '1', '-framerate', '30', '-i', introPng, '-i', introWav, '-t', '5', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', introMp4]);
  parts.push(introMp4);
  for (const s of JSON.parse(fs.readFileSync(introWav + '.subs.json', 'utf8'))) subs.push(s);
  chapters.push([0, 'Intro']);
  at = dur(introMp4);

  for (const [i, t] of topics.entries()) {
    const seg = path.join(work, `${t.id}.mp4`), png = path.join(work, `${t.id}.png`), framed = path.join(work, `${t.id}.framed.mp4`);
    const { subs: s1 } = await renderShort(t, seg);
    await shot(browser, { mode: 'seg', title: S.frame, i: i + 1, n: topics.length, hue }, png);
    ff(['-loop', '1', '-framerate', '30', '-i', png, '-i', seg, '-filter_complex', '[1:v]scale=-2:1080,setsar=1[p];[0:v][p]overlay=(W-w)/2:0:shortest=1,format=yuv420p[v]',
      '-map', '[v]', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-ar', '44100', '-ac', '2', framed]);
    fs.rmSync(seg); fs.rmSync(png);
    parts.push(framed);
    chapters.push([at, name(t)]);
    for (const s of s1) subs.push({ ...s, start: s.start + at, end: s.end + at });
    at += dur(framed);
    console.log(`  [mix ${i + 1}/${topics.length}] ${t.id}`);
  }
  if (outroMp4) { parts.push(outroMp4); for (const s of outroSubs) subs.push({ ...s, start: s.start + at, end: s.end + at }); }

  const out = path.join(OUT, `${id}.mp4`);
  const inputs = parts.flatMap(p => ['-i', p]);
  const chain = parts.map((_, k) => `[${k}:v]fps=30,format=yuv420p,setsar=1[v${k}];[${k}:a]aresample=44100,aformat=channel_layouts=stereo[a${k}]`).join(';');
  const cat = parts.map((_, k) => `[v${k}][a${k}]`).join('') + `concat=n=${parts.length}:v=1:a=1[v][a]`;
  ff([...inputs, '-filter_complex', `${chain};${cat}`, '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out]);
  fs.rmSync(work, { recursive: true, force: true });

  const ts = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const title = S.title(topics).slice(0, 100);
  const tag = w => '#' + String(w).toLowerCase().replace(/[^a-z0-9]/g, '');
  return {
    id, file: path.basename(out), long: true, compiled: topics.map(t => t.id), subs,
    title,
    description: [
      `${title.split(' | ')[0]} — ${topics.length} Doodle Pals videos in one, with Penny the Pencil, Ellie the Eraser and Coco the Crayon!`,
      '',
      `🎯 What your child learns: ${S.learn(topics).join(', ')}.`,
      '',
      ...chapters.map(([s, n]) => `${ts(s)} ${n}`),
      '',
      'Gentle, original 2D animation in simple English for kids aged 2–6. Watch together on the big screen and play along!',
      '',
      [...S.tags.slice(0, 2), 'doodlepals'].map(tag).join(' '),
    ].join('\n'),
    tags: [...S.learn(topics), 'kids cartoon', 'learn english for kids', 'preschool learning', 'toddler learning', 'educational videos for kids', 'Doodle Pals', 'Penny the Pencil'],
    categoryId: '27',
    madeForKids: true,
  };
}

module.exports = { pickCompilation, pickFreshCompilation, buildCompilation, SERIES, shot, ff, dur, name, KEY };

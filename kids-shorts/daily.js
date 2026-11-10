// Daily batch: pick N unused topics, render each Short with its own soundtrack, write YouTube metadata.
// Usage: node daily.js [--count 5] [--date YYYY-MM-DD] [--out out]
// Output: out/<date>/<topic>.mp4 + out/<date>/batch.json ; state/used.json records what was rendered.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const TOPICS = require('./topics');
const { renderTopic, getTimeline } = require('./render');

const a = process.argv.slice(2);
const flag = (n, d) => (a.includes(n) ? a[a.indexOf(n) + 1] : d);
const COUNT = Number(flag('--count', 5));
const DATE = flag('--date', new Date().toISOString().slice(0, 10));
const OUT = path.join(flag('--out', 'out'), DATE);
const STATE = path.join(__dirname, 'state', 'used.json');
const SCENE = path.join(__dirname, 'scenes', 'draw-shape.html');

function pickTopics() {
  const used = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : {};
  // least-recently-used first; spread shapes so one day doesn't repeat a shape
  const order = [...TOPICS].sort((x, y) => (used[x.id] || '').localeCompare(used[y.id] || '') || x.id.localeCompare(y.id));
  const picked = [], shapes = new Set();
  for (const t of order) if (picked.length < COUNT && !shapes.has(t.shape)) { picked.push(t); shapes.add(t.shape); }
  for (const t of order) if (picked.length < COUNT && !picked.includes(t)) picked.push(t);
  return { picked, used };
}

function metadata(t) {
  const shape = t.shape[0] + t.shape.slice(1).toLowerCase();
  const thing = t.becomes[0] + t.becomes.slice(1).toLowerCase();
  const an = w => (/^[AEIOU]/i.test(w) ? 'an' : 'a');
  return {
    title: `Let's Draw ${an(shape)} ${shape}! It Becomes ${t.article} ${thing} ${t.emoji} | Shapes for Toddlers #shorts`,
    description: [
      `Draw along with Penny the Pencil! ✏️ Today we draw ${an(shape)} ${shape.toUpperCase()} and it turns into ${t.article} ${thing.toLowerCase()} ${t.emoji}`,
      '',
      `Learn the word: ${t.shape.split('').join('-')} — ${shape}!`,
      'Simple English words and shapes for kids aged 2–6.',
      '',
      'Grown-ups: grab a crayon and ask your little one — can YOU draw one too? 🖍️',
      '',
      '#shapes #kidslearning #toddlers #learnenglish #drawingforkids #preschool',
    ].join('\n'),
    tags: ['shapes for kids', `${shape.toLowerCase()} for kids`, `how to draw a ${thing.toLowerCase()}`, 'learn shapes', 'toddler learning',
      'preschool', 'english for kids', 'drawing for kids', 'kids cartoon', 'Doodle Pals', 'Penny the Pencil'],
    categoryId: '27', // Education
    madeForKids: true,
  };
}

(async () => {
  const { picked, used } = pickTopics();
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const batch = [];
  for (const [i, t] of picked.entries()) {
    const mp4 = path.join(OUT, `${t.id}.mp4`);
    const wav = path.join(OUT, `${t.id}.wav`);
    const tlFile = path.join(OUT, `${t.id}.timeline.json`);
    fs.writeFileSync(tlFile, JSON.stringify(await getTimeline(SCENE, t.id, browser)));
    const seed = [...(DATE + t.id)].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
    execFileSync('python3', [path.join(__dirname, 'audio', 'music.py'), wav, tlFile, String(seed)]);
    const t0 = Date.now();
    await renderTopic({ scene: SCENE, topic: t.id, out: mp4, audio: wav, browser });
    fs.rmSync(wav); fs.rmSync(tlFile);
    console.log(`[${i + 1}/${picked.length}] ${t.id} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    batch.push({ id: t.id, file: path.basename(mp4), ...metadata(t) });
    used[t.id] = DATE;
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'batch.json'), JSON.stringify({ date: DATE, videos: batch }, null, 2));
  fs.mkdirSync(path.dirname(STATE), { recursive: true });
  fs.writeFileSync(STATE, JSON.stringify(used, null, 2) + '\n');
  console.log('batch ready:', OUT);
})().catch(e => { console.error(e); process.exit(1); });

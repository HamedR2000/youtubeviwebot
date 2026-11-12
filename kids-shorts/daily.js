// Daily batch: pick N unused topics, render each Short with its own soundtrack, write YouTube metadata.
// Usage: node daily.js [--count 5] [--date YYYY-MM-DD] [--out out]
// Output: out/<date>/<topic>.mp4 + out/<date>/batch.json ; state/used.json records what was rendered.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const TOPICS = require('./topics');
const { renderTopic, getTimeline } = require('./render');
const { buildEpisode } = require('./longvideo');

const a = process.argv.slice(2);
const flag = (n, d) => (a.includes(n) ? a[a.indexOf(n) + 1] : d);
const COUNT = Number(flag('--count', 5));
const DATE = flag('--date', new Date().toISOString().slice(0, 10));
const OUT = path.join(flag('--out', 'out'), DATE);
const STATE = path.join(__dirname, 'state', 'used.json');
const sceneFor = t => path.join(__dirname, 'scenes', `${t.template || 'draw-shape'}.html`);

function pickTopics() {
  const used = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : {};
  const lru = (x, y) => (used[x.id] || '').localeCompare(used[y.id] || '') || x.id.localeCompare(y.id, 'en', { numeric: true });
  // one queue per template (shapes, numbers, ...); take from each in turn so every day is a mix
  const queues = {};
  for (const t of [...TOPICS].sort(lru)) (queues[t.template || 'draw-shape'] ||= []).push(t);
  const order = Object.keys(queues).sort((a, b) => lru(queues[a][0], queues[b][0]));
  const picked = [], shapes = new Set();
  while (picked.length < COUNT && order.some(k => queues[k].length)) {
    for (const k of order) {
      if (picked.length >= COUNT) break;
      const q = queues[k];
      const i = q.findIndex(t => !t.shape || !shapes.has(t.shape));
      if (i < 0) { q.length = 0; continue; }
      const [t] = q.splice(i, 1);
      picked.push(t); if (t.shape) shapes.add(t.shape);
    }
  }
  return { picked, used };
}

const tag = w => '#' + String(w).toLowerCase().replace(/[^a-z0-9]/g, '');
const tags = (...ws) => [...new Set(ws.map(tag))].join(' ');

function episodeMetadata(ep) {
  return {
    title: `${ep.title} ${ep.emoji} | Doodle Pals Cartoon for Kids | Learn ${ep.learn.slice(0, 3).map(w => w[0].toUpperCase() + w.slice(1)).join(', ')}`.slice(0, 100),
    description: [
      `${ep.title} ${ep.emoji} — a new Doodle Pals story with Penny the Pencil, Ellie the Eraser and Coco the Crayon!`,
      '',
      `In this episode we learn: ${ep.learn.join(', ')}.`,
      'Gentle, original 2D animation and songs in simple English for kids aged 2–6.',
      'Sing along, count along and answer the questions — the friends wait for you!',
      '',
      tags('kidscartoon', ...(ep.hashtags || []), 'learnenglish', 'preschool', 'toddlers', 'kidslearning', 'doodlepals'),
    ].join('\n'),
    tags: ['kids cartoon', 'cartoon for toddlers', 'learn english for kids', 'preschool learning', 'educational cartoon', ...ep.learn, 'Doodle Pals', 'Penny the Pencil', 'Ellie the Eraser', 'Coco the Crayon'],
    categoryId: '27',
    madeForKids: true,
  };
}

function metadata(t) {
  if (t.template === 'animal') {
    const animal = t.word[0] + t.word.slice(1).toLowerCase();
    const snd = t.sound.split(' ')[0].replace('!', '');
    return {
      title: `Who Says ${snd}? ${t.emoji} It's ${t.article === 'an' ? 'an' : 'a'} ${animal}! | Animal Sounds for Toddlers #shorts`,
      description: [
        `Guess the animal with Ellie the Eraser! 🩷 Who says "${t.sound}"? It's ${t.article} ${animal.toLowerCase()} ${t.emoji}`,
        '',
        `Learn the word: ${t.word.split('').join('-')} — ${animal}!`,
        'Animal names and sounds in English for kids aged 2–6.',
        '',
        `Grown-ups: make the sound together — can your little one say "${snd.toLowerCase()}"? 🐾`,
        '',
        tags(t.word, 'animalsounds', `${t.word}sound`, 'animals', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['animal sounds for kids', `${animal.toLowerCase()} sound`, `what does the ${animal.toLowerCase()} say`, 'animals for toddlers', 'learn animals',
        'preschool', 'english for kids', 'kids cartoon', 'Doodle Pals', 'Ellie the Eraser'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'abc') {
    const cap = w => w.split(/([ -])/).map(x => x[0] ? x[0] + x.slice(1).toLowerCase() : x).join('');
    const word = cap(t.word);
    return {
      title: `Letter ${t.letter} is for ${word}! ${t.emoji} | ABC for Toddlers #shorts`,
      description: [
        `Learn the letter ${t.letter} with Penny the Pencil! ✏️ Big ${t.letter}, little ${t.letter.toLowerCase()} — ${t.letter} is for ${word.toLowerCase()} ${t.emoji}`,
        '',
        `Learn the word: ${t.word.replace(/[^A-Z]/g, '').split('').join('-')} — ${word}!`,
        'The English alphabet for kids aged 2–6, one letter at a time.',
        '',
        `Grown-ups: what else starts with ${t.letter}? Look around the room together! 🔎`,
        '',
        tags(`letter${t.letter}`, 'abc', t.word, 'phonics', 'alphabet', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['abc for kids', `letter ${t.letter}`, `${t.letter} is for ${word.toLowerCase()}`, 'alphabet for toddlers', 'learn the alphabet', 'phonics',
        'preschool', 'english for kids', 'kids cartoon', 'Doodle Pals', 'Penny the Pencil'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'count') {
    const word = t.word[0] + t.word.slice(1).toLowerCase();
    const things = t.objectName.toLowerCase();
    return {
      title: `Let's Count to ${word}! ${t.n} ${things[0].toUpperCase() + things.slice(1)} ${t.emoji} | Numbers for Toddlers #shorts`,
      description: [
        `Count along with Penny the Pencil! ✏️ Today we draw the number ${t.n} and count ${t.n} ${things} ${t.emoji}`,
        '',
        `Learn the word: ${t.word.split('').join('-')} — ${word}!`,
        'Simple numbers and English words for kids aged 2–6.',
        '',
        `Grown-ups: count with your little one on your fingers — can they count to ${t.word.toLowerCase()}? 🖐️`,
        '',
        tags(`number${t.n}`, 'counting', `countto${t.n}`, 'numbers', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['numbers for kids', `number ${t.n}`, `count to ${t.n}`, 'counting for toddlers', 'learn numbers', 'toddler learning',
        'preschool', 'english for kids', 'kids cartoon', 'Doodle Pals', 'Penny the Pencil'],
      categoryId: '27',
      madeForKids: true,
    };
  }
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
      tags(t.shape, 'shapes', `howtodraw${t.becomes}`, 'drawingforkids', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
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
    fs.writeFileSync(tlFile, JSON.stringify(await getTimeline(sceneFor(t), t.id, browser)));
    const seed = [...(DATE + t.id)].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
    execFileSync('python3', [path.join(__dirname, 'audio', 'music.py'), wav, tlFile, String(seed)]);
    if (process.env.NARRATION !== '0') { // friendly narrator over the music (Kokoro TTS)
      const topicFile = path.join(OUT, `${t.id}.topic.json`);
      fs.writeFileSync(topicFile, JSON.stringify({ template: t.template || 'draw-shape', shape: t.shape, becomes: t.becomes, article: t.article, n: t.n, word: t.word, objectName: t.objectName, letter: t.letter, sound: t.sound }));
      execFileSync('python3', [path.join(__dirname, 'audio', 'narration.py'), wav, tlFile, topicFile, wav,
        '--voice', process.env.NARRATOR_VOICE || 'af_heart'], { stdio: 'inherit' });
      fs.rmSync(topicFile);
    }
    const t0 = Date.now();
    await renderTopic({ scene: sceneFor(t), topic: t.id, out: mp4, audio: wav, browser });
    fs.rmSync(wav); fs.rmSync(tlFile);
    console.log(`[${i + 1}/${picked.length}] ${t.id} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    batch.push({ id: t.id, file: path.basename(mp4), ...metadata(t) });
    used[t.id] = DATE;
  }
  // one long (16:9) episode per day: the next episode script not yet used
  if (!a.includes('--no-episode')) {
    const dir = path.join(__dirname, 'episodes');
    const next = fs.readdirSync(dir).filter(f => f.endsWith('.json')).sort().find(f => !used['episode:' + f.replace(/\.json$/, '')]);
    if (next) {
      const ep = JSON.parse(fs.readFileSync(path.join(dir, next), 'utf8'));
      const mp4 = path.join(OUT, `episode-${ep.id}.mp4`);
      const t0 = Date.now();
      const tl = await buildEpisode(path.join(dir, next), mp4, { browser });
      fs.rmSync(mp4.replace(/\.mp4$/, '') + '.work', { recursive: true, force: true });
      console.log(`[episode] ${ep.id} ${tl.duration.toFixed(0)}s (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      batch.push({ id: `episode-${ep.id}`, file: path.basename(mp4), long: true, ...episodeMetadata(ep) });
      used['episode:' + ep.id] = DATE;
    } else console.log('[episode] no unused episode script left — write a new one in episodes/');
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT, 'batch.json'), JSON.stringify({ date: DATE, videos: batch }, null, 2));
  fs.mkdirSync(path.dirname(STATE), { recursive: true });
  fs.writeFileSync(STATE, JSON.stringify(used, null, 2) + '\n');
  console.log('batch ready:', OUT);
})().catch(e => { console.error(e); process.exit(1); });

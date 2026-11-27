// Daily batch: pick N unused topics, render each Short with its own soundtrack, write YouTube metadata.
// Usage: node daily.js [--count 5] [--date YYYY-MM-DD] [--out out]
// Output: out/<date>/<topic>.mp4 + out/<date>/batch.json ; state/used.json records what was rendered.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const TOPICS = require('./topics');
const { renderTopic, getTimeline } = require('./render');
const { renderOutro, appendOutro, OUTRO_SUBS } = require('./outro');

// English captions (.srt) uploaded with each video: [{text, start, end}] in seconds
function writeSrt(file, subs) {
  const ts = x => { const ms = Math.round(x * 1000); const p = (n, w = 2) => String(n).padStart(w, '0');
    return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
  const rows = subs.filter(s => s.text && s.end > s.start).sort((a, b) => a.start - b.start);
  fs.writeFileSync(file, rows.map((s, i) => `${i + 1}\n${ts(s.start)} --> ${ts(s.end)}\n${s.text}\n`).join('\n'));
}
const withOutroSubs = (subs, len) => a.includes('--no-outro') ? subs : [...subs, ...OUTRO_SUBS.map(o => ({ ...o, start: o.start + len, end: o.end + len }))];
const { buildEpisode } = require('./longvideo');
const { renderThumbnail } = require('./thumbnail');
const { pickCompilation, pickFreshCompilation, buildCompilation } = require('./compile');
const { buildBedtime } = require('./bedtime');

const a = process.argv.slice(2);
const flag = (n, d) => (a.includes(n) ? a[a.indexOf(n) + 1] : d);
const COUNT = Number(flag('--count', 1));
const DATE = flag('--date', new Date().toISOString().slice(0, 10));
const OUT = path.join(flag('--out', 'out'), DATE);
const STATE = path.join(__dirname, 'state', 'used.json');
// story episodes: order of preference by series (channel data: ABC/numbers/shapes/animals get ~10x the views)
const SERIES_RANK = ['ABC Adventures', 'Counting to Ten', 'Shape Sort', 'Animal Homes', 'Music Time', "What's Missing?", "Coco's Fruit Shop", 'Opposites', 'Kind Friends', 'Weather Friends'];
const SCENE_OF = { vehicle: 'animal' }; // templates that reuse another template's scene
const sceneFor = t => path.join(__dirname, 'scenes', `${SCENE_OF[t.template] || t.template || 'draw-shape'}.html`);

function pickTopics() {
  const used = fs.existsSync(STATE) ? JSON.parse(fs.readFileSync(STATE, 'utf8')) : {};
  // never repeat: only topics that were never rendered before, in their natural order
  const fresh = TOPICS.filter(t => !used[t.id]);
  const lastUse = k => TOPICS.filter(t => (t.template || 'draw-shape') === k).map(t => used[t.id] || '').sort().pop() || '';
  // one queue per template (shapes, numbers, ...); take from each in turn so every day is a mix
  const queues = {};
  for (const t of fresh) (queues[t.template || 'draw-shape'] ||= []).push(t);
  const order = Object.keys(queues).sort((a, b) => lastUse(a).localeCompare(lastUse(b)) || a.localeCompare(b));
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
  // what is left after today, per template, so the daily task can warn early and ask for new topics
  const left = {};
  for (const t of fresh) if (!picked.includes(t)) left[t.template || 'draw-shape'] = (left[t.template || 'draw-shape'] || 0) + 1;
  return { picked, used, left };
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

// trips (every 2 days): the Doodle Pals visit a place (zoo, farm, aquarium, countries...)
function tripMetadata(ep) {
  return {
    title: `${ep.title} ${ep.emoji} Doodle Pals Trip for Kids | Learn ${ep.learn.slice(0, 2).map(w => w[0].toUpperCase() + w.slice(1)).join(' and ')}`.slice(0, 100),
    description: [
      `${ep.title} ${ep.emoji} Hop on the bus with Penny the Pencil, Ellie the Eraser and Coco the Crayon!`,
      '',
      `On this trip we learn: ${ep.learn.join(', ')}.`,
      'Gentle, original 2D animation and songs in simple English for kids aged 2–6. Answer the questions and move along — the friends wait for you!',
      '',
      tags('fieldtrip', 'kidscartoon', ...(ep.hashtags || []), 'learnenglish', 'preschool', 'toddlers', 'kidslearning', 'doodlepals'),
    ].join('\n'),
    tags: ['field trip for kids', 'virtual field trip', 'kids cartoon', 'learn english for kids', 'preschool learning', 'educational cartoon', ...ep.learn, 'Doodle Pals'],
    categoryId: '27',
    madeForKids: true,
  };
}

function metadata(t) {
  if (t.template === 'feelings') {
    const w = t.word[0] + t.word.slice(1).toLowerCase(), lw = w.toLowerCase();
    return {
      title: `I Feel ${w}! ${t.emoji} Feelings for Kids | Can You Make a ${w} Face? #shorts`.slice(0, 100),
      description: [
        `I feel ${lw}! ${t.emoji} ${t.why} Can you make a ${lw} face? Learn feelings and emotions in simple English with the Doodle Pals.`,
        '',
        `Grown-ups: make the ${lw} face together and talk about a time you felt ${lw} — naming feelings helps little ones handle them. 💛`,
        '',
        tags(`${lw}`, 'feelings', 'emotions', 'feelingsforkids', 'learnenglish', 'kidslearning', 'toddlers', 'preschool'),
      ].join('\n'),
      tags: ['feelings for kids', 'emotions for kids', `${lw} for kids`, 'learn feelings', 'how do you feel', 'social emotional learning',
        'toddler learning', 'preschool', 'english for kids', 'Doodle Pals'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'bodyparts') {
    const w = t.word[0] + t.word.slice(1).toLowerCase(), lw = w.toLowerCase();
    return {
      title: `${t.plural ? 'These Are My' : 'This Is My'} ${w}! ${t.emoji} Body Parts for Kids | Touch Your ${w}! #shorts`.slice(0, 100),
      description: [
        `${t.plural ? 'These are my' : 'This is my'} ${lw}! ${t.emoji} ${t.action} Can you touch your ${lw}? Learn body parts in simple English with the Doodle Pals.`,
        '',
        `Grown-ups: point to your own ${lw} together and say the word — little ones learn best by moving! 🙌`,
        '',
        tags(`my${lw}`, 'bodyparts', 'bodypartsforkids', 'learnenglish', 'kidslearning', 'toddlers', 'preschool', 'firstwords'),
      ].join('\n'),
      tags: ['body parts for kids', `${lw} for kids`, 'learn body parts', 'my body', 'body parts song', 'toddler learning', 'first words',
        'preschool', 'english for kids', 'Doodle Pals'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'colormix') {
    const cc = n => n.toLowerCase().replace(/\b[a-z]/g, x => x.toUpperCase());
    const [A, B, C] = [cc(t.a.name), cc(t.b.name), cc(t.c.name)];
    return {
      title: `${A} + ${B} = ${C}! 🎨 Mixing Colors for Kids ${t.emoji} | Color Mixing with Coco #shorts`.slice(0, 100),
      description: [
        `What happens when we mix ${A.toLowerCase()} and ${B.toLowerCase()}? 🎨 Coco the Crayon stirs the paint… and it's ${C.toLowerCase()}, like ${t.like}! ${t.emoji}`,
        '',
        'Learn colors and color mixing in simple English with the Doodle Pals — for kids aged 2–6.',
        `Grown-ups: try it at home with paint or play-dough — mix ${A.toLowerCase()} and ${B.toLowerCase()} together! 🖌️`,
        '',
        tags('colormixing', 'mixingcolors', `learn${C}`, 'colors', 'kidsart', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['color mixing for kids', 'mixing colors', `${A.toLowerCase()} and ${B.toLowerCase()} make ${C.toLowerCase()}`, 'learn colors', 'colors for toddlers', 'toddler learning',
        'preschool', 'english for kids', 'Doodle Pals', 'Coco the Crayon'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'vehicle') {
    const w = t.word.split(' ').map(x => x[0] + x.slice(1).toLowerCase()).join(' ');
    const snd = t.sound.replace(/[!,]/g, '').split(' ').slice(0, 2).join(' ');
    return {
      title: `Who Says ${snd}? ${t.emoji} It's ${t.article === 'an' ? 'an' : 'a'} ${w}! | Vehicle Sounds for Kids #shorts`.slice(0, 100),
      description: [
        `${t.sound} Who says ${snd.toLowerCase()}? Ellie the Eraser erases the scribbles… it's ${t.article} ${w.toLowerCase()}! ${t.emoji}`,
        '',
        'Learn vehicle names and sounds in simple English with the Doodle Pals — for kids aged 2–6.',
        `Grown-ups: make the sound together — ${t.sound.toLowerCase()} 🙌`,
        '',
        tags(w, 'vehiclesounds', 'vehicles', 'carsforkids', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['vehicle sounds for kids', `${w.toLowerCase()} for kids`, `${w.toLowerCase()} sound`, 'vehicles for toddlers', 'cars and trucks', 'toddler learning',
        'preschool', 'english for kids', 'Doodle Pals', 'Ellie the Eraser'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'shadow') {
    const w = t.word.split(' ').map(x => x[0] + x.slice(1).toLowerCase()).join(' ');
    return {
      title: `Who Is Hiding? 🔦 Guess the Shadow! It's ${t.article ? t.article + ' ' : ''}${w} ${t.emoji} | Guessing Game for Kids #shorts`.slice(0, 100),
      description: [
        `Who is hiding in the shadow? 🔦 Look carefully, count 3-2-1 with Penny the Pencil… and guess! It's ${t.article ? t.article + ' ' : ''}${w.toLowerCase()} ${t.emoji}`,
        '',
        'A fun guessing game for toddlers and preschoolers: shapes, shadows and first English words.',
        'Grown-ups: pause before the reveal and let your little one shout the answer! 🙌',
        '',
        tags('guesstheshadow', 'guessinggame', w, 'kidsgames', 'firstwords', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['guess the shadow', 'guessing game for kids', 'who is hiding', 'shadow game', `${w.toLowerCase()} for kids`, 'first words',
        'toddler learning', 'preschool', 'english for kids', 'Doodle Pals', 'Penny the Pencil'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'drawalong') {
    const w = t.word[0] + t.word.slice(1).toLowerCase(), A = t.article === 'an' ? 'an' : 'a';
    return {
      title: `How to Draw ${A} ${w}! ${t.emoji} Easy Step by Step Drawing for Kids #shorts`,
      description: [
        `Let's draw ${A} ${w.toLowerCase()} ${t.emoji} with Penny the Pencil — in ${t.steps.length} easy steps! Then Coco the Crayon colours it in.`,
        '',
        ...t.steps.map((s, i) => `${i + 1}. ${s.show}`),
        '',
        `Grown-ups: grab paper and crayons and draw ${A} ${w.toLowerCase()} together with your little one! 🖍️`,
        '',
        tags(`howtodraw${w}`, 'drawingforkids', 'easydrawing', 'stepbystep', 'artforkids', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: [`how to draw a ${w.toLowerCase()}`, `${w.toLowerCase()} drawing`, 'easy drawing for kids', 'drawing for kids', 'step by step drawing',
        'art for kids', 'toddler learning', 'preschool', 'english for kids', 'Doodle Pals', 'Penny the Pencil', 'Coco the Crayon'],
      categoryId: '27',
      madeForKids: true,
    };
  }
  if (t.template === 'color') {
    const color = t.word[0] + t.word.slice(1).toLowerCase();
    const thing = t.mainName[0].toUpperCase() + t.mainName.slice(1);
    const plural = /s$/.test(t.mainName); // e.g. grapes: no article
    const a1 = plural ? '' : /^[aeiou]/i.test(color) ? 'An' : 'A';
    return {
      title: `Learn the Color ${color}! ${t.emoji} ${a1 ? a1 + ' ' : ''}${color} ${thing} | Colors for Toddlers #shorts`,
      description: [
        `Coco the Crayon colours ${plural ? 'the' : /^[aeiou]/i.test(t.mainName) ? 'an' : 'a'} ${t.mainName} ${t.word.toLowerCase()}! 🖍️ ${t.extras.map(e => e[1]).join(', ')} — what else is ${t.word.toLowerCase()}? ${t.emoji}`,
        '',
        `Learn the word: ${t.word.split('').join('-')} — ${color}!`,
        'Colours in simple English for kids aged 2–6.',
        '',
        `Grown-ups: go on a colour hunt — find something ${t.word.toLowerCase()} at home together! 🔎`,
        '',
        tags(t.word, 'colors', `learn${t.word}`, 'learncolors', 'kidslearning', 'toddlers', 'learnenglish', 'preschool'),
      ].join('\n'),
      tags: ['colors for kids', `color ${t.word.toLowerCase()}`, `learn the color ${t.word.toLowerCase()}`, 'learn colors', 'colors for toddlers',
        'preschool', 'english for kids', 'kids cartoon', 'Doodle Pals', 'Coco the Crayon'],
      categoryId: '27',
      madeForKids: true,
    };
  }
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
  const { picked, used, left } = pickTopics();
  if (picked.length < COUNT) console.log(`[topics] only ${picked.length} unused Short topics left — add new ones to topics.js`);
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const batch = [];
  // end card (bye bye + like & subscribe for grown-ups), rendered once per orientation and appended to every video
  const outro = { portrait: path.join(OUT, 'outro-portrait.tmp.mp4'), landscape: path.join(OUT, 'outro-landscape.tmp.mp4') };
  if (!a.includes('--no-outro')) for (const o of Object.keys(outro)) await renderOutro(o, outro[o], { browser });
  const withOutro = (mp4, o) => { if (!a.includes('--no-outro')) appendOutro(mp4, outro[o]); };
  // one Short (portrait) with music + narration; returns its captions and length (no end card)
  async function renderShort(t, mp4) {
    const wav = mp4.replace(/\.mp4$/, '.wav');
    const tlFile = mp4.replace(/\.mp4$/, '.timeline.json');
    fs.writeFileSync(tlFile, JSON.stringify(await getTimeline(sceneFor(t), t.id, browser)));
    const seed = [...(DATE + t.id)].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
    execFileSync('python3', [path.join(__dirname, 'audio', 'music.py'), wav, tlFile, String(seed)]);
    let subs = [];
    if (process.env.NARRATION !== '0') { // friendly narrator over the music (Kokoro TTS)
      const topicFile = mp4.replace(/\.mp4$/, '.topic.json');
      fs.writeFileSync(topicFile, JSON.stringify({ template: t.template || 'draw-shape', shape: t.shape, becomes: t.becomes, article: t.article, n: t.n, word: t.word, objectName: t.objectName, letter: t.letter, sound: t.sound, mainName: t.mainName, extras: t.extras, steps: t.steps, extra: t.extra, a: t.a, b: t.b, c: t.c, like: t.like, plural: t.plural, action: t.action, why: t.why }));
      execFileSync('python3', [path.join(__dirname, 'audio', 'narration.py'), wav, tlFile, topicFile, wav,
        '--voice', process.env.NARRATOR_VOICE || 'af_heart'], { stdio: 'inherit' });
      fs.rmSync(topicFile);
      if (fs.existsSync(wav + '.subs.json')) { subs = JSON.parse(fs.readFileSync(wav + '.subs.json', 'utf8')); fs.rmSync(wav + '.subs.json'); }
    }
    const { timeline: rtl } = await renderTopic({ scene: sceneFor(t), topic: t.id, out: mp4, audio: wav, browser });
    fs.rmSync(wav); fs.rmSync(tlFile);
    return { subs, len: rtl.end || 20 };
  }

  for (const [i, t] of picked.entries()) {
    const mp4 = path.join(OUT, `${t.id}.mp4`);
    const t0 = Date.now();
    const { subs, len } = await renderShort(t, mp4);
    writeSrt(mp4.replace(/\.mp4$/, '.srt'), withOutroSubs(subs, len));
    withOutro(mp4, 'portrait');
    console.log(`[${i + 1}/${picked.length}] ${t.id} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    batch.push({ id: t.id, file: path.basename(mp4), captions: path.basename(mp4).replace(/\.mp4$/, '.srt'), ...metadata(t) });
    used[t.id] = DATE;
  }
  // long (16:9) episodes: the next --episodes (default 2) episode scripts not yet used
  const EPISODES = a.includes('--no-episode') ? 0 : Number(flag('--episodes', 1));
  const epDir = path.join(__dirname, 'episodes');
  for (let e = 0; e < EPISODES; e++) {
    const dir = epDir;
    // core learning topics first (they get the views: ABC, numbers, shapes, animals); softer series wait
    const rank = f => { const ser = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')).series || ''; const k = SERIES_RANK.findIndex(r => ser.startsWith(r)); return k < 0 ? 50 : k; };
    const next = fs.readdirSync(dir).filter(f => f.endsWith('.json') && !used['episode:' + f.replace(/\.json$/, '')])
      .sort((x, y) => rank(x) - rank(y) || x.localeCompare(y))[0];
    if (next) {
      const ep = JSON.parse(fs.readFileSync(path.join(dir, next), 'utf8'));
      const mp4 = path.join(OUT, `episode-${ep.id}.mp4`);
      const t0 = Date.now();
      const tl = await buildEpisode(path.join(dir, next), mp4, { browser });
      const lines = tl.beats.flatMap(b => b.lines).filter(l => l.who !== 'pause' && l.text).map(l => ({ text: l.text, start: l.start, end: l.start + l.dur }));
      writeSrt(mp4.replace(/\.mp4$/, '.srt'), withOutroSubs(lines, tl.duration));
      fs.rmSync(mp4.replace(/\.mp4$/, '') + '.work', { recursive: true, force: true });
      withOutro(mp4, 'landscape');
      await renderThumbnail(ep, mp4.replace(/\.mp4$/, '.jpg'), browser);
      console.log(`[episode] ${ep.id} ${tl.duration.toFixed(0)}s (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      batch.push({ id: `episode-${ep.id}`, file: path.basename(mp4), captions: path.basename(mp4).replace(/\.mp4$/, '.srt'), thumbnail: path.basename(mp4).replace(/\.mp4$/, '.jpg'), long: true, ...episodeMetadata(ep) });
      used['episode:' + ep.id] = DATE;
    } else { console.log('[episode] no unused episode script left — write a new one in episodes/'); break; }
  }
  // trip film (16:9): '--trips auto' makes one when the last trip is 2+ days old (the owner's choice since 2026-11-27: every 2 days)
  const TRIPS = flag('--trips', '0'), tripDir = path.join(__dirname, 'trips');
  const lastTrip = Object.entries(used).filter(([k]) => k.startsWith('trip:')).map(([, d]) => d).sort().pop() || '';
  const tripDue = TRIPS === 'auto' ? (!lastTrip || (Date.parse(DATE.slice(0, 10)) - Date.parse(lastTrip.slice(0, 10))) / 864e5 >= 2 ? 1 : 0) : Number(TRIPS) || 0;
  for (let k = 0; k < tripDue; k++) {
    const next = fs.existsSync(tripDir) && fs.readdirSync(tripDir).filter(f => f.endsWith('.json') && !used['trip:' + JSON.parse(fs.readFileSync(path.join(tripDir, f), 'utf8')).id]).sort()[0];
    if (!next) { console.log('[trip] no unused trip script left — write a new one in trips/'); break; }
    const ep = JSON.parse(fs.readFileSync(path.join(tripDir, next), 'utf8'));
    const mp4 = path.join(OUT, `${ep.id}.mp4`), t0 = Date.now();
    const tl = await buildEpisode(path.join(tripDir, next), mp4, { browser });
    const lines = tl.beats.flatMap(b => b.lines).filter(l => l.who !== 'pause' && l.text).map(l => ({ text: l.text, start: l.start, end: l.start + l.dur }));
    writeSrt(mp4.replace(/\.mp4$/, '.srt'), withOutroSubs(lines, tl.duration));
    fs.rmSync(mp4.replace(/\.mp4$/, '') + '.work', { recursive: true, force: true });
    withOutro(mp4, 'landscape');
    await renderThumbnail(ep, mp4.replace(/\.mp4$/, '.jpg'), browser);
    console.log(`[trip] ${ep.id} ${tl.duration.toFixed(0)}s (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
    batch.push({ id: ep.id, file: path.basename(mp4), captions: path.basename(mp4).replace(/\.mp4$/, '.srt'), thumbnail: path.basename(mp4).replace(/\.mp4$/, '.jpg'), long: true, ...tripMetadata(ep) });
    used['trip:' + ep.id] = DATE;
  }
  // compilation videos (16:9) made of already-published Shorts of one category
  const COMPS = Number(flag('--compilations', 1));
  for (let c = 0; c < COMPS; c++) {
    const pick = pickCompilation(used, DATE) || pickFreshCompilation(used);
    if (!pick) { console.log('[mix] no topics left for a compilation'); break; }
    if (pick.fresh) console.log(`[mix] not enough published Shorts: ${pick.topics.length} new ${pick.key} topics go straight into the long video`);
    const t0 = Date.now();
    const v = await buildCompilation({ pick, DATE: c ? `${DATE}-${c + 1}` : DATE, OUT, browser, renderShort,
      outroMp4: a.includes('--no-outro') ? null : outro.landscape, outroSubs: OUTRO_SUBS });
    const { subs, compiled, ...meta } = v;
    writeSrt(path.join(OUT, v.id + '.srt'), subs);
    batch.push({ ...meta, captions: v.id + '.srt' });
    for (const id of compiled) { used['mix:' + id] = DATE; if (pick.fresh) used[id] = DATE; } // fresh topics never become Shorts later
    console.log(`[mix] ${v.id}: ${compiled.length} segments (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  // evening slot: a calm ~14 min bedtime (15 min YouTube upload limit) lullaby video (published with the morning batch)
  for (let k = 0; k < Number(flag('--bedtime', 0)); k++) {
    const t0 = Date.now();
    const { subjects, subs, video } = await buildBedtime({ used, DATE: k ? `${DATE}-${k + 1}` : DATE, OUT, browser, minutes: Number(flag('--bedtime-minutes', 14)) });
    writeSrt(path.join(OUT, video.id + '.srt'), subs);
    batch.push({ ...video, captions: video.id + '.srt' });
    for (const id of subjects) used['bed:' + id] = DATE;
    console.log(`[bedtime] ${video.id}: ${subjects.join(', ')} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  const episodesLeft = fs.readdirSync(epDir).filter(f => f.endsWith('.json') && !used['episode:' + f.replace(/\.json$/, '')]).length;
  await browser.close();
  for (const f of Object.values(outro)) fs.rmSync(f, { force: true });
  for (const k of Object.keys(left)) left[k] = TOPICS.filter(t => (t.template || 'draw-shape') === k && !used[t.id]).length;
  fs.writeFileSync(path.join(OUT, 'batch.json'), JSON.stringify({ date: DATE, videos: batch, topicsLeft: left, episodesLeft }, null, 2));
  fs.mkdirSync(path.dirname(STATE), { recursive: true });
  fs.writeFileSync(STATE, JSON.stringify(used, null, 2) + '\n');
  console.log('batch ready:', OUT);
})().catch(e => { console.error(e); process.exit(1); });

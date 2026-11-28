// Daily long learning video (up to ~14 min while the channel has the 15 min upload limit, 16:9), a new mix every day for the TV: the channel's published core-topic Shorts in sections
// (ABC, numbers, colors, shapes, animals), taken from the Release files (no re-render), the Shorts' end card
// cut off, each framed like the compilations, joined behind a title card and closed with the landscape end card.
// Usage (CI): node mega.js <releases-dir> <date> <out-dir>
//   <releases-dir>/<tag>/{batch.json,uploaded.json,<id>.mp4,<id>.srt}  (downloaded by the workflow)
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const TOPICS = require('./topics');
const { shot, ff, dur, name } = require('./compile');
const { renderOutro, OUTRO_SUBS } = require('./outro');

const END_CARD = 6.8; // seconds of end card at the end of every Short (outro.html DURATION)
const CARD_SINCE = 'shorts-2026-11-20'; // first day with the end card
// every Shorts category can be a section; core topics (the channel's best performers) first when equally fresh
const SECTIONS = [
  ['abc', 'ABC Time!', 'ABC'], ['count', "Let's Count!", 'Numbers'], ['color', 'Colors with Coco!', 'Colors'],
  ['draw-shape', 'Shapes!', 'Shapes'], ['animal', 'Animal Sounds!', 'Animals'], ['vehicle', 'Vehicle Sounds!', 'Vehicles'],
  ['bodyparts', 'My Body!', 'Body Parts'], ['feelings', 'How Do You Feel?', 'Feelings'], ['colormix', 'Mixing Colors!', 'Color Mixing'],
  ['drawalong', "Let's Draw!", 'Drawing'], ['shadow', 'Who Is Hiding?', 'Guess Who'],
];
// YouTube rejects videos over 15 min until the channel has "intermediate features" (this one does not yet)
const MAX_SECONDS = 14 * 60;
const HARD_LIMIT = 14.5 * 60; // the real cut-off while joining (end card included)

function readSrt(f) {
  if (!fs.existsSync(f)) return [];
  const t = s => { const [h, m, r] = s.split(':'); const [sec, ms] = r.split(','); return +h * 3600 + +m * 60 + +sec + +ms / 1000; };
  return fs.readFileSync(f, 'utf8').split(/\n\n+/).map(b => b.trim().split('\n')).filter(l => l.length >= 3)
    .map(l => { const [a, b] = l[1].split(' --> '); return { start: t(a), end: t(b), text: l.slice(2).join(' ') }; });
}
function writeSrt(file, subs) {
  const ts = x => { const ms = Math.round(x * 1000); const p = (n, w = 2) => String(n).padStart(w, '0');
    return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`; };
  fs.writeFileSync(file, subs.sort((a, b) => a.start - b.start).map((s, i) => `${i + 1}\n${ts(s.start)} --> ${ts(s.end)}\n${s.text}\n`).join('\n'));
}

(async () => {
  const [relDir, DATE, OUT] = process.argv.slice(2).map((x, i) => i === 1 ? x : path.resolve(x)); // absolute: ffmpeg's concat list resolves paths itself
  fs.mkdirSync(OUT, { recursive: true });
  // every published Short we have the file of
  const have = {};
  for (const tag of fs.readdirSync(relDir)) {
    const d = path.join(relDir, tag);
    if (!fs.existsSync(path.join(d, 'uploaded.json'))) continue;
    for (const u of JSON.parse(fs.readFileSync(path.join(d, 'uploaded.json'), 'utf8'))) {
      const mp4 = path.join(d, u.id + '.mp4');
      if (fs.existsSync(mp4)) have[u.id] = { mp4, srt: path.join(d, u.id + '.srt'), tag };
    }
  }
  // what earlier long learning videos used (their batch.json lists the lessons), so each day's video is a new mix
  const lastUsed = {}, sectionLast = {}, sectionUses = {};
  const later = (a, b) => [a || '', b].sort().pop();
  for (const tag of fs.readdirSync(relDir)) {
    const f = path.join(relDir, tag, 'batch.json');
    if (!fs.existsSync(f)) continue;
    for (const v of JSON.parse(fs.readFileSync(f, 'utf8')).videos || []) {
      if (!v.id.startsWith('mega-') || v.id === `mega-${DATE}`) continue;
      const day = v.id.slice(5);
      for (const id of v.compiled || []) {
        lastUsed[id] = later(lastUsed[id], day);
        const t = TOPICS.find(x => x.id === id); if (t) sectionLast[t.template || 'draw-shape'] = later(sectionLast[t.template || 'draw-shape'], day);
      }
      for (const tpl of new Set((v.compiled || []).map(id => (TOPICS.find(x => x.id === id) || {}).template || 'draw-shape'))) sectionUses[tpl] = (sectionUses[tpl] || 0) + 1;
      // the first videos did not list their lessons: their title names the sections
      if (!v.compiled) for (const [tpl, , label] of SECTIONS) if (new RegExp(`\\b${label}\\b`).test(v.title)) { sectionLast[tpl] = later(sectionLast[tpl], day); sectionUses[tpl] = (sectionUses[tpl] || 0) + 1; }
    }
  }
  const order = (a, b) => (a.n || 0) - (b.n || 0) || TOPICS.indexOf(a) - TOPICS.indexOf(b);
  const fresh = (a, b) => (lastUsed[a.id] || '').localeCompare(lastUsed[b.id] || '') || order(a, b);
  const sections = SECTIONS.map(([tpl, frame, label], rank) => {
    const all = TOPICS.filter(t => (t.template || 'draw-shape') === tpl && have[t.id]);
    // least recently used lessons of this section, then shown in their natural order (A, B, C... / 1, 2, 3...)
    return { tpl, frame, label, rank, all, last: sectionLast[tpl] || '' }; // when this section was last in a video
  }).filter(s => s.all.length >= 4)
    .sort((a, b) => a.last.localeCompare(b.last) || (sectionUses[a.tpl] || 0) - (sectionUses[b.tpl] || 0) || a.rank - b.rank); // ties: the section used least so far
  // fill up to ~14 minutes: the freshest sections first, each with its least recently used lessons
  let est = 5, chosen = [];
  for (const s of sections) {
    if (chosen.length >= 3) break; // 2-3 topics per video keeps it focused
    const room = Math.min(Math.floor((MAX_SECONDS - est) / 20.5), chosen.length < 2 ? 18 : 99); // leave room for a 2nd section
    if (room < 4) break;
    const part = { ...s, topics: [...s.all].sort(fresh).slice(0, room).sort(order) };
    chosen.push(part); est += part.topics.length * 20.5;
  }
  if (!chosen.length) { console.log('[mega] not enough published Shorts'); return; }
  if (process.env.MEGA_DRY) { for (const c of chosen) console.log(`[mega] ${c.label}: ${c.topics.map(t => t.id).join(' ')}`); return; } // check the pick only

  const id = `mega-${DATE}`, work = path.join(OUT, id + '.work');
  fs.mkdirSync(work, { recursive: true });
  const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
  const hue = 190;
  const parts = [], subs = [], chapters = [], used = [];
  const total = chosen.reduce((a, s) => a + s.topics.length, 0);
  const minutes = Math.round(est / 60);

  const introWav = path.join(work, 'intro.wav'), introPng = path.join(work, 'intro.png'), introMp4 = path.join(work, 'intro.mp4');
  const introText = `Hi friends! Let's learn together with the Doodle Pals! ${chosen.map(s => s.label).join(', ')}!`;
  execFileSync('python3', [path.join(__dirname, 'audio', 'card_audio.py'), introWav, '6', introText], { stdio: 'inherit' });
  await shot(browser, { mode: 'intro', title: 'Learn with Doodle Pals!', sub: chosen.map(s => s.label).join(' • '), hue }, introPng);
  ff(['-loop', '1', '-framerate', '30', '-i', introPng, '-i', introWav, '-t', '6', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '44100', '-ac', '2', introMp4]);
  parts.push(introMp4); subs.push(...JSON.parse(fs.readFileSync(introWav + '.subs.json', 'utf8')));
  chapters.push([0, 'Intro']);
  let at = dur(introMp4);

  for (const sec of chosen) {
    if (at + 20 + END_CARD > HARD_LIMIT) break;
    chapters.push([at, `${sec.label}: ${name(sec.topics[0])} to ${name(sec.topics[sec.topics.length - 1])}`]);
    for (const [i, t] of sec.topics.entries()) {
      // Shorts made before the end card existed (before 2026-11-20) keep their whole length
      const src = have[t.id], len = dur(src.mp4) - (src.tag >= CARD_SINCE ? END_CARD : 0);
      if (at + len + END_CARD + 1 > HARD_LIMIT) { console.log(`  [mega] stop at ${Math.round(at)}s (15 min upload limit)`); break; }
      const png = path.join(work, `${t.id}.png`), framed = path.join(work, `${t.id}.mp4`);
      await shot(browser, { mode: 'seg', title: sec.frame, i: i + 1, n: sec.topics.length, hue: (hue + parts.length * 7) % 360 }, png);
      ff(['-loop', '1', '-framerate', '30', '-i', png, '-t', String(len), '-i', src.mp4, '-filter_complex',
        `[1:v]trim=0:${len},setpts=PTS-STARTPTS,scale=-2:1080,setsar=1[p];[0:v][p]overlay=(W-w)/2:0:shortest=1,format=yuv420p[v];[1:a]atrim=0:${len},asetpts=PTS-STARTPTS,afade=t=out:st=${Math.max(0, len - 0.6)}:d=0.6[a]`,
        '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-c:a', 'aac', '-ar', '44100', '-ac', '2', framed]);
      fs.rmSync(png);
      parts.push(framed); used.push(t.id);
      for (const s of readSrt(src.srt)) if (s.start < len) subs.push({ text: s.text, start: s.start + at, end: Math.min(s.end, len) + at });
      at += dur(framed);
      console.log(`  [mega] ${sec.label} ${i + 1}/${sec.topics.length} ${t.id}`);
    }
  }
  const outroMp4 = path.join(work, 'outro.mp4');
  await renderOutro('landscape', outroMp4, { browser });
  parts.push(outroMp4); for (const s of OUTRO_SUBS) subs.push({ ...s, start: s.start + at, end: s.end + at });
  await browser.close();

  // join in chunks (ffmpeg concat demuxer: all parts share one encoding)
  const list = path.join(work, 'list.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p.replace(/'/g, "'\\''")}'`).join('\n'));
  const out = path.join(OUT, `${id}.mp4`);
  ff(['-f', 'concat', '-safe', '0', '-i', list, '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', '30',
    '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-movflags', '+faststart', out]);
  fs.rmSync(work, { recursive: true, force: true });
  writeSrt(path.join(OUT, `${id}.srt`), subs);

  const ts = s => s >= 3600 ? `${Math.floor(s / 3600)}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}:${String(Math.floor(s % 60)).padStart(2, '0')}` : `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  const realMin = Math.round(dur(out) / 60);
  const labels = chosen.map(s => s.label);
  const title = `Toddler Learning Video 📚 ${labels.slice(0, -1).join(', ')} and ${labels[labels.length - 1]} | ${realMin} Minutes with Doodle Pals`.slice(0, 100);
  const meta = {
    id, file: path.basename(out), captions: `${id}.srt`, long: true, title, compiled: used,
    description: [
      `${realMin} minutes of learning with Penny the Pencil, Ellie the Eraser and Coco the Crayon! ${total} lessons in one video: ${labels.join(', ').toLowerCase()}.`,
      '',
      `🎯 What your child learns: ${chosen.map(s => `${s.label.toLowerCase()} (${name(s.topics[0])} to ${name(s.topics[s.topics.length - 1])})`).join(', ')}.`,
      '',
      ...chapters.map(([s, n]) => `${ts(s)} ${n}`),
      '',
      'Gentle, original 2D animation in simple English for kids aged 2–6 — perfect for the big screen.',
      '',
      '#toddlerlearning #learningvideos #doodlepals',
    ].join('\n'),
    tags: ['toddler learning video', 'learning videos for toddlers', 'abc', 'numbers', 'colors', 'shapes', 'animal sounds', 'preschool learning',
      'educational videos for kids', 'learn english for kids', 'Doodle Pals'],
    categoryId: '27', madeForKids: true,
  };
  fs.writeFileSync(path.join(OUT, `${id}.json`), JSON.stringify(meta, null, 2));
  console.log(`[mega] ${id}: ${total} segments, ${realMin} min`);
})().catch(e => { console.error(e); process.exit(1); });

/* موتور مشترک نمونه‌ها: تولید آثار آزمایشی (SVG)، گالری تمام‌صفحه، انیمیشن ظاهرشدن
   در نسخه‌ی نهایی به‌جای آثار تولیدی، عکس‌های واقعی آثار استاد قرار می‌گیرد. */
(() => {
  let UID = 0;
  const rand = seed => { let s = (seed * 2654435761 >>> 0) % 2147483647 || 1; return () => (s = s * 16807 % 2147483647) / 2147483647; };
  const pick = (r, a) => a[Math.floor(r() * a.length)];
  const f = n => n.toFixed(1);

  function smooth(p) {
    const n = p.length; let d = `M${f(p[0][0])},${f(p[0][1])}`;
    for (let i = 0; i < n; i++) {
      const a = p[(i - 1 + n) % n], b = p[i], c = p[(i + 1) % n], e = p[(i + 2) % n];
      d += `C${f(b[0] + (c[0] - a[0]) / 6)},${f(b[1] + (c[1] - a[1]) / 6)} ${f(c[0] - (e[0] - b[0]) / 6)},${f(c[1] - (e[1] - b[1]) / 6)} ${f(c[0])},${f(c[1])}`;
    }
    return d + 'Z';
  }
  function blob(r, cx, cy, rx, ry, n = 8, amp = .35) {
    const p = [];
    for (let i = 0; i < n; i++) { const a = i / n * Math.PI * 2, k = 1 + (r() - .5) * amp; p.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k]); }
    return smooth(p);
  }
  const open = (W, h) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${h}" width="${W}" height="${h}" preserveAspectRatio="xMidYMid slice">`;

  /* تابلوی نقاشی انتزاعی/منظره‌گون */
  function painting(seed, pal, h = 500) {
    const r = rand(seed), u = ++UID, W = 400;
    let s = open(W, h) + `<defs><filter id="bl${u}" filterUnits="userSpaceOnUse" x="-200" y="-200" width="${W + 400}" height="${h + 400}"><feGaussianBlur stdDeviation="${18 + r() * 22}"/></filter>
      <linearGradient id="lg${u}" x1="0" y1="0" x2="${f(r())}" y2="1"><stop offset="0" stop-color="${pal[0]}"/><stop offset="1" stop-color="${pick(r, pal)}"/></linearGradient></defs>
      <rect width="${W}" height="${h}" fill="url(#lg${u})"/><g filter="url(#bl${u})">`;
    for (let i = 0; i < 7; i++) s += `<path d="${blob(r, r() * W, r() * h, 50 + r() * 120, 50 + r() * 120)}" fill="${pick(r, pal)}" opacity="${f(.5 + r() * .5)}"/>`;
    s += '</g>';
    for (let i = 0; i < 4; i++) { const y = r() * h; s += `<path d="M-20,${f(y)} Q${W / 2},${f(y + (r() - .5) * 160)} ${W + 20},${f(y + (r() - .5) * 90)}" stroke="${pick(r, pal)}" stroke-width="${f(3 + r() * 22)}" fill="none" stroke-linecap="round" opacity="${f(.3 + r() * .5)}"/>`; }
    if (r() > .45) s += `<circle cx="${f(60 + r() * 280)}" cy="${f(40 + r() * h * .4)}" r="${f(14 + r() * 38)}" fill="${pick(r, pal)}" opacity=".92"/>`;
    return s + '</svg>';
  }

  /* قطعه‌ی خوشنویسی: تک‌کلمه، سیاه‌مشق یا چلیپا با زرافشان و قاب */
  const WORDS = ['عشق', 'هو', 'صبر', 'نور', 'دل', 'یار', 'امید', 'سکوت', 'جان', 'مهر'];
  const VERSES = [['در ازل پرتو حسنت', 'ز تجلی دم زد'], ['بشنو این نی', 'چون شکایت می‌کند'], ['هر کسی کو دور ماند', 'از اصل خویش']];
  function calligraphy(seed, pal, h = 500) {
    const r = rand(seed), u = ++UID, W = 400; const [paper, edge, ink, gold, seal] = pal;
    const F = `font-family="'Noto Nastaliq Urdu',serif"`;
    let s = open(W, h) + `<defs><radialGradient id="pg${u}" cx=".5" cy=".45" r=".8"><stop offset="0" stop-color="${paper}"/><stop offset="1" stop-color="${edge}"/></radialGradient></defs>
      <rect width="${W}" height="${h}" fill="url(#pg${u})"/>`;
    for (let i = 0; i < 70; i++) s += `<circle cx="${f(r() * W)}" cy="${f(r() * h)}" r="${f(.5 + r() * 2.2)}" fill="${gold}" opacity="${f(.25 + r() * .5)}"/>`;
    s += `<rect x="16" y="16" width="${W - 32}" height="${h - 32}" fill="none" stroke="${gold}" stroke-width="2"/><rect x="24" y="24" width="${W - 48}" height="${h - 48}" fill="none" stroke="${gold}" stroke-width=".7"/>`;
    const mode = r();
    if (mode < .3) {
      for (let i = 0; i < 9; i++) s += `<text x="${f(40 + r() * 320)}" y="${f(80 + r() * (h - 140))}" ${F} font-size="${f(34 + r() * 50)}" fill="${ink}" opacity="${f(.12 + r() * .75)}" text-anchor="middle" transform="rotate(${f(-25 + r() * 20)} 200 ${h / 2})">${pick(r, WORDS)}</text>`;
    } else if (mode < .6) {
      const v = pick(r, VERSES);
      s += `<g transform="rotate(-14 200 ${h / 2})"><text x="200" y="${h / 2 - 34}" ${F} font-size="40" fill="${ink}" text-anchor="middle">${v[0]}</text><text x="200" y="${h / 2 + 62}" ${F} font-size="40" fill="${ink}" text-anchor="middle">${v[1]}</text></g>`;
    } else {
      const w = pick(r, WORDS), fs = Math.min(150, 360 / Math.max(1.4, w.length * .62));
      s += `<text x="200" y="${f(h / 2 + fs * .1)}" ${F} font-size="${f(fs)}" fill="${ink}" text-anchor="middle">${w}</text>`;
    }
    s += `<text x="58" y="${h - 44}" ${F} font-size="13" fill="${ink}" opacity=".75" text-anchor="middle">رضایتمند</text><rect x="${W - 62}" y="${h - 62}" width="22" height="22" fill="${seal}" opacity=".85" rx="2"/>`;
    return s + '</svg>';
  }

  /* مجسمه: فرم سه‌بعدی‌نما روی پایه با نورپردازی قابل تغییر (light: ۰ تا ۱) */
  function sculpture(seed, pal, h = 500, light = .3) {
    const r = rand(seed), u = ++UID, W = 400; const [bg, base, hi, sh] = pal;
    const top = h * .72;
    let s = open(W, h) + `<defs><radialGradient id="sp${u}" cx=".5" cy=".1" r=".95"><stop offset="0" stop-color="${hi}" stop-opacity=".28"/><stop offset=".6" stop-color="${bg}" stop-opacity="0"/></radialGradient>
      <radialGradient id="m${u}" cx="${f(light)}" cy=".3" r=".9" fx="${f(light)}" fy=".22"><stop offset="0" stop-color="${hi}"/><stop offset=".45" stop-color="${base}"/><stop offset="1" stop-color="${sh}"/></radialGradient>
      <linearGradient id="pd${u}" x1="0" x2="1"><stop offset="0" stop-color="#2a2724"/><stop offset="${f(light)}" stop-color="#57514a"/><stop offset="1" stop-color="#1c1a18"/></linearGradient>
      <filter id="fs${u}" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${h}"><feGaussianBlur stdDeviation="9"/></filter></defs>
      <rect width="${W}" height="${h}" fill="${bg}"/><rect width="${W}" height="${h}" fill="url(#sp${u})"/>
      <ellipse cx="200" cy="${f(h * .93)}" rx="120" ry="12" fill="#000" opacity=".55" filter="url(#fs${u})"/>
      <rect x="135" y="${f(top)}" width="130" height="${f(h * .21)}" fill="url(#pd${u})"/><rect x="135" y="${f(top)}" width="130" height="5" fill="#6d665d"/>`;
    const type = Math.floor(r() * 3), M = `fill="url(#m${u})"`;
    if (type === 0) {
      const th = h * .36;
      s += `<path d="${blob(r, 200, top - th / 2, 62 + r() * 20, th / 2, 9, .22)}" ${M}/><rect x="188" y="${f(top - th - 26)}" width="24" height="34" ${M}/><path d="${blob(r, 200 + (r() - .5) * 16, top - th - 58, 34, 42, 8, .15)}" ${M}/>`;
    } else if (type === 1) {
      const ry = h * .3;
      s += `<path fill-rule="evenodd" d="${blob(r, 200, top - ry, 95, ry, 10, .25)} ${blob(r, 200 + (r() - .5) * 30, top - ry - 10, 36, ry * .42, 8, .3)}" ${M}/>`;
    } else {
      let y = top;
      for (let i = 0; i < 3; i++) { const ry = 34 + r() * 40, rx = 40 + r() * 60; s += `<path d="${blob(r, 200 + (r() - .5) * 50, y - ry * .85, rx, ry, 8, .3)}" ${M}/>`; y -= ry * 1.55; }
    }
    return s + '</svg>';
  }

  /* پرتره‌ی جایگزین (سیلوئت) */
  function portrait(pal, h = 520) {
    const u = ++UID, W = 400; const [bg, fg, acc] = pal;
    return open(W, h) + `<defs><radialGradient id="pt${u}" cx=".5" cy=".35" r=".8"><stop offset="0" stop-color="${acc}"/><stop offset="1" stop-color="${bg}"/></radialGradient></defs>
      <rect width="${W}" height="${h}" fill="url(#pt${u})"/><circle cx="200" cy="${h * .36}" r="72" fill="${fg}"/><path d="M60,${h} C70,${h * .66} 140,${h * .56} 200,${h * .56} S330,${h * .66} 340,${h}Z" fill="${fg}"/>
      <text x="200" y="${h - 30}" font-family="Vazirmatn,sans-serif" font-size="14" fill="${acc}" text-anchor="middle" opacity=".9">جای عکس پرتره‌ی استاد</text></svg>`;
  }

  /* گالری تمام‌صفحه: بزرگ‌نمایی، کیبورد، کشیدن انگشت، شمارنده */
  function lightbox() {
    const el = document.createElement('div');
    el.className = 'lb'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true');
    el.innerHTML = `<button class="lb-x" aria-label="بستن">×</button><button class="lb-n lb-prev" aria-label="قبلی">›</button><button class="lb-n lb-next" aria-label="بعدی">‹</button>
      <div class="lb-stage"><div class="lb-art"></div></div><div class="lb-cap"><div><h3></h3><p></p></div><span class="lb-c"></span></div><div class="lb-hint">برای بزرگ‌نمایی روی اثر بزنید</div>`;
    document.body.appendChild(el);
    const art = el.querySelector('.lb-art'), stage = el.querySelector('.lb-stage');
    let items = [], i = 0, tx = 0;
    function fit() {
      const svg = art.querySelector('svg'); if (!svg) return;
      const vb = svg.viewBox.baseVal, ar = vb.width / vb.height;
      const mw = innerWidth * .9, mh = innerHeight * .72, w = Math.min(mw, mh * ar);
      svg.style.width = w + 'px'; svg.style.height = w / ar + 'px';
    }
    function show(n) {
      i = (n + items.length) % items.length; const it = items[i];
      art.classList.remove('zoom'); art.style.opacity = 0;
      setTimeout(() => {
        art.innerHTML = it.html; fit();
        el.querySelector('h3').textContent = it.title; el.querySelector('p').textContent = it.meta || '';
        el.querySelector('.lb-c').textContent = `${(i + 1).toLocaleString('fa')} / ${items.length.toLocaleString('fa')}`;
        art.style.opacity = 1;
      }, 160);
    }
    const close = () => { el.classList.remove('on'); document.body.style.overflow = ''; };
    el.querySelector('.lb-x').onclick = close;
    el.querySelector('.lb-prev').onclick = () => show(i - 1);
    el.querySelector('.lb-next').onclick = () => show(i + 1);
    el.addEventListener('click', e => { if (e.target === el || e.target === stage) close(); });
    art.addEventListener('click', e => {
      const b = art.getBoundingClientRect();
      art.style.transformOrigin = `${(e.clientX - b.left) / b.width * 100}% ${(e.clientY - b.top) / b.height * 100}%`;
      art.classList.toggle('zoom');
    });
    art.addEventListener('mousemove', e => {
      if (!art.classList.contains('zoom')) return;
      const b = art.getBoundingClientRect();
      art.style.transformOrigin = `${(e.clientX - b.left) / b.width * 100}% ${(e.clientY - b.top) / b.height * 100}%`;
    });
    addEventListener('keydown', e => {
      if (!el.classList.contains('on')) return;
      if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i + 1); if (e.key === 'ArrowRight') show(i - 1);
    });
    el.addEventListener('touchstart', e => tx = e.touches[0].clientX, { passive: true });
    el.addEventListener('touchend', e => { const d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50 && !art.classList.contains('zoom')) show(d > 0 ? i + 1 : i - 1); });
    addEventListener('resize', fit);
    return (list, n) => { items = list; el.classList.add('on'); document.body.style.overflow = 'hidden'; show(n); };
  }

  /* ظاهرشدن تدریجی هنگام اسکرول */
  function reveal(sel = '.rv') {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll(sel).forEach(x => io.observe(x));
  }

  /* شمارنده‌ی عددی */
  function counters(sel = '[data-count]') {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return; io.unobserve(e.target);
      const t = +e.target.dataset.count, t0 = performance.now();
      const step = now => { const k = Math.min(1, (now - t0) / 1600), v = Math.round(t * (1 - Math.pow(1 - k, 3))); e.target.textContent = v.toLocaleString('fa'); if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    }), { threshold: .5 });
    document.querySelectorAll(sel).forEach(x => io.observe(x));
  }

  /* نوار پیشرفت اسکرول */
  function progress(el) { addEventListener('scroll', () => { el.style.transform = `scaleX(${scrollY / (document.documentElement.scrollHeight - innerHeight)})`; }, { passive: true }); }

  const LB_CSS = `.lb{position:fixed;inset:0;z-index:1000;background:var(--lb-bg,rgba(8,7,6,.96));backdrop-filter:blur(12px);display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .35s}
.lb.on{opacity:1;pointer-events:auto}.lb-stage{flex:1;display:flex;align-items:center;justify-content:center;width:100%;overflow:hidden}
.lb-art{transition:transform .45s cubic-bezier(.2,.8,.2,1),opacity .16s;cursor:zoom-in;box-shadow:0 30px 80px rgba(0,0,0,.6)}.lb-art.zoom{transform:scale(2.2);cursor:zoom-out}.lb-art svg{display:block}
.lb-cap{width:min(900px,92vw);display:flex;justify-content:space-between;align-items:end;gap:16px;padding:14px 0 26px;color:var(--lb-fg,#eee)}.lb-cap h3{margin:0;font-size:1.15rem;font-weight:600}.lb-cap p{margin:4px 0 0;opacity:.65;font-size:.88rem}
.lb-c{font-size:.85rem;opacity:.7;white-space:nowrap}.lb-hint{position:absolute;top:22px;inset-inline-start:24px;font-size:.78rem;color:var(--lb-fg,#eee);opacity:.45}
.lb button{position:absolute;background:none;border:1px solid var(--lb-accent,#c9a45c);color:var(--lb-fg,#eee);width:48px;height:48px;border-radius:50%;font-size:1.6rem;cursor:pointer;z-index:2;transition:background .25s;line-height:1}
.lb button:hover{background:var(--lb-accent,#c9a45c);color:#000}.lb-x{top:16px;inset-inline-end:18px}.lb-prev{inset-inline-start:18px;top:50%}.lb-next{inset-inline-end:18px;top:50%}
@media (max-width:640px){.lb-n{top:auto!important;bottom:84px}.lb-hint{display:none}}`;
  const st = document.createElement('style'); st.textContent = LB_CSS; document.head.appendChild(st);

  window.Art = { rand, pick, painting, calligraphy, sculpture, portrait, lightbox, reveal, counters, progress };
})();

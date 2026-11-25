// Topic bank for the "Let's draw a SHAPE → it becomes a THING" Shorts template.
// Coordinates are relative to the drawing card centre (0,0); keep art within about ±330.
// Each element: [tag, attrs]. Layers: back (behind fill), front (over fill, under face).
(function () {
  const C = (cx, cy, r, fill, extra = {}) => ['circle', { cx, cy, r, fill, ...extra }];
  const E = (cx, cy, rx, ry, fill, rot = 0) => ['ellipse', { cx, cy, rx, ry, fill, transform: `rotate(${rot} ${cx} ${cy})` }];
  const P = (d, fill, extra = {}) => ['path', { d, fill, ...extra }];
  const R = (x, y, width, height, fill, rx = 12, extra = {}) => ['rect', { x, y, width, height, rx, fill, ...extra }];
  const line = (d, stroke, w = 14) => P(d, 'none', { stroke, 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });

  const circle = r => `M 0 ${-r} A ${r} ${r} 0 1 1 -0.01 ${-r}`;
  const oval = (rx, ry) => `M 0 ${-ry} A ${rx} ${ry} 0 1 1 -0.01 ${-ry}`;
  const star = (ro, ri, cy = 0) => {
    const pts = [];
    for (let i = 0; i < 10; i++) {
      const r = i % 2 ? ri : ro, a = -Math.PI / 2 + i * Math.PI / 5;
      pts.push(`${(Math.cos(a) * r).toFixed(1)} ${(Math.sin(a) * r + cy).toFixed(1)}`);
    }
    return 'M ' + pts.join(' L ') + ' Z';
  };
  const heart = 'M 0 -170 C -60 -310 -330 -270 -305 -50 C -285 110 -110 210 0 310 C 110 210 285 110 305 -50 C 330 -270 60 -310 0 -170 Z';
  const ring = (n, f) => Array.from({ length: n }, (_, i) => f(i, (i / n) * Math.PI * 2));

  const TOPICS = [
    {
      id: 'circle-sun', shape: 'CIRCLE', becomes: 'SUN', article: 'a', emoji: '☀️',
      strokes: [circle(290)], fill: [P(circle(290), '#FFC93C')], face: { y: 0, s: 1 },
      back: ring(12, (i, a) => R(-16, -440, 32, 90, i % 2 ? '#FFB627' : '#FF9F1C', 16, { transform: `rotate(${i * 30})` })),
      front: [],
    },
    {
      id: 'circle-cookie', shape: 'CIRCLE', becomes: 'COOKIE', article: 'a', emoji: '🍪',
      strokes: [circle(290)], fill: [P(circle(290), '#E3A869')], face: { y: 10, s: 0.9 },
      back: [],
      front: [[-170, -150], [150, -170], [210, 60], [-210, 90], [0, -230], [-80, 210], [110, 200]]
        .map(([x, y], i) => E(x, y, 30, 24, '#6B3E26', i * 40)),
    },
    {
      id: 'circle-orange', shape: 'CIRCLE', becomes: 'ORANGE', article: 'an', emoji: '🍊',
      strokes: [circle(280)], fill: [P(circle(280), '#FF9F1C')], face: { y: 20, s: 0.95 },
      back: [],
      front: [R(-12, -330, 24, 70, '#6B4226', 10), E(70, -320, 80, 34, '#4CB944', -20),
        ...[[-180, -120], [190, -60], [-150, 170], [160, 170], [0, 230]].map(([x, y]) => C(x, y, 7, '#F28A0F'))],
    },
    {
      id: 'square-present', shape: 'SQUARE', becomes: 'PRESENT', article: 'a', emoji: '🎁',
      strokes: ['M -250 -230 H 250 V 270 H -250 Z'], fill: [R(-250, -230, 500, 500, '#FF6B6B', 0)], face: { y: 60, s: 0.9 },
      back: [E(-75, -280, 85, 48, '#FFC93C', -25), E(75, -280, 85, 48, '#FFC93C', 25)],
      front: [R(-38, -230, 76, 500, '#FFC93C', 0), R(-250, -110, 500, 70, '#FFC93C', 0), C(0, -265, 40, '#FFB020')],
    },
    {
      id: 'square-robot', shape: 'SQUARE', becomes: 'ROBOT', article: 'a', emoji: '🤖',
      strokes: ['M -250 -220 H 250 V 280 H -250 Z'], fill: [R(-250, -220, 500, 500, '#9AD1F5', 0)], face: { y: 30, s: 1 },
      back: [line('M 0 -220 V -330', '#5B6B7F', 16), R(-300, -40, 50, 130, '#5B6B7F', 18), R(250, -40, 50, 130, '#5B6B7F', 18)],
      front: [C(0, -345, 34, '#FF6B6B'), ...[[-210, -180], [210, -180], [-210, 240], [210, 240]].map(([x, y]) => C(x, y, 14, '#5B6B7F'))],
    },
    {
      id: 'triangle-pizza', shape: 'TRIANGLE', becomes: 'PIZZA', article: 'a', emoji: '🍕',
      strokes: ['M -300 -220 L 300 -220 L 0 320 Z'], fill: [P('M -300 -220 L 300 -220 L 0 320 Z', '#FFD166')], face: { y: -40, s: 0.8 },
      back: [],
      front: [R(-320, -275, 640, 80, '#E09F3E', 40),
        ...[[-150, -130], [140, -120], [0, 180], [-60, 60], [80, 40]].map(([x, y]) => C(x, y, 36, '#E63946'))],
    },
    {
      id: 'triangle-tree', shape: 'TRIANGLE', becomes: 'TREE', article: 'a', emoji: '🎄',
      strokes: ['M 0 -300 L 290 220 L -290 220 Z'], fill: [P('M 0 -300 L 290 220 L -290 220 Z', '#4CB944')], face: { y: 60, s: 0.85 },
      back: [R(-55, 210, 110, 120, '#8B5A3C', 10)],
      front: [P(star(70, 30, -300), '#FFC93C'), ...[[-150, 170, '#FF6B6B'], [150, 160, '#4D96FF'], [-60, -120, '#F15BB5'], [80, -40, '#FFC93C']].map(([x, y, f]) => C(x, y, 24, f))],
    },
    {
      id: 'rectangle-door', shape: 'RECTANGLE', becomes: 'DOOR', article: 'a', emoji: '🚪',
      strokes: ['M -180 -320 H 180 V 320 H -180 Z'], fill: [R(-180, -320, 360, 640, '#C68B59', 0)], face: { y: -60, s: 0.8 },
      back: [],
      front: [R(-130, -280, 260, 120, '#B07A4C', 14), R(-130, 140, 260, 140, '#B07A4C', 14), C(120, 70, 26, '#FFC93C')],
    },
    {
      id: 'oval-balloon', shape: 'OVAL', becomes: 'BALLOON', article: 'a', emoji: '🎈',
      strokes: [oval(220, 270)], fill: [P(oval(220, 270), '#FF5D8F')], face: { y: -20, s: 0.9 },
      back: [line('M 0 285 C -40 330 40 370 0 420', '#5B4A7A', 8), P('M -24 300 L 24 300 L 0 270 Z', '#E04877')],
      front: [E(-110, -150, 40, 70, '#FFFFFF', 25)],
    },
    {
      id: 'oval-avocado', shape: 'OVAL', becomes: 'AVOCADO', article: 'an', emoji: '🥑',
      strokes: [oval(230, 300)], fill: [P(oval(230, 300), '#3E7B27'), P(oval(185, 255), '#C8E07A')], face: { y: -90, s: 0.75 },
      back: [],
      front: [C(0, 110, 95, '#8B5A3C'), C(-25, 85, 22, '#A97452')],
    },
    {
      id: 'heart-strawberry', shape: 'HEART', becomes: 'STRAWBERRY', article: 'a', emoji: '🍓',
      strokes: [heart], fill: [P(heart, '#F2545B')], face: { y: 30, s: 0.9 },
      back: [],
      front: [...[-110, -55, 0, 55, 110].map((x, i) => E(x, -200, 34, 70, '#4CB944', (i - 2) * 28)),
        ...[[-200, -60], [200, -60], [-120, 160], [120, 160], [0, 230], [-230, 40], [230, 40]].map(([x, y]) => E(x, y, 9, 14, '#FFE066'))],
    },
    {
      id: 'star-starfish', shape: 'STAR', becomes: 'STARFISH', article: 'a', emoji: '⭐',
      strokes: [star(320, 140, 20)], fill: [P(star(320, 140, 20), '#FF9F80')], face: { y: 30, s: 0.75 },
      back: [],
      front: ring(5, (i, a) => C(Math.cos(a - Math.PI / 2) * 230, Math.sin(a - Math.PI / 2) * 230 + 20, 18, '#FFD3C2')),
    },
    {
      id: 'diamond-kite', shape: 'DIAMOND', becomes: 'KITE', article: 'a', emoji: '🪁',
      strokes: ['M 0 -320 L 230 -60 L 0 300 L -230 -60 Z'], fill: [P('M 0 -320 L 230 -60 L 0 300 L -230 -60 Z', '#4D96FF')], face: { y: -20, s: 0.75 },
      back: [line('M 0 300 C 80 340 140 330 200 400', '#5B4A7A', 7), P('M 90 335 l 30 -26 l 6 40 Z', '#FFC93C'), P('M 170 375 l 30 -26 l 6 40 Z', '#FF6B6B')],
      front: [line('M 0 -320 V 300', '#FFF3D6', 10), line('M -230 -60 H 230', '#FFF3D6', 10)],
    },
  ];

  // ---- Numbers: Penny draws the numeral, then we count objects (art borrowed from the shape topics) ----
  const DIGITS = {
    0: ['M 0 -190 C -150 -190 -150 190 0 190 C 150 190 150 -190 0 -190'],
    1: ['M -50 -130 L 20 -190 L 20 190'],
    2: ['M -110 -110 C -100 -210 115 -215 110 -90 C 105 10 -100 100 -120 190 L 120 190'],
    3: ['M -100 -160 C -40 -225 120 -200 100 -80 C 90 -20 30 -5 -20 0 C 60 0 120 30 115 100 C 110 215 -60 220 -110 150'],
    4: ['M 60 190 L 60 -190 L -120 80 L 130 80'],
    5: ['M 100 -180 L -80 -180 L -100 -20 C -20 -60 120 -40 115 70 C 110 205 -60 215 -110 140'],
    6: ['M 80 -170 C 0 -215 -120 -150 -115 40 C -110 205 110 210 110 80 C 110 -30 -60 -40 -110 40'],
    7: ['M -110 -180 L 110 -180 L -20 190'],
    8: ['M 0 0 C -120 -30 -100 -190 0 -190 C 100 -190 120 -30 0 0 C -130 30 -120 190 0 190 C 120 190 130 30 0 0'],
    9: ['M 105 -60 C 60 30 -110 20 -105 -80 C -100 -205 110 -205 105 -60 C 100 80 60 180 -80 190'],
  };
  const shift = (paths, dx) => paths.map(d => d.replace(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g, (m, x, y) => `${+x + dx} ${y}`));
  const NUM_WORDS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN',
    'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN', 'SEVENTEEN', 'EIGHTEEN', 'NINETEEN', 'TWENTY'];
  const COUNT_OBJECTS = [
    ['oval-balloon', 'BALLOON', 'BALLOONS', '🎈'], ['circle-cookie', 'COOKIE', 'COOKIES', '🍪'], ['heart-strawberry', 'STRAWBERRY', 'STRAWBERRIES', '🍓'],
    ['star-starfish', 'STARFISH', 'STARFISH', '⭐'], ['circle-orange', 'ORANGE', 'ORANGES', '🍊'], ['square-present', 'PRESENT', 'PRESENTS', '🎁'],
    ['circle-sun', 'SUN', 'SUNS', '☀️'], ['diamond-kite', 'KITE', 'KITES', '🪁'], ['triangle-tree', 'TREE', 'TREES', '🎄'], ['oval-avocado', 'AVOCADO', 'AVOCADOS', '🥑'],
  ];
  // 11-20 count on from a full "ten frame" (ten! eleven, twelve, ...)
  for (let n = 1; n <= 20; n++) {
    const [object, one, many, emoji] = COUNT_OBJECTS[(n * 3 + (n > 10 ? 5 : 0)) % COUNT_OBJECTS.length];
    TOPICS.push({
      id: `count-${n}`, template: 'count', n, word: NUM_WORDS[n], object, objectName: n === 1 ? one : many, emoji,
      strokes: n < 10 ? DIGITS[n] : [...shift(DIGITS[Math.floor(n / 10)], -135), ...shift(DIGITS[n % 10], 140)],
    });
  }

  // ---- ABC: Penny draws the capital letter, then "A is for Apple!" ----
  const O = { stroke: '#3B2B4F', 'stroke-width': 16, 'stroke-linejoin': 'round' }; // outline for object art
  const ART = {
    apple: { fill: [P('M 0 -170 C 80 -250 280 -210 270 -20 C 260 180 120 280 0 230 C -120 280 -260 180 -270 -20 C -280 -210 -80 -250 0 -170 Z', '#F2545B', O)],
      back: [R(-12, -290, 24, 110, '#6B4226', 10)], front: [E(80, -250, 75, 30, '#4CB944', -25)], face: { y: 30, s: 0.9 } },
    egg: { fill: [P(oval(210, 280), '#FFF3D6', O)], back: [], front: [[-90, -150], [80, -60], [-60, 160], [110, 140]].map(([x, y]) => C(x, y, 12, '#E9C9A0')), face: { y: 40, s: 0.8 } },
    fish: { back: [P('M 170 0 L 320 -130 L 320 130 Z', '#FF9F1C', O), P('M -60 -110 L 30 -210 L 90 -100 Z', '#FFB627', O), C(-250, -230, 22, '#B8E0FF'), C(-190, -290, 14, '#B8E0FF')],
      fill: [P('M -270 0 C -270 -180 200 -180 200 0 C 200 180 -270 180 -270 0 Z', '#FF9F1C', O)], front: [line('M 90 -90 Q 120 0 90 90', '#E07A00', 12)], face: { x: -50, y: 0, s: 0.7 } },
    grapes: { back: [line('M 0 -170 L 20 -280', '#6B4226', 18), E(90, -260, 80, 32, '#4CB944', -20)],
      fill: [[-130, -140], [-45, -140], [45, -140], [130, -140], [-90, -40], [0, -40], [90, -40], [-45, 60], [45, 60], [0, 155]].map(([x, y]) => C(x, y, 60, '#9B5DE5', O)),
      front: [], face: { y: -60, s: 0.7 } },
    heart: { fill: [P(heart, '#FF5D8F', O)], back: [], front: [E(-130, -150, 40, 60, '#FFFFFF', 30)], face: { y: 20, s: 0.9 } },
    icecream: { back: [P('M -160 20 L 160 20 L 0 330 Z', '#E8A75D', O), line('M -100 80 L 40 240 M 100 80 L -40 240', '#C98A45', 10)],
      fill: [C(0, -110, 175, '#FFB3C8', O)], front: [P('M -150 -20 Q -120 60 -90 -10 Q -40 70 10 -10 Q 60 60 100 -10 Q 130 50 160 -30', '#FFB3C8'), C(0, -300, 38, '#E63946', O)], face: { y: -120, s: 0.75 } },
    juice: { back: [line('M 70 -200 L 120 -330 L 180 -330', '#4D96FF', 24)], fill: [R(-160, -200, 320, 430, '#FF9F1C', 36, O)],
      front: [R(-160, 60, 320, 110, '#FFFFFF', 0), C(0, 115, 42, '#FFB627')], face: { y: -60, s: 0.8 } },
    lemon: { fill: [P('M -280 0 C -240 -210 240 -210 280 0 C 240 210 -240 210 -280 0 Z', '#FFD23F', O)], back: [], front: [E(120, -170, 80, 30, '#4CB944', -15)], face: { y: 10, s: 0.85 } },
    moon: { fill: [P('M 90 -270 A 280 280 0 1 0 90 270 A 220 220 0 1 1 90 -270 Z', '#FFD23F', O)], back: [], front: [P(star(50, 22, 0), '#FFE873'), P(star(40, 18, 0), '#FFE873')].map(([t, a], i) => [t, { ...a, transform: i ? 'translate(230 160)' : 'translate(200 -150)' }]), face: { x: -130, y: 0, s: 0.6 } },
    nest: { back: [C(-80, -70, 75, '#B8E0FF', O), C(70, -80, 75, '#FFF3D6', O)], fill: [P('M -290 -30 C -270 210 270 210 290 -30 Z', '#A9744F', O)],
      front: [line('M -230 40 L 200 0 M -200 100 L 230 60', '#7A5236', 10)], face: { y: 80, s: 0.65 } },
    queen: { back: [C(0, 50, 265, '#8B5A3C')], fill: [C(0, 50, 220, '#FFD9B8', O)], front: [P('M -170 -140 L -170 -320 L -85 -230 L 0 -340 L 85 -230 L 170 -320 L 170 -140 Z', '#FFD23F', O), C(0, -230, 22, '#E63946'), C(-110, -200, 16, '#4D96FF'), C(110, -200, 16, '#4CB944')], face: { y: 70, s: 0.85 } },
    umbrella: { back: [line('M 0 -10 L 0 230 C 0 300 -90 300 -90 230', '#3B2B4F', 22)],
      fill: [P('M -300 0 C -300 -340 300 -340 300 0 C 250 -40 200 -40 150 0 C 100 -40 50 -40 0 0 C -50 -40 -100 -40 -150 0 C -200 -40 -250 -40 -300 0 Z', '#4D96FF', O)],
      front: [P('M -150 0 C -140 -200 -60 -290 0 -300 C -60 -220 -60 -80 -50 -20 Z', '#7AB2FF'), P('M 150 0 C 140 -200 60 -290 0 -300 C 60 -220 60 -80 50 -20 Z', '#7AB2FF')], face: { y: -130, s: 0.7 } },
    van: { back: [], fill: [R(-300, -180, 600, 290, '#FF6B6B', 50, O)],
      front: [R(-240, -140, 170, 110, '#B8E0FF', 16), R(-40, -140, 170, 110, '#B8E0FF', 16), C(-170, 120, 64, '#3B2B4F'), C(170, 120, 64, '#3B2B4F'), C(-170, 120, 24, '#C9CED6'), C(170, 120, 24, '#C9CED6')], face: { x: 210, y: 0, s: 0.45 } },
    watermelon: { back: [P('M -330 -70 A 330 330 0 0 0 330 -70 Z', '#4CB944', O)], fill: [P('M -290 -70 A 290 290 0 0 0 290 -70 Z', '#FF5D6C', O)],
      front: [[-150, 40], [150, 40], [-70, 140], [70, 140], [0, 60]].map(([x, y]) => E(x, y, 10, 18, '#3B2B4F')), face: { y: 20, s: 0.75 } },
    xylophone: { back: [R(-290, -60, 580, 24, '#8B5A3C', 10), R(-290, 120, 580, 24, '#8B5A3C', 10)],
      fill: ['#FF6B6B', '#FF9F1C', '#FFD23F', '#4CB944', '#4D96FF', '#9B5DE5'].map((c, i) => R(-270 + i * 92, -150 + i * 22, 76, 360 - i * 44, c, 14, O)),
      front: [line('M 120 -230 L 260 -330', '#8B5A3C', 14), C(120, -230, 26, '#FF8FA3')], face: null },
    yoyo: { back: [line('M 0 0 L 0 -340', '#3B2B4F', 8)], fill: [C(0, 20, 240, '#9B5DE5', O)], front: [C(0, 20, 130, '#C9A7F5')], face: { y: 20, s: 0.8 } },
    zebra: { back: [E(-140, -250, 50, 100, '#FFFFFF', -25), E(140, -250, 50, 100, '#FFFFFF', 25), P('M -40 -300 L 0 -360 L 40 -300 Z', '#3B2B4F')],
      fill: [P(oval(210, 280), '#FFFFFF', O)],
      front: [line('M -200 -100 L -110 -80 M -205 -20 L -120 -10 M 200 -100 L 110 -80 M 205 -20 L 120 -10 M -40 -270 L -20 -190 M 40 -270 L 20 -190', '#3B2B4F', 22), E(0, 180, 150, 95, '#C9CED6'), E(-50, 180, 14, 20, '#3B2B4F'), E(50, 180, 14, 20, '#3B2B4F')], face: { y: -20, s: 0.75 } },
  };
  const LETTERS = {
    A: ['M -140 190 L 0 -190 L 140 190', 'M -80 50 L 80 50'],
    B: ['M -110 -190 L -110 190', 'M -110 -190 L 30 -190 C 150 -190 150 0 30 0 L -110 0', 'M -110 0 L 50 0 C 175 0 175 190 50 190 L -110 190'],
    C: ['M 130 -120 C 70 -215 -140 -205 -140 0 C -140 205 70 215 130 120'],
    D: ['M -110 -190 L -110 190', 'M -110 -190 L 0 -190 C 190 -190 190 190 0 190 L -110 190'],
    E: ['M 110 -190 L -110 -190 L -110 190 L 110 190', 'M -110 0 L 70 0'],
    F: ['M 110 -190 L -110 -190 L -110 190', 'M -110 0 L 70 0'],
    G: ['M 130 -120 C 70 -215 -140 -205 -140 0 C -140 205 140 215 140 30 L 20 30'],
    H: ['M -120 -190 L -120 190', 'M 120 -190 L 120 190', 'M -120 0 L 120 0'],
    I: ['M 0 -190 L 0 190', 'M -80 -190 L 80 -190', 'M -80 190 L 80 190'],
    J: ['M 100 -190 L 100 90 C 100 225 -120 225 -120 90'],
    K: ['M -110 -190 L -110 190', 'M 110 -190 L -110 30', 'M -40 -40 L 120 190'],
    L: ['M -100 -190 L -100 190 L 110 190'],
    M: ['M -150 190 L -150 -190 L 0 60 L 150 -190 L 150 190'],
    N: ['M -120 190 L -120 -190 L 120 190 L 120 -190'],
    O: ['M 0 -190 C -190 -190 -190 190 0 190 C 190 190 190 -190 0 -190'],
    P: ['M -110 190 L -110 -190 L 30 -190 C 165 -190 165 20 30 20 L -110 20'],
    Q: ['M 0 -190 C -190 -190 -190 190 0 190 C 190 190 190 -190 0 -190', 'M 50 100 L 160 210'],
    R: ['M -110 190 L -110 -190 L 30 -190 C 165 -190 165 20 30 20 L -110 20', 'M 10 20 L 130 190'],
    S: ['M 120 -130 C 80 -205 -130 -215 -120 -90 C -110 10 120 -10 125 100 C 130 215 -90 225 -130 130'],
    T: ['M -140 -190 L 140 -190', 'M 0 -190 L 0 190'],
    U: ['M -120 -190 L -120 80 C -120 235 120 235 120 80 L 120 -190'],
    V: ['M -140 -190 L 0 190 L 140 -190'],
    W: ['M -175 -190 L -90 190 L 0 -60 L 90 190 L 175 -190'],
    X: ['M -130 -190 L 130 190', 'M 130 -190 L -130 190'],
    Y: ['M -130 -190 L 0 10 L 130 -190', 'M 0 10 L 0 190'],
    Z: ['M -120 -190 L 120 -190 L -120 190 L 120 190'],
  };
  const ABC = [
    ['A', 'APPLE', 'apple', '🍎'], ['B', 'BALLOON', 'oval-balloon', '🎈'], ['C', 'COOKIE', 'circle-cookie', '🍪'], ['D', 'DOOR', 'rectangle-door', '🚪'],
    ['E', 'EGG', 'egg', '🥚'], ['F', 'FISH', 'fish', '🐟'], ['G', 'GRAPES', 'grapes', '🍇'], ['H', 'HEART', 'heart', '❤️'],
    ['I', 'ICE CREAM', 'icecream', '🍦'], ['J', 'JUICE', 'juice', '🧃'], ['K', 'KITE', 'diamond-kite', '🪁'], ['L', 'LEMON', 'lemon', '🍋'],
    ['M', 'MOON', 'moon', '🌙'], ['N', 'NEST', 'nest', '🪺'], ['O', 'ORANGE', 'circle-orange', '🍊'], ['P', 'PIZZA', 'triangle-pizza', '🍕'],
    ['Q', 'QUEEN', 'queen', '👑'], ['R', 'ROBOT', 'square-robot', '🤖'], ['S', 'SUN', 'circle-sun', '☀️'], ['T', 'TREE', 'triangle-tree', '🌳'],
    ['U', 'UMBRELLA', 'umbrella', '☂️'], ['V', 'VAN', 'van', '🚐'], ['W', 'WATERMELON', 'watermelon', '🍉'], ['X', 'XYLOPHONE', 'xylophone', '🎶'],
    ['Y', 'YO-YO', 'yoyo', '🪀'], ['Z', 'ZEBRA', 'zebra', '🦓'],
  ];
  for (const [letter, word, art, emoji] of ABC) {
    TOPICS.push({ id: `abc-${letter.toLowerCase()}`, template: 'abc', letter, word, art, artData: ART[art] || null, emoji, strokes: LETTERS[letter] });
  }

  // ---- Animals: "Who says moo?" — Ellie erases the scribbles to reveal the animal ----
  const EO = (cx, cy, rx, ry, fill, rot = 0) => ['ellipse', { cx, cy, rx, ry, fill, transform: `rotate(${rot} ${cx} ${cy})`, ...O }];
  const CO = (cx, cy, r, fill) => ['circle', { cx, cy, r, fill, ...O }];
  const mirror = (d) => d.replace(/(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)/g, (m, x, y) => `${-x} ${y}`);
  const MOUTH_W = (y) => line(`M -40 ${y} Q -20 ${y + 25} 0 ${y} Q 20 ${y + 25} 40 ${y}`, '#3B2B4F', 9);
  const whiskers = (y) => line(`M -110 ${y} L -250 ${y - 30} M -110 ${y + 30} L -250 ${y + 40} M 110 ${y} L 250 ${y - 30} M 110 ${y + 30} L 250 ${y + 40}`, '#3B2B4F', 7);
  const earL = (d, f) => [P(d, f, O), P(mirror(d), f, O)];
  const ANIMAL_ART = {
    cow: { back: [...earL('M -150 -230 C -190 -310 -150 -340 -110 -280 Z', '#FFF3D6'), EO(-250, -140, 85, 40, '#F6C1C9', -20), EO(250, -140, 85, 40, '#F6C1C9', 20)],
      fill: [P(oval(230, 270), '#FFFFFF', O)],
      front: [C(150, -170, 60, '#3B2B4F'), C(-185, 40, 40, '#3B2B4F'), EO(0, 170, 175, 100, '#F6C1C9'), E(-55, 165, 15, 24, '#3B2B4F'), E(55, 165, 15, 24, '#3B2B4F'), line('M -45 220 Q 0 245 45 220', '#3B2B4F', 9)],
      face: { y: -60, s: 0.8, mouth: false } },
    dog: { back: [EO(-215, -50, 70, 150, '#8B5A3C', 15), EO(215, -50, 70, 150, '#8B5A3C', -15)], fill: [CO(0, 0, 230, '#D9A066')],
      front: [E(0, 115, 120, 85, '#F5DEC0'), E(0, 75, 38, 28, '#3B2B4F'), MOUTH_W(125)], face: { y: -50, s: 0.8, mouth: false } },
    cat: { back: earL('M -205 -110 L -175 -320 L -60 -205 Z', '#FF9F1C'), fill: [CO(0, 0, 230, '#FFB627')],
      front: [whiskers(80), P('M -26 60 L 26 60 L 0 88 Z', '#FF8FA3'), MOUTH_W(100)], face: { y: -60, s: 0.8, mouth: false } },
    pig: { back: earL('M -205 -130 L -145 -295 L -70 -190 Z', '#FF8FB1'), fill: [CO(0, 0, 235, '#FFB3C8')],
      front: [EO(0, 80, 95, 65, '#FF8FB1'), E(-30, 80, 14, 22, '#3B2B4F'), E(30, 80, 14, 22, '#3B2B4F'), line('M -50 170 Q 0 200 50 170', '#3B2B4F', 9)], face: { y: -90, s: 0.8, mouth: false } },
    sheep: { back: ring(12, (i, a) => CO(Math.cos(a) * 225, Math.sin(a) * 225 - 10, 88, '#FFFFFF')), fill: [P(oval(150, 190), '#F5DEC0', O)],
      front: [EO(-175, -20, 70, 32, '#F5DEC0', -20), EO(175, -20, 70, 32, '#F5DEC0', 20), CO(-60, -190, 60, '#FFFFFF'), CO(30, -205, 66, '#FFFFFF')], face: { y: 10, s: 0.62 } },
    duck: { back: [line('M 0 -225 Q 15 -295 55 -280', '#E0B000', 14)], fill: [CO(0, 0, 230, '#FFD23F')],
      front: [EO(0, 95, 125, 52, '#FF9F1C'), line('M -115 95 L 115 95', '#E07A00', 7)], face: { y: -80, s: 0.8, mouth: false } },
    horse: { back: earL('M -150 -230 L -120 -345 L -60 -255 Z', '#8B5A3C'), fill: [P(oval(190, 290), '#A9744F', O)],
      front: [P('M -70 -275 C -30 -345 60 -335 85 -260 L 40 -205 Z', '#3B2B4F'), EO(0, 180, 150, 100, '#D9A066'), E(-50, 175, 14, 22, '#3B2B4F'), E(50, 175, 14, 22, '#3B2B4F'), line('M -40 235 Q 0 260 40 235', '#3B2B4F', 9)],
      face: { y: -90, s: 0.75, mouth: false } },
    chicken: { back: [P('M -60 -215 C -75 -300 -10 -315 0 -250 C 10 -325 75 -305 60 -225 Z', '#E63946', O)], fill: [CO(0, 0, 230, '#FFFFFF')],
      front: [P('M -45 65 L 45 65 L 0 135 Z', '#FF9F1C', O), EO(0, 172, 26, 38, '#E63946')], face: { y: -80, s: 0.8, mouth: false } },
    lion: { back: [...ring(14, (i, a) => C(Math.cos(a) * 235, Math.sin(a) * 235, 92, i % 2 ? '#E07A00' : '#FF9F1C')), CO(-170, -170, 52, '#FFB627'), CO(170, -170, 52, '#FFB627')],
      fill: [CO(0, 0, 220, '#FFD23F')], front: [E(0, 100, 115, 75, '#FFF3D6'), P('M -35 55 L 35 55 L 0 95 Z', '#8B5A3C'), MOUTH_W(120)], face: { y: -60, s: 0.8, mouth: false } },
    frog: { back: [CO(-115, -170, 92, '#4CB944'), CO(115, -170, 92, '#4CB944')],
      fill: [P('M -285 40 C -285 -185 285 -185 285 40 C 285 225 -285 225 -285 40 Z', '#4CB944', O)],
      front: [line('M -150 60 Q 0 165 150 60', '#3B2B4F', 12)], face: { y: -140, s: 0.95, mouth: false } },
    mouse: { back: [CO(-185, -165, 110, '#C9CED6'), CO(185, -165, 110, '#C9CED6'), C(-185, -165, 64, '#FFB3C8'), C(185, -165, 64, '#FFB3C8')],
      fill: [CO(0, 20, 210, '#C9CED6')], front: [whiskers(110), C(0, 105, 26, '#FF8FA3'), MOUTH_W(140)], face: { y: -40, s: 0.75, mouth: false } },
    owl: { back: earL('M -180 -195 L -150 -335 L -80 -245 Z', '#A9744F'), fill: [P(oval(220, 280), '#A9744F', O)],
      front: [E(0, 145, 140, 110, '#F5DEC0'), CO(-90, -60, 88, '#FFFFFF'), CO(90, -60, 88, '#FFFFFF'), P('M -25 25 L 25 25 L 0 75 Z', '#FF9F1C', O)],
      face: { y: -20, s: 0.95, mouth: false } },

    // --- second set (added 2026-11-21) ---
    bear: { back: [CO(-170, -185, 75, '#8B5A3C'), CO(170, -185, 75, '#8B5A3C'), C(-170, -185, 38, '#D9A066'), C(170, -185, 38, '#D9A066')], fill: [CO(0, 0, 230, '#8B5A3C')],
      front: [E(0, 110, 115, 82, '#D9A066'), E(0, 72, 38, 27, '#3B2B4F'), MOUTH_W(128)], face: { y: -60, s: 0.8, mouth: false } },
    monkey: { back: [CO(-232, -10, 72, '#8B5A3C'), CO(232, -10, 72, '#8B5A3C'), C(-232, -10, 40, '#F5DEC0'), C(232, -10, 40, '#F5DEC0')], fill: [CO(0, 0, 220, '#8B5A3C')],
      front: [E(-68, -45, 88, 100, '#F5DEC0'), E(68, -45, 88, 100, '#F5DEC0'), E(0, 100, 150, 92, '#F5DEC0'), E(-22, 78, 9, 13, '#3B2B4F'), E(22, 78, 9, 13, '#3B2B4F'), line('M -60 128 Q 0 175 60 128', '#3B2B4F', 9)],
      face: { y: -55, s: 0.7, mouth: false } },
    elephant: { back: [EO(-225, -30, 125, 165, '#B8C4D6', -10), EO(225, -30, 125, 165, '#B8C4D6', 10), E(-225, -30, 80, 115, '#FFB3C8'), E(225, -30, 80, 115, '#FFB3C8')], fill: [CO(0, -20, 200, '#C9D3E2')],
      front: [P('M -45 60 C -50 200 -10 285 60 272 C 92 266 92 232 60 234 C 28 238 28 190 45 60 Z', '#C9D3E2', O)], face: { y: -85, s: 0.75, mouth: false } },
    bee: { back: [EO(-120, -215, 90, 58, '#DDF3FF', -30), EO(120, -215, 90, 58, '#DDF3FF', 30), line('M -60 -195 Q -90 -285 -130 -300 M 60 -195 Q 90 -285 130 -300', '#3B2B4F', 10),
      C(-132, -302, 18, '#3B2B4F'), C(132, -302, 18, '#3B2B4F')], fill: [P(oval(270, 210), '#FFD23F', O)],
      front: [line('M 165 -150 Q 190 0 165 150', '#3B2B4F', 40), line('M -165 -150 Q -190 0 -165 150', '#3B2B4F', 40)], face: { y: -15, s: 0.75 } },
    snake: { fill: [EO(0, 175, 270, 110, '#6BCB77'), CO(0, -60, 170, '#7ED957')],
      front: [line('M 0 75 L 0 140 M 0 140 L -22 170 M 0 140 L 22 170', '#E63946', 8), C(-160, 175, 22, '#3FA34D'), C(160, 175, 22, '#3FA34D'), C(-60, 240, 18, '#3FA34D'), C(70, 240, 18, '#3FA34D'),
        line('M -45 25 Q 0 55 45 25', '#3B2B4F', 9)], face: { y: -95, s: 0.7, mouth: false } },
    goat: { back: [line('M -80 -200 C -120 -300 -60 -345 -30 -260', '#C9A36A', 30), line('M 80 -200 C 120 -300 60 -345 30 -260', '#C9A36A', 30),
      EO(-215, -60, 90, 38, '#E8DCC8', 20), EO(215, -60, 90, 38, '#E8DCC8', -20)], fill: [P(oval(190, 260), '#F5F0E6', O)],
      front: [P('M -40 225 L 0 330 L 40 225 Z', '#E8DCC8', O), E(0, 150, 100, 70, '#F0E0D0'), E(-28, 140, 10, 15, '#3B2B4F'), E(28, 140, 10, 15, '#3B2B4F'), line('M -35 190 Q 0 210 35 190', '#3B2B4F', 8)],
      face: { y: -70, s: 0.75, mouth: false } },
    donkey: { back: [EO(-115, -255, 45, 130, '#9A9AA8', -15), EO(115, -255, 45, 130, '#9A9AA8', 15), E(-115, -255, 20, 90, '#FFB3C8', -15), E(115, -255, 20, 90, '#FFB3C8', 15)],
      fill: [P(oval(190, 280), '#A8A8B8', O)], front: [EO(0, 170, 150, 100, '#E0E0E8'), E(-50, 165, 14, 22, '#3B2B4F'), E(50, 165, 14, 22, '#3B2B4F'), line('M -40 228 Q 0 252 40 228', '#3B2B4F', 9)],
      face: { y: -85, s: 0.75, mouth: false } },
    bird: { back: [P('M -20 -220 C -45 -305 25 -325 12 -248 Z', '#4D96FF', O)], fill: [CO(0, 0, 230, '#4D96FF')],
      front: [E(0, 125, 150, 95, '#BDE6FF'), P('M -40 40 L 40 40 L 0 98 Z', '#FF9F1C', O)], face: { y: -60, s: 0.8, mouth: false } },
    rooster: { back: [P('M -80 -205 C -100 -310 -30 -330 -15 -255 C -5 -345 70 -340 55 -255 C 90 -320 140 -280 100 -205 Z', '#E63946', O)], fill: [CO(0, 0, 230, '#FF9F1C')],
      front: [P('M -45 50 L 45 50 L 0 112 Z', '#FFD23F', O), EO(-14, 165, 24, 36, '#E63946'), EO(18, 163, 22, 32, '#E63946')], face: { y: -75, s: 0.8, mouth: false } },
    wolf: { back: earL('M -200 -115 L -160 -330 L -60 -200 Z', '#7D8597'), fill: [CO(0, 0, 230, '#9AA3B5')],
      front: [E(0, 112, 120, 85, '#E5E8EE'), E(0, 72, 40, 28, '#3B2B4F'), MOUTH_W(132)], face: { y: -60, s: 0.8, mouth: false } },
  };
  const ANIMALS = [
    ['cow', 'COW', 'a', 'Moo!', 'MOO', '🐮'], ['dog', 'DOG', 'a', 'Woof woof!', 'WOOF', '🐶'], ['cat', 'CAT', 'a', 'Meow!', 'MEOW', '🐱'],
    ['duck', 'DUCK', 'a', 'Quack quack!', 'QUACK', '🦆'], ['pig', 'PIG', 'a', 'Oink oink!', 'OINK', '🐷'], ['sheep', 'SHEEP', 'a', 'Baa!', 'BAA', '🐑'],
    ['lion', 'LION', 'a', 'Roar!', 'ROAR', '🦁'], ['frog', 'FROG', 'a', 'Ribbit!', 'RIBBIT', '🐸'], ['horse', 'HORSE', 'a', 'Neigh!', 'NEIGH', '🐴'],
    ['chicken', 'CHICKEN', 'a', 'Cluck cluck!', 'CLUCK', '🐔'], ['owl', 'OWL', 'an', 'Hoo hoo!', 'HOO HOO', '🦉'], ['mouse', 'MOUSE', 'a', 'Squeak squeak!', 'SQUEAK', '🐭'],
    ['bear', 'BEAR', 'a', 'Grrr!', 'GRRR', '🐻'], ['monkey', 'MONKEY', 'a', 'Ooh ooh, ah ah!', 'OOH AH', '🐵'], ['elephant', 'ELEPHANT', 'an', 'Toot toot!', 'TOOT', '🐘'],
    ['bee', 'BEE', 'a', 'Buzz buzz!', 'BUZZ', '🐝'], ['snake', 'SNAKE', 'a', 'Hiss!', 'HISS', '🐍'], ['goat', 'GOAT', 'a', 'Maa!', 'MAA', '🐐'],
    ['donkey', 'DONKEY', 'a', 'Hee-haw!', 'HEE-HAW', '🫏'], ['bird', 'BIRD', 'a', 'Tweet tweet!', 'TWEET', '🐦'], ['rooster', 'ROOSTER', 'a', 'Cock-a-doodle-doo!', 'COCK-A-DOO', '🐓'],
    ['wolf', 'WOLF', 'a', 'Awoo!', 'AWOO', '🐺'],
  ];
  for (const [key, word, article, sound, soundText, emoji] of ANIMALS) {
    TOPICS.push({ id: `animal-${key}`, template: 'animal', word, article, sound, soundText, emoji, artData: ANIMAL_ART[key] });
  }

  // ---- Vehicles: "Who says beep beep?" — same scene as the animals (Ellie erases the scribbles) ----
  const RO = (x, y, w, h, fill, rx = 16) => R(x, y, w, h, fill, rx, O);
  const wheel = (x, y, r = 60) => [CO(x, y, r, '#3B2B4F'), C(x, y, r * 0.4, '#C9CED6')];
  const VEHICLE_ART = {
    car: { fill: [P('M -280 80 L -280 0 Q -280 -30 -240 -30 L -160 -30 L -100 -140 L 110 -140 L 170 -30 L 250 -30 Q 290 -30 290 10 L 290 80 Z', '#FF6B6B', O)],
      front: [P('M -80 -45 L -45 -120 L 95 -120 L 135 -45 Z', '#BDE6FF', O), C(265, 20, 16, '#FFD23F'), ...wheel(-160, 90), ...wheel(165, 90)], face: { x: 25, y: -85, s: 0.28, mouth: false } },
    bus: { fill: [RO(-300, -200, 600, 300, '#FFD23F', 40)],
      front: [RO(-260, -165, 95, 90, '#BDE6FF', 12), RO(-145, -165, 95, 90, '#BDE6FF', 12), RO(-30, -165, 95, 90, '#BDE6FF', 12), RO(190, -165, 80, 250, '#BDE6FF', 12),
        R(-300, 10, 490, 24, '#FF9F1C', 0), ...wheel(-170, 110, 58), ...wheel(150, 110, 58)], face: { x: -40, y: 50, s: 0.38 } },
    firetruck: { fill: [RO(-300, -120, 420, 200, '#E63946', 20), RO(100, -180, 200, 260, '#E63946', 24)],
      front: [RO(150, -150, 110, 90, '#BDE6FF', 12), line('M -280 -150 L 70 -150 M -280 -190 L 70 -190 M -240 -190 L -240 -150 M -170 -190 L -170 -150 M -100 -190 L -100 -150 M -30 -190 L -30 -150 M 40 -190 L 40 -150', '#C9CED6', 12),
        CO(200, -205, 24, '#4D96FF'), ...wheel(-190, 100), ...wheel(190, 100)], face: { x: 205, y: 20, s: 0.28, mouth: false } },
    policecar: { fill: [P('M -280 80 L -280 0 Q -280 -30 -240 -30 L -160 -30 L -100 -140 L 110 -140 L 170 -30 L 250 -30 Q 290 -30 290 10 L 290 80 Z', '#4D96FF', O)],
      front: [R(-280, 10, 570, 34, '#FFFFFF', 0), P('M -80 -45 L -45 -120 L 95 -120 L 135 -45 Z', '#BDE6FF', O), RO(-20, -185, 70, 40, '#FF6B6B', 10), ...wheel(-160, 90), ...wheel(165, 90)],
      face: { x: 25, y: -85, s: 0.28, mouth: false } },
    ambulance: { fill: [RO(-290, -180, 560, 260, '#FFFFFF', 30)],
      front: [RO(140, -150, 110, 90, '#BDE6FF', 12), P('M -125 -110 h 50 v 50 h 50 v 50 h -50 v 50 h -50 v -50 h -50 v -50 h 50 z', '#E63946'), CO(-200, -200, 24, '#E63946'),
        R(-290, 30, 560, 22, '#E63946', 0), ...wheel(-170, 100), ...wheel(170, 100)], face: { x: 195, y: -5, s: 0.25, mouth: false } },
    train: { fill: [RO(-260, -60, 340, 160, '#3DAA3D', 30), RO(60, -200, 210, 300, '#E63946', 20)],
      front: [RO(100, -165, 130, 90, '#BDE6FF', 12), P('M -210 -60 L -230 -170 L -130 -170 L -150 -60 Z', '#3B2B4F', O), ...wheel(-180, 120, 55), ...wheel(-40, 120, 55), ...wheel(165, 120, 72)],
      face: { x: -90, y: 15, s: 0.35 } },
    airplane: { back: [P('M -60 -20 L 30 -20 L -60 -170 L -130 -170 Z', '#4D96FF', O), P('M -250 -20 L -300 -170 L -220 -170 L -170 -40 Z', '#FF6B6B', O)],
      fill: [EO(0, 0, 300, 90, '#FFFFFF')],
      front: [P('M -60 10 L 40 10 L -40 210 L -120 210 Z', '#4D96FF', O), C(-120, -10, 18, '#BDE6FF'), C(-60, -10, 18, '#BDE6FF'), C(0, -10, 18, '#BDE6FF')], face: { x: 195, y: -5, s: 0.25, mouth: false } },
    boat: { back: [RO(40, -230, 60, 110, '#FFD23F', 10)], fill: [P('M -290 20 L 290 20 L 220 160 L -220 160 Z', '#FF6B6B', O), RO(-150, -130, 260, 150, '#FFFFFF', 20)],
      front: [CO(-60, -55, 32, '#BDE6FF'), CO(30, -55, 32, '#BDE6FF'), line('M -320 200 Q -270 170 -220 200 Q -170 230 -120 200 Q -70 170 -20 200 Q 30 230 80 200 Q 130 170 180 200 Q 230 230 280 200', '#4D96FF', 14)],
      face: { x: 0, y: 85, s: 0.32 } },
    tractor: { back: [RO(120, -170, 30, 110, '#3B2B4F', 8)], fill: [RO(-120, -60, 310, 140, '#3DAA3D', 20), RO(-170, -230, 180, 200, '#3DAA3D', 16)],
      front: [RO(-140, -200, 120, 100, '#BDE6FF', 10), CO(-120, 120, 110, '#3B2B4F'), C(-120, 120, 45, '#FFD23F'), CO(200, 150, 72, '#3B2B4F'), C(200, 150, 28, '#FFD23F')],
      face: { x: 100, y: 5, s: 0.3, mouth: false } },
    helicopter: { back: [line('M -280 -205 L 280 -205', '#3B2B4F', 16), R(-10, -205, 20, 60, '#3B2B4F', 4), line('M -150 195 L 170 195 M -90 195 L -70 140 M 110 195 L 90 140', '#3B2B4F', 14)],
      fill: [P('M -180 -30 L -330 -60 L -330 0 L -180 40 Z', '#FFD23F', O), EO(0, 0, 220, 150, '#FFD23F')],
      front: [EO(105, -15, 92, 90, '#BDE6FF')], face: { x: 105, y: -20, s: 0.33 } },
    rocket: { fill: [P('M -90 80 L -190 230 L -90 200 Z', '#E63946', O), P('M 90 80 L 190 230 L 90 200 Z', '#E63946', O), P('M -60 200 Q 0 330 60 200 Z', '#FF9F1C', O),
      P('M 0 -320 C 120 -200 120 120 90 200 L -90 200 C -120 120 -120 -200 0 -320 Z', '#FFFFFF', O)],
      front: [CO(0, -110, 72, '#BDE6FF')], face: { x: 0, y: -115, s: 0.3 } },
    truck: { fill: [P('M -300 -120 L 100 -120 L 100 80 L -280 80 Z', '#FFD23F', O), RO(110, -180, 180, 260, '#FF9F1C', 20)],
      front: [RO(150, -150, 110, 90, '#BDE6FF', 12), ...wheel(-170, 100), ...wheel(190, 100)], face: { x: 200, y: 25, s: 0.28 } },
  };
  const VEHICLES = [
    ['car', 'CAR', 'a', 'Beep beep!', 'BEEP BEEP', '🚗'], ['firetruck', 'FIRE TRUCK', 'a', 'Wee-woo, wee-woo!', 'WEE-WOO', '🚒'], ['train', 'TRAIN', 'a', 'Choo choo!', 'CHOO CHOO', '🚂'],
    ['airplane', 'AIRPLANE', 'an', 'Zoom zoom!', 'ZOOM', '✈️'], ['bus', 'BUS', 'a', 'Honk honk!', 'HONK', '🚌'], ['boat', 'BOAT', 'a', 'Toot toot!', 'TOOT', '⛵'],
    ['policecar', 'POLICE CAR', 'a', 'Nee-naw, nee-naw!', 'NEE-NAW', '🚓'], ['tractor', 'TRACTOR', 'a', 'Chug chug!', 'CHUG', '🚜'], ['helicopter', 'HELICOPTER', 'a', 'Whirr whirr!', 'WHIRR', '🚁'],
    ['ambulance', 'AMBULANCE', 'an', 'Wee-oo, wee-oo!', 'WEE-OO', '🚑'], ['rocket', 'ROCKET', 'a', 'Whoosh!', 'WHOOSH', '🚀'], ['truck', 'TRUCK', 'a', 'Vroom vroom!', 'VROOM', '🚚'],
  ];
  for (const [key, word, article, sound, soundText, emoji] of VEHICLES) {
    TOPICS.push({ id: `vehicle-${key}`, template: 'vehicle', word, article, sound, soundText, emoji, artData: VEHICLE_ART[key] });
  }

  // ---- Color mixing: two paint blobs + Coco stirring = a new colour (and something of that colour) ----
  {
    const K = { RED: '#F2454B', YELLOW: '#FFC928', BLUE: '#3D86F0', WHITE: '#F7F7F7', BLACK: '#2B2B35', GREEN: '#3DAA3D',
      ORANGE: '#FF8A1C', PURPLE: '#8A4FD6', PINK: '#FF8FB8', 'LIGHT BLUE': '#9DD3FF', GRAY: '#9A9AA8', BROWN: '#9A6338' };
    const col = n => ({ name: n, hex: K[n] });
    const MIXES = [
      ['RED', 'YELLOW', 'ORANGE', 'circle-orange', 'an orange', '🍊'], ['BLUE', 'YELLOW', 'GREEN', 'triangle-tree', 'a tree', '🌳'],
      ['RED', 'BLUE', 'PURPLE', 'abc-g', 'grapes', '🍇'], ['RED', 'WHITE', 'PINK', 'animal-pig', 'a pig', '🐷'],
      ['BLUE', 'WHITE', 'LIGHT BLUE', 'abc-u', 'an umbrella', '☂️'], ['BLACK', 'WHITE', 'GRAY', 'animal-elephant', 'an elephant', '🐘'],
      ['RED', 'GREEN', 'BROWN', 'animal-bear', 'a bear', '🐻'], ['YELLOW', 'RED', 'ORANGE', 'animal-lion', 'a lion', '🦁'],
    ];
    for (const [a, b, c, object, like, emoji] of MIXES)
      TOPICS.push({ id: `colormix-${a.toLowerCase()}-${b.toLowerCase()}`, template: 'colormix', a: col(a), b: col(b), c: col(c), object, like, emoji, word: c });
  }

  // ---- Colors: Coco colours a grey object, then two more things of that colour ----
  const COLORS_T = [
    ['RED', '#F2454B', '🍎', ['abc-a', 'apple'], ['heart-strawberry', 'strawberry'], ['abc-h', 'heart']],
    ['ORANGE', '#FF8A1C', '🍊', ['circle-orange', 'orange'], ['abc-j', 'juice box'], ['animal-cat', 'cat']],
    ['YELLOW', '#FFC928', '🍋', ['abc-l', 'lemon'], ['circle-sun', 'sun'], ['animal-duck', 'duck']],
    ['GREEN', '#3DAA3D', '🌳', ['triangle-tree', 'tree'], ['animal-frog', 'frog'], ['oval-avocado', 'avocado']],
    ['BLUE', '#3D86F0', '☂️', ['abc-u', 'umbrella'], ['diamond-kite', 'kite'], ['square-robot', 'robot']],
    ['PURPLE', '#8A4FD6', '🍇', ['abc-g', 'grapes'], ['abc-y', 'yo-yo'], ['star-starfish', null]],
    ['PINK', '#FF6FA8', '🐷', ['animal-pig', 'pig'], ['oval-balloon', 'balloon'], ['abc-i', 'ice cream']],
    ['BROWN', '#9A6338', '🚪', ['rectangle-door', 'door'], ['circle-cookie', 'cookie'], ['abc-n', 'nest']],
    ['WHITE', '#F4F4F4', '🥚', ['abc-e', 'egg'], ['animal-sheep', 'sheep'], ['animal-cow', 'cow']],
  ];
  for (const [color, hex, emoji, main, x1, x2] of COLORS_T) {
    const extras = [x1, x2].filter(x => x[1]);
    TOPICS.push({ id: `color-${color.toLowerCase()}`, template: 'color', word: color, hex, emoji, main: main[0], mainName: main[1], extras });
  }


  // ---- Let's Draw: step-by-step easy drawing of animals and things (Penny draws, Coco colours) ----
  // Each step: what the narrator says, the short caption shown, and the strokes drawn (centre of the card is 0,0).
  const circ = (cx, cy, r) => `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.01} ${cy - r}`;
  const dot = (cx, cy) => circ(cx, cy, 9); // drawn with a thick pen: a solid dot (eyes)
  const st = (say, show, paths, w) => ({ say, show, paths, ...(w ? { w } : {}) });
  const DRAW_TOPICS = [
    { word: 'CAT', article: 'a', emoji: '🐱', steps: [
      st('Draw a big circle for the head.', 'A big circle', [circ(0, -20, 170)]),
      st('Add two pointy ears.', 'Two pointy ears', ['M -150 -100 L -135 -265 L -45 -180', 'M 150 -100 L 135 -265 L 45 -180']),
      st('Two eyes, and a little nose.', 'Eyes and nose', [dot(-60, -50), dot(60, -50), 'M -20 15 L 20 15 L 0 38 Z']),
      st('A happy smile!', 'A happy smile', ['M 0 38 Q -30 80 -65 55', 'M 0 38 Q 30 80 65 55']),
      st('And long whiskers!', 'Whiskers', ['M -95 25 L -240 0', 'M -95 50 L -240 65', 'M 95 25 L 240 0', 'M 95 50 L 240 65']),
    ], fills: [[circ(0, -20, 170), '#FFB347'], ['M -150 -100 L -135 -265 L -45 -180 Z', '#FFB347'], ['M 150 -100 L 135 -265 L 45 -180 Z', '#FFB347'], ['M -20 15 L 20 15 L 0 38 Z', '#FF8FA3']] },
    { word: 'FISH', article: 'a', emoji: '🐟', steps: [
      st('Draw a long oval for the body.', 'A long oval', ['M -190 0 C -120 -150 120 -140 170 0 C 120 140 -120 150 -190 0 Z']),
      st('Add a triangle tail.', 'A triangle tail', ['M 165 0 L 290 -110 L 290 110 Z']),
      st('An eye, and a little mouth.', 'Eye and mouth', [dot(-95, -30), 'M -165 25 Q -140 45 -115 30']),
      st('Draw some stripes.', 'Stripes', ['M -20 -105 Q 15 0 -20 105', 'M 60 -95 Q 95 0 60 95']),
      st('And bubbles! Blub, blub!', 'Bubbles', [circ(-270, -120, 22), circ(-310, -215, 15)]),
    ], fills: [['M -190 0 C -120 -150 120 -140 170 0 C 120 140 -120 150 -190 0 Z', '#4D96FF'], ['M 165 0 L 290 -110 L 290 110 Z', '#FFC93C'], [circ(-270, -120, 22), '#BDE6FF'], [circ(-310, -215, 15), '#BDE6FF']] },
    { word: 'HOUSE', article: 'a', emoji: '🏠', steps: [
      st('Draw a big square.', 'A big square', ['M -200 -30 L 200 -30 L 200 270 L -200 270 Z']),
      st('Put a triangle roof on top.', 'A triangle roof', ['M -250 -30 L 0 -270 L 250 -30 Z']),
      st('Draw a door.', 'A door', ['M -50 270 L -50 120 L 50 120 L 50 270', dot(30, 200)]),
      st('Two square windows.', 'Two windows', ['M -165 30 L -85 30 L -85 110 L -165 110 Z', 'M 85 30 L 165 30 L 165 110 L 85 110 Z']),
      st('And a chimney!', 'A chimney', ['M 115 -140 L 115 -240 L 175 -240 L 175 -85']),
    ], fills: [['M -200 -30 L 200 -30 L 200 270 L -200 270 Z', '#FFD6A5'], ['M -250 -30 L 0 -270 L 250 -30 Z', '#FF6B6B'], ['M -50 270 L -50 120 L 50 120 L 50 270 Z', '#9B5DE5'],
      ['M -165 30 L -85 30 L -85 110 L -165 110 Z', '#A0E7FF'], ['M 85 30 L 165 30 L 165 110 L 85 110 Z', '#A0E7FF'], ['M 115 -140 L 115 -240 L 175 -240 L 175 -85 Z', '#C97B4A']] },
    { word: 'FLOWER', article: 'a', emoji: '🌸', steps: [
      st('Draw a small circle in the middle.', 'A small circle', [circ(0, -110, 55)]),
      st('Now draw round petals, all around.', 'Round petals', [0, 1, 2, 3, 4].map(i => circ(Math.round(118 * Math.cos(i * 1.2566 - 1.5708)), Math.round(-110 + 118 * Math.sin(i * 1.2566 - 1.5708)), 62))),
      st('Draw a long stem.', 'A long stem', ['M 0 0 L 0 300']),
      st('And two leaves!', 'Two leaves', ['M 0 190 C 50 120 130 130 160 150 C 120 200 50 205 0 190 Z', 'M 0 250 C -50 180 -130 190 -160 210 C -120 260 -50 265 0 250 Z']),
    ], fills: [...[0, 1, 2, 3, 4].map(i => [circ(Math.round(118 * Math.cos(i * 1.2566 - 1.5708)), Math.round(-110 + 118 * Math.sin(i * 1.2566 - 1.5708)), 62), '#F15BB5']), [circ(0, -110, 55), '#FFC93C'],
      ['M 0 190 C 50 120 130 130 160 150 C 120 200 50 205 0 190 Z', '#6BCB77'], ['M 0 250 C -50 180 -130 190 -160 210 C -120 260 -50 265 0 250 Z', '#6BCB77']] },
    { word: 'SNAIL', article: 'a', emoji: '🐌', steps: [
      st('Draw a big circle for the shell.', 'A big circle', [circ(40, -20, 150)]),
      st('Now a swirl inside. Round and round!', 'A swirl', ['M 40 -20 C 40 -50 80 -50 80 -20 C 80 30 0 30 0 -20 C 0 -90 120 -90 120 -20 C 120 70 -40 70 -40 -20 C -40 -120 150 -130 160 -20']),
      st('Draw a long body.', 'A long body', ['M -240 130 C -290 130 -290 40 -230 40 C -200 40 -190 110 -110 120 L 230 130 C 270 135 260 160 230 160 L -230 160 C -260 160 -260 130 -240 130']),
      st('Two eyes on top!', 'Eyes on stalks', ['M -250 50 L -285 -50', 'M -215 45 L -205 -55', dot(-288, -60), dot(-203, -65)]),
      st('And a smile!', 'A smile', ['M -275 95 Q -255 115 -235 100']),
    ], fills: [['M -240 130 C -290 130 -290 40 -230 40 C -200 40 -190 110 -110 120 L 230 130 C 270 135 260 160 230 160 L -230 160 C -260 160 -260 130 -240 130 Z', '#B8E986'], [circ(40, -20, 150), '#FF9F1C']] },
    { word: 'CAR', article: 'a', emoji: '🚗', steps: [
      st('Draw the body of the car.', 'The body', ['M -280 100 L -280 20 Q -280 -10 -245 -10 L -150 -10 L -95 -110 L 110 -110 L 170 -10 L 250 -10 Q 290 -10 290 30 L 290 100 Z']),
      st('Add two windows.', 'Two windows', ['M -120 -25 L -80 -90 L -15 -90 L -15 -25 Z', 'M 15 -25 L 15 -90 L 95 -90 L 135 -25 Z']),
      st('Two round wheels.', 'Two wheels', [circ(-160, 110, 62), circ(165, 110, 62)]),
      st('And a light. Beep, beep!', 'A light', [circ(260, 30, 16), dot(-160, 110), dot(165, 110)]),
    ], fills: [['M -280 100 L -280 20 Q -280 -10 -245 -10 L -150 -10 L -95 -110 L 110 -110 L 170 -10 L 250 -10 Q 290 -10 290 30 L 290 100 Z', '#FF6B6B'],
      ['M -120 -25 L -80 -90 L -15 -90 L -15 -25 Z', '#A0E7FF'], ['M 15 -25 L 15 -90 L 95 -90 L 135 -25 Z', '#A0E7FF'], [circ(-160, 110, 62), '#5B5B6B'], [circ(165, 110, 62), '#5B5B6B'], [circ(260, 30, 16), '#FFC93C']] },
    { word: 'BIRD', article: 'a', emoji: '🐦', steps: [
      st('Draw a big circle for the body.', 'A big circle', [circ(0, -10, 150)]),
      st('Add a pointy beak, and an eye.', 'Beak and eye', ['M 140 -50 L 225 -15 L 140 20', dot(70, -60)]),
      st('Draw a wing.', 'A wing', ['M -80 10 Q -10 120 90 30 Q 10 -10 -80 10 Z']),
      st('A little tail.', 'A tail', ['M -145 -40 L -245 -100 L -235 10 Z']),
      st('And two thin legs!', 'Two legs', ['M -35 138 L -35 230 M -65 230 L -5 230', 'M 35 138 L 35 230 M 5 230 L 65 230']),
    ], fills: [['M -145 -40 L -245 -100 L -235 10 Z', '#4D96FF'], [circ(0, -10, 150), '#4D96FF'], ['M 140 -50 L 225 -15 L 140 20 Z', '#FF9F1C'], ['M -80 10 Q -10 120 90 30 Q 10 -10 -80 10 Z', '#A0C8FF']] },
    { word: 'BUTTERFLY', article: 'a', emoji: '🦋', steps: [
      st('Draw a long body in the middle.', 'A long body', ['M 0 -170 C 35 -170 35 170 0 170 C -35 170 -35 -170 0 -170 Z']),
      st('Two big wings on top.', 'Two big wings', ['M 20 -60 C 120 -280 330 -220 260 -40 C 230 30 100 20 20 0', 'M -20 -60 C -120 -280 -330 -220 -260 -40 C -230 30 -100 20 -20 0']),
      st('Two small wings below.', 'Two small wings', ['M 20 30 C 120 30 260 80 200 200 C 140 270 40 180 20 80', 'M -20 30 C -120 30 -260 80 -200 200 C -140 270 -40 180 -20 80']),
      st('Add two antennae.', 'Antennae', ['M -12 -165 Q -40 -250 -90 -280', 'M 12 -165 Q 40 -250 90 -280', dot(-92, -282), dot(92, -282)]),
      st('And pretty spots!', 'Pretty spots', [circ(170, -110, 32), circ(-170, -110, 32), circ(140, 140, 22), circ(-140, 140, 22)]),
    ], fills: [['M 20 -60 C 120 -280 330 -220 260 -40 C 230 30 100 20 20 0 Z', '#F15BB5'], ['M -20 -60 C -120 -280 -330 -220 -260 -40 C -230 30 -100 20 -20 0 Z', '#F15BB5'],
      ['M 20 30 C 120 30 260 80 200 200 C 140 270 40 180 20 80 Z', '#9B5DE5'], ['M -20 30 C -120 30 -260 80 -200 200 C -140 270 -40 180 -20 80 Z', '#9B5DE5'],
      ['M 0 -170 C 35 -170 35 170 0 170 C -35 170 -35 -170 0 -170 Z', '#FFC93C'], [circ(170, -110, 32), '#FFE66D'], [circ(-170, -110, 32), '#FFE66D'], [circ(140, 140, 22), '#FFE66D'], [circ(-140, 140, 22), '#FFE66D']] },
    { word: 'APPLE', article: 'an', emoji: '🍎', steps: [
      st('Draw a big round apple.', 'A round apple', ['M 0 -120 C 80 -200 260 -160 250 20 C 240 200 110 280 0 230 C -110 280 -240 200 -250 20 C -260 -160 -80 -200 0 -120 Z']),
      st('Add a little stem.', 'A stem', ['M 0 -120 Q 10 -190 40 -235']),
      st('And a leaf!', 'A leaf', ['M 25 -185 C 80 -255 160 -240 175 -210 C 125 -165 60 -165 25 -185 Z']),
      st('A shiny spot. So shiny!', 'A shiny spot', ['M -175 -30 Q -165 -95 -115 -115']),
    ], fills: [['M 0 -120 C 80 -200 260 -160 250 20 C 240 200 110 280 0 230 C -110 280 -240 200 -250 20 C -260 -160 -80 -200 0 -120 Z', '#F2545B'], ['M 25 -185 C 80 -255 160 -240 175 -210 C 125 -165 60 -165 25 -185 Z', '#6BCB77']] },
    { word: 'TURTLE', article: 'a', emoji: '🐢', steps: [
      st('Draw a big half circle for the shell.', 'A half circle', ['M -230 80 C -230 -180 230 -180 230 80 Z']),
      st('Add a round head.', 'A round head', [circ(290, 10, 62)]),
      st('Draw four little legs.', 'Four legs', ['M -175 80 L -175 150 L -115 150 L -115 80', 'M 115 80 L 115 150 L 175 150 L 175 80']),
      st('Draw a pattern on the shell.', 'A pattern', ['M -60 -20 L 0 -75 L 60 -20 L 40 50 L -40 50 Z']),
      st('An eye, and a smile!', 'Eye and smile', [dot(305, -5), 'M 270 35 Q 295 55 320 35']),
    ], fills: [['M -175 80 L -175 150 L -115 150 L -115 80 Z', '#B8E986'], ['M 115 80 L 115 150 L 175 150 L 175 80 Z', '#B8E986'], [circ(290, 10, 62), '#B8E986'],
      ['M -230 80 C -230 -180 230 -180 230 80 Z', '#6BCB77'], ['M -60 -20 L 0 -75 L 60 -20 L 40 50 L -40 50 Z', '#3FA34D']] },
  ];
  for (const d of DRAW_TOPICS) TOPICS.push({ id: `drawalong-${d.word.toLowerCase()}`, template: 'drawalong', ...d });


  // ---- Who is hiding? A shadow, a 3-2-1 countdown, then the colourful reveal (art borrowed from other topics) ----
  {
    const animals = TOPICS.filter(t => t.template === 'animal');
    const objects = [
      ['abc-a', 'APPLE'], ['circle-sun', 'SUN'], ['abc-u', 'UMBRELLA'], ['triangle-pizza', 'PIZZA'], ['abc-m', 'MOON'], ['square-robot', 'ROBOT'],
      ['abc-w', 'WATERMELON'], ['oval-balloon', 'BALLOON'], ['abc-i', 'ICE CREAM'], ['triangle-tree', 'TREE'], ['abc-v', 'VAN'], ['heart-strawberry', 'STRAWBERRY'],
      ['abc-g', 'GRAPES'], ['star-starfish', 'STARFISH'], ['abc-e', 'EGG'], ['circle-cookie', 'COOKIE'], ['abc-x', 'XYLOPHONE'], ['square-present', 'PRESENT'],
      ['abc-l', 'LEMON'], ['diamond-kite', 'KITE'], ['abc-y', 'YO-YO'], ['circle-orange', 'ORANGE'], ['abc-n', 'NEST'], ['oval-avocado', 'AVOCADO'],
      ['abc-f', 'FISH'], ['rectangle-door', 'DOOR'], ['abc-h', 'HEART'], ['abc-z', 'ZEBRA'], ['abc-j', 'JUICE BOX'], ['abc-q', 'CROWN'],
    ];
    const an = w => /^[AEIOU]/.test(w) ? 'an' : 'a';
    const SHADOW = [];
    for (let i = 0; i < Math.max(animals.length, objects.length); i++) {
      const a = animals[i];
      if (a) SHADOW.push({ id: `shadow-${a.id.slice(7)}`, art: a.id, word: a.word, article: a.article, emoji: a.emoji,
        extra: `The ${a.word.toLowerCase()} says ${a.sound.split(' ')[0].replace(/[!,]/g, '').toLowerCase()}!` });
      const o = objects[i];
      if (o) {
        const src = TOPICS.find(t => t.id === o[0]);
        const plural = o[1] === 'GRAPES';
        SHADOW.push({ id: `shadow-${o[1].toLowerCase().replace(/[^a-z]/g, '')}`, art: o[0], word: o[1], article: plural ? '' : an(o[1]), emoji: src.emoji || '❓', plural });
      }
    }
    for (const t of SHADOW) TOPICS.push({ template: 'shadow', ...t });
  }

  if (typeof module !== 'undefined') module.exports = TOPICS; else window.TOPICS = TOPICS;
})();

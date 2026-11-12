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
  const NUM_WORDS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN'];
  const COUNT_OBJECTS = [
    ['oval-balloon', 'BALLOON', 'BALLOONS', '🎈'], ['circle-cookie', 'COOKIE', 'COOKIES', '🍪'], ['heart-strawberry', 'STRAWBERRY', 'STRAWBERRIES', '🍓'],
    ['star-starfish', 'STARFISH', 'STARFISH', '⭐'], ['circle-orange', 'ORANGE', 'ORANGES', '🍊'], ['square-present', 'PRESENT', 'PRESENTS', '🎁'],
    ['circle-sun', 'SUN', 'SUNS', '☀️'], ['diamond-kite', 'KITE', 'KITES', '🪁'], ['triangle-tree', 'TREE', 'TREES', '🎄'], ['oval-avocado', 'AVOCADO', 'AVOCADOS', '🥑'],
  ];
  for (let n = 1; n <= 10; n++) {
    const [object, one, many, emoji] = COUNT_OBJECTS[(n * 3) % COUNT_OBJECTS.length];
    TOPICS.push({
      id: `count-${n}`, template: 'count', n, word: NUM_WORDS[n], object, objectName: n === 1 ? one : many, emoji,
      strokes: n === 10 ? [...shift(DIGITS[1], -120), ...shift(DIGITS[0], 110)] : DIGITS[n],
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
  };
  const ANIMALS = [
    ['cow', 'COW', 'a', 'Moo!', 'MOO', '🐮'], ['dog', 'DOG', 'a', 'Woof woof!', 'WOOF', '🐶'], ['cat', 'CAT', 'a', 'Meow!', 'MEOW', '🐱'],
    ['duck', 'DUCK', 'a', 'Quack quack!', 'QUACK', '🦆'], ['pig', 'PIG', 'a', 'Oink oink!', 'OINK', '🐷'], ['sheep', 'SHEEP', 'a', 'Baa!', 'BAA', '🐑'],
    ['lion', 'LION', 'a', 'Roar!', 'ROAR', '🦁'], ['frog', 'FROG', 'a', 'Ribbit!', 'RIBBIT', '🐸'], ['horse', 'HORSE', 'a', 'Neigh!', 'NEIGH', '🐴'],
    ['chicken', 'CHICKEN', 'a', 'Cluck cluck!', 'CLUCK', '🐔'], ['owl', 'OWL', 'an', 'Hoo hoo!', 'HOO HOO', '🦉'], ['mouse', 'MOUSE', 'a', 'Squeak squeak!', 'SQUEAK', '🐭'],
  ];
  for (const [key, word, article, sound, soundText, emoji] of ANIMALS) {
    TOPICS.push({ id: `animal-${key}`, template: 'animal', word, article, sound, soundText, emoji, artData: ANIMAL_ART[key] });
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

  if (typeof module !== 'undefined') module.exports = TOPICS; else window.TOPICS = TOPICS;
})();

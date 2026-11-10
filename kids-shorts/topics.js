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

  if (typeof module !== 'undefined') module.exports = TOPICS; else window.TOPICS = TOPICS;
})();

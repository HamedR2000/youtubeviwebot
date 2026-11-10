// Doodle Pals character art (SVG strings). Each character stands with its base at (0,0), about 450px tall.
// Used by the channel branding and by scenes. Faces: blink by passing { blink: 0..1 }.
(function () {
  const face = (y, s = 1, blink = 1) => `
    <g transform="translate(0 ${y}) scale(${s})">
      <ellipse cx="-16" cy="0" rx="8" ry="${11 * blink}" fill="#3B2B4F"/><ellipse cx="16" cy="0" rx="8" ry="${11 * blink}" fill="#3B2B4F"/>
      <circle cx="-13" cy="-4" r="2.6" fill="#fff"/><circle cx="19" cy="-4" r="2.6" fill="#fff"/>
      <path d="M -14 22 Q 0 36 14 22" fill="none" stroke="#3B2B4F" stroke-width="6" stroke-linecap="round"/>
      <ellipse cx="-30" cy="20" rx="9" ry="6" fill="#FF8FA3" opacity="0.85"/><ellipse cx="30" cy="20" rx="9" ry="6" fill="#FF8FA3" opacity="0.85"/>
    </g>`;

  // Penny the Pencil — the host (tip at the bottom)
  const penny = (o = {}) => `
    <g>
      <path d="M 0 0 L -38 -100 L 38 -100 Z" fill="#F7D2A6"/><path d="M 0 0 L -13 -34 L 13 -34 Z" fill="#3B2B4F"/>
      <rect x="-40" y="-380" width="80" height="284" rx="9" fill="#FFC93C"/><rect x="-40" y="-380" width="24" height="284" fill="#FFB020" opacity="0.65"/>
      <rect x="-42" y="-412" width="84" height="36" rx="7" fill="#C9CED6"/><rect x="-42" y="-466" width="84" height="60" rx="24" fill="#FF8FA3"/>
      ${face(-270, 1, o.blink ?? 1)}
    </g>`;

  // Ellie the Eraser — playful helper (pink with a blue sleeve)
  const ellie = (o = {}) => `
    <g>
      <rect x="-95" y="-230" width="190" height="230" rx="46" fill="#FF8FB1"/>
      <rect x="-95" y="-230" width="190" height="70" rx="40" fill="#FFB3C8"/>
      <rect x="-99" y="-120" width="198" height="78" rx="12" fill="#4D96FF"/>
      <rect x="-99" y="-120" width="198" height="18" fill="#7AB2FF"/>
      <text x="0" y="-66" text-anchor="middle" font-size="34" font-weight="700" fill="#fff" font-family="Fredoka, sans-serif">ELLIE</text>
      ${face(-180, 1.1, o.blink ?? 1)}
      <path d="M -60 -232 Q -40 -270 -20 -232" fill="#FF8FB1"/>
    </g>`;

  // Coco the Crayon — colour teacher (purple wrapper, pointy tip at the top)
  const coco = (o = {}) => {
    const c = o.color || '#9B5DE5';
    return `
    <g>
      <path d="M -45 -360 L 0 -450 L 45 -360 Z" fill="${c}"/>
      <rect x="-45" y="-362" width="90" height="362" rx="16" fill="${c}"/>
      <rect x="-45" y="-300" width="90" height="230" fill="#FFF3D6"/>
      <rect x="-45" y="-300" width="90" height="14" fill="${c}" opacity="0.6"/><rect x="-45" y="-84" width="90" height="14" fill="${c}" opacity="0.6"/>
      <path d="M -45 -250 Q 0 -230 45 -250" fill="none" stroke="${c}" stroke-width="6" opacity="0.5"/>
      ${face(-200, 1, o.blink ?? 1)}
      <text x="0" y="-110" text-anchor="middle" font-size="26" font-weight="700" fill="${c}" font-family="Fredoka, sans-serif">COCO</text>
    </g>`;
  };

  const C = { penny, ellie, coco };
  if (typeof module !== 'undefined') module.exports = C; else window.CHARACTERS = C;
})();

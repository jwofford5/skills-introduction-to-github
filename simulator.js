'use strict';

const NS  = 'http://www.w3.org/2000/svg';
const SVG = document.getElementById('map');

// ── Floor plan geometry (SVG 400×580, walls = gaps between rooms) ──────────
const FLOOR = [
  { x: 12, y:  12, w:128, h:190, label:'Living Room' },
  { x:152, y:  12, w:236, h:190, label:'Family Room'  },
  { x: 12, y:214, w:364, h: 54, label:'Hallway'       },
  { x: 12, y:280, w:128, h: 90, label:'Room 1'        },
  { x: 12, y:382, w:128, h: 90, label:'Room 2'        },
  { x: 12, y:484, w:128, h: 82, label:'Last Room'     },
  { x:152, y:280, w:236, h:168, label:'Kitchen'       },
  { x:152, y:462, w:236, h:104, label:'Bathroom'      },
];

const DOOR_MARKS = [
  { x1:  6, y1: 82, x2:  6, y2:132, color:'#ef4444', label:'FRONT' },
  { x1: 20, y1:272, x2:120, y2:272, color:'#f59e0b', label:'Closed R' },
  { x1: 20, y1:374, x2:120, y2:374, color:'#f59e0b', label:'Closed L' },
  { x1: 20, y1:476, x2:120, y2:476, color:'#22c55e', label:'Open L'   },
  { x1:270, y1:268, x2:270, y2:280, color:'#3b82f6', label:'Kitchen'  },
  { x1:270, y1:450, x2:270, y2:462, color:'#3b82f6', label:'Bath'     },
];

// Camera: cx/cy = focal point in SVG units, zoom = SVG units visible (width)
const CAMERAS = {
  STAGING:     { cx:  20, cy:150, zoom:280 },
  ENTRY:       { cx:  76, cy:112, zoom:200 },
  FAMILY_ROOM: { cx: 200, cy:122, zoom:340 },
  KITCHEN:     { cx: 270, cy:348, zoom:215 },
  BATHROOM:    { cx: 270, cy:492, zoom:195 },
  ROOM1:       { cx:  76, cy:322, zoom:195 },
  ROOM2:       { cx:  76, cy:424, zoom:195 },
  LAST_ROOM:   { cx:  76, cy:522, zoom:178 },
  ALL_CLEAR:   { cx: 200, cy:296, zoom:450 },
};

// ── State ───────────────────────────────────────────────────────────────────
let step = 0, playing = false, playTimer = null;
let focusedOp = null, showAngles = false;

// Animation
const opPos = {}, opTgt = {};
let camCur = null, camTgt = null, animating = false;

// ── SVG helper ──────────────────────────────────────────────────────────────
function el(tag, attrs) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
}
const layer = id => document.getElementById(id);

// ── Build floor plan ────────────────────────────────────────────────────────
function buildFloor() {
  const fl = layer('floor-layer'), dl = layer('door-layer'), ll = layer('label-layer');

  fl.appendChild(el('rect', { x:0, y:0, width:400, height:580, fill:'#080d14' }));

  for (const r of FLOOR) {
    fl.appendChild(el('rect', {
      x:r.x, y:r.y, width:r.w, height:r.h,
      fill: r.label === 'Hallway' ? '#0c1620' : '#0f1c2e',
    }));
    const t = el('text', {
      x: r.x + r.w/2, y: r.y + r.h/2,
      'font-size': r.w < 140 ? 9 : 11,
      'font-family': 'system-ui,-apple-system,sans-serif',
      'font-weight': 500, fill:'#1e3a5f',
      'text-anchor':'middle', 'dominant-baseline':'middle',
    });
    t.textContent = r.label;
    ll.appendChild(t);
  }

  for (const d of DOOR_MARKS) {
    dl.appendChild(el('line', {
      x1:d.x1, y1:d.y1, x2:d.x2, y2:d.y2,
      stroke:d.color, 'stroke-width':2.5, 'stroke-linecap':'round',
    }));
    if (d.label) {
      const mx = d.x1 === d.x2 ? d.x1 - 9 : (d.x1+d.x2)/2;
      const my = d.y1 === d.y2 ? d.y1 - 5 : (d.y1+d.y2)/2;
      const t = el('text', {
        x:mx, y:my, 'font-size':7,
        'font-family':'system-ui,-apple-system,sans-serif',
        'font-weight':600, fill:d.color,
        'text-anchor':'middle', 'dominant-baseline':'middle',
      });
      t.textContent = d.label;
      dl.appendChild(t);
    }
  }
}

// ── Build operator tokens ───────────────────────────────────────────────────
const opEls = {};

function buildOperators() {
  const ol = layer('operator-layer');
  for (const [name, op] of Object.entries(OPERATORS)) {
    const g = document.createElementNS(NS, 'g');
    g.id = 'op-' + name;
    g.setAttribute('transform', 'translate(-60,107)');
    g.style.cursor = 'pointer';

    const ini = name.length <= 3 ? name : name.slice(0,2);
    g.appendChild(el('circle', { cx:0, cy:0, r:14, fill:'#0a1525', stroke:op.color, 'stroke-width':2.5 }));

    const ti = el('text', {
      x:0, y:1, 'font-size': ini.length > 2 ? 8 : 9.5,
      'font-family':'system-ui,-apple-system,sans-serif',
      'font-weight':700, fill:op.color,
      'text-anchor':'middle', 'dominant-baseline':'middle',
    });
    ti.textContent = ini;
    g.appendChild(ti);

    const tn = el('text', {
      x:0, y:23, 'font-size':7,
      'font-family':'system-ui,-apple-system,sans-serif',
      'font-weight':600, fill:op.color, opacity:0.85,
      'text-anchor':'middle', 'dominant-baseline':'auto',
    });
    tn.textContent = name;
    g.appendChild(tn);

    g.addEventListener('click', () => toggleFocus(name));
    ol.appendChild(g);
    opEls[name] = g;
    opPos[name] = { x:-60, y:107 };
    opTgt[name] = { x:-60, y:107 };
  }
}

// ── Animation loop ──────────────────────────────────────────────────────────
function lerp(a, b, t) { return a + (b - a) * t; }

function runAnim() {
  let busy = false;

  if (camCur && camTgt) {
    const T = 0.13;
    ['x','y','w','h'].forEach(k => { camCur[k] = lerp(camCur[k], camTgt[k], T); });
    SVG.setAttribute('viewBox', `${camCur.x.toFixed(1)} ${camCur.y.toFixed(1)} ${camCur.w.toFixed(1)} ${camCur.h.toFixed(1)}`);
    if (['x','y','w','h'].some(k => Math.abs(camCur[k]-camTgt[k]) > 0.5)) busy = true;
    else Object.assign(camCur, camTgt);
  }

  for (const name of Object.keys(OPERATORS)) {
    const cur = opPos[name], tgt = opTgt[name];
    if (!cur || !tgt) continue;
    const dx = tgt.x - cur.x, dy = tgt.y - cur.y;
    if (Math.abs(dx) > 0.3 || Math.abs(dy) > 0.3) {
      cur.x += dx * 0.15; cur.y += dy * 0.15;
      opEls[name].setAttribute('transform', `translate(${cur.x.toFixed(1)},${cur.y.toFixed(1)})`);
      busy = true;
    } else {
      cur.x = tgt.x; cur.y = tgt.y;
      opEls[name].setAttribute('transform', `translate(${cur.x},${cur.y})`);
    }
  }

  if (busy) requestAnimationFrame(runAnim);
  else animating = false;
}

function startAnim() {
  if (!animating) { animating = true; requestAnimationFrame(runAnim); }
}

// ── Camera ──────────────────────────────────────────────────────────────────
function camVB(phase) {
  const cam = CAMERAS[phase] || CAMERAS.ALL_CLEAR;
  const sw = SVG.clientWidth || 380, sh = SVG.clientHeight || 480;
  const w = cam.zoom, h = cam.zoom * (sh / sw);
  return { x: cam.cx - w/2, y: cam.cy - h/2, w, h };
}

function applyCamera(phase, instant) {
  const vb = camVB(phase);
  if (instant || !camCur) {
    camCur = { ...vb }; camTgt = { ...vb };
    SVG.setAttribute('viewBox', `${vb.x} ${vb.y} ${vb.w} ${vb.h}`);
  } else {
    camTgt = vb;
    startAnim();
  }
}

// ── Go to step ──────────────────────────────────────────────────────────────
function goToStep(n, instant) {
  step = Math.max(0, Math.min(STEPS.length - 1, n));
  const s = STEPS[step];

  applyCamera(s.phase, instant);

  const pos = s.pos || {};
  for (const [name, p] of Object.entries(pos)) {
    const px = Array.isArray(p) ? p[0] : p.x;
    const py = Array.isArray(p) ? p[1] : p.y;
    opTgt[name] = { x: px, y: py };
    if (instant) {
      opPos[name] = { x: px, y: py };
      opEls[name]?.setAttribute('transform', `translate(${px},${py})`);
    }
  }

  if (!instant) startAnim();
  updateFocusDim();
  drawAngles(s);
  updateUI(s);
}

// ── Angles ──────────────────────────────────────────────────────────────────
function drawAngles(s) {
  const al = layer('angle-layer');
  al.innerHTML = '';
  if (!showAngles) return;
  for (const a of (s.angles || [])) {
    const op = OPERATORS[a.op]; if (!op) continue;
    const r  = (a.deg - 90) * Math.PI / 180;
    const sp = ((a.spread || 28) / 2) * Math.PI / 180;
    const L  = 55;
    const x1 = a.x + L * Math.cos(r - sp), y1 = a.y + L * Math.sin(r - sp);
    const x2 = a.x + L * Math.cos(r + sp), y2 = a.y + L * Math.sin(r + sp);
    al.appendChild(el('path', {
      d: `M${a.x},${a.y} L${x1},${y1} A${L},${L} 0 0 1 ${x2},${y2} Z`,
      fill: op.color + '28', stroke: op.color + '70', 'stroke-width': 0.8,
    }));
  }
}

// ── UI ──────────────────────────────────────────────────────────────────────
function updateUI(s) {
  document.getElementById('step-num').textContent   = step + 1;
  document.getElementById('step-total').textContent = STEPS.length;
  document.getElementById('progress-bar').style.width = ((step / (STEPS.length - 1)) * 100) + '%';
  document.getElementById('info-title').textContent = s.title;

  const crow = document.getElementById('info-callout');
  if (s.callout) {
    crow.classList.remove('hidden');
    document.getElementById('callout-text').textContent = s.callout;
  } else {
    crow.classList.add('hidden');
  }
  document.getElementById('info-teaching').textContent = s.teaching || '';
  document.getElementById('btn-prev').disabled = step === 0;
  document.getElementById('btn-next').disabled = step === STEPS.length - 1;
}

// ── Focus / dim ─────────────────────────────────────────────────────────────
function toggleFocus(name) {
  focusedOp = focusedOp === name ? null : name;
  updateFocusDim(); updateLegend();
}

function updateFocusDim() {
  for (const [name, g] of Object.entries(opEls)) {
    const staged = opPos[name]?.x < 0;
    if (focusedOp === null)      g.style.opacity = staged ? '0.38' : '1';
    else if (focusedOp === name) g.style.opacity = '1';
    else                         g.style.opacity = staged ? '0.08' : '0.12';
  }
}

// ── Legend ──────────────────────────────────────────────────────────────────
function buildLegend() {
  const c = document.getElementById('op-legend');
  for (const [name, op] of Object.entries(OPERATORS)) {
    const d = document.createElement('div');
    d.className = 'legend-op'; d.id = 'leg-' + name; d.style.color = op.color;
    d.innerHTML = `<span class="legend-dot" style="background:${op.color}"></span><span class="legend-name">${name}</span>`;
    d.addEventListener('click', () => toggleFocus(name));
    c.appendChild(d);
  }
}

function updateLegend() {
  for (const name of Object.keys(OPERATORS))
    document.getElementById('leg-' + name)?.classList.toggle('active', focusedOp === name);
}

// ── Playback ────────────────────────────────────────────────────────────────
function startPlay() {
  playing = true;
  document.getElementById('icon-play').classList.add('hidden');
  document.getElementById('icon-pause').classList.remove('hidden');
  document.getElementById('btn-play').classList.add('paused');
  playTimer = setInterval(() => {
    if (step >= STEPS.length - 1) { stopPlay(); return; }
    goToStep(step + 1);
  }, 2200);
}

function stopPlay() {
  playing = false; clearInterval(playTimer);
  document.getElementById('icon-play').classList.remove('hidden');
  document.getElementById('icon-pause').classList.add('hidden');
  document.getElementById('btn-play').classList.remove('paused');
}

// ── Controls ────────────────────────────────────────────────────────────────
document.getElementById('btn-prev').addEventListener('click', () => { stopPlay(); goToStep(step - 1); });
document.getElementById('btn-next').addEventListener('click', () => { stopPlay(); goToStep(step + 1); });
document.getElementById('btn-play').addEventListener('click', () => {
  if (playing) stopPlay();
  else { if (step >= STEPS.length - 1) goToStep(0, true); startPlay(); }
});
document.getElementById('btn-angles').addEventListener('click', function () {
  showAngles = !showAngles;
  this.classList.toggle('active', showAngles);
  drawAngles(STEPS[step]);
});

// ── Touch swipe ─────────────────────────────────────────────────────────────
let tx0 = 0;
SVG.addEventListener('touchstart', e => { tx0 = e.touches[0].clientX; }, { passive: true });
SVG.addEventListener('touchend',   e => {
  const dx = e.changedTouches[0].clientX - tx0;
  if (Math.abs(dx) > 44) { stopPlay(); goToStep(step + (dx < 0 ? 1 : -1)); }
}, { passive: true });

window.addEventListener('resize', () => { if (step >= 0) applyCamera(STEPS[step].phase, true); });

// ── Init ─────────────────────────────────────────────────────────────────────
buildFloor();
buildOperators();
buildLegend();
requestAnimationFrame(() => goToStep(0, true));

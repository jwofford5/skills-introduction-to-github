'use strict';
const SCALE = 30; // px per meter
const OFFSET = { x: 210, y: 20 }; // exterior stack visible left of x=0

function px(m) { return m * SCALE; }
function cx(xm) { return OFFSET.x + xm * SCALE; }
function cy(ym) { return OFFSET.y + ym * SCALE; }

// ── Canvas setup ──────────────────────────────────────────────────────────────
const canvas = document.getElementById('sim');
const ctx = canvas.getContext('2d');

// Fit canvas to window
function resize() {
  const wrap = document.getElementById('canvas-wrap');
  const maxW = wrap.clientWidth, maxH = wrap.clientHeight;
  const nativeW = 700, nativeH = 520;
  const ratio = Math.min(maxW / nativeW, maxH / nativeH, 1);
  canvas.style.width  = Math.floor(nativeW * ratio) + 'px';
  canvas.style.height = Math.floor(nativeH * ratio) + 'px';
}
window.addEventListener('resize', resize);
resize();

// ── Math helpers ──────────────────────────────────────────────────────────────
function deg2rad(d) { return d * Math.PI / 180; }
// 0=north,90=east,180=south,270=west → SVG angle (0=east)
function facingToAngle(f) { return (f - 90) * Math.PI / 180; }

function lerpAngle(a, b, t) {
  let d = ((b - a + 540) % 360) - 180;
  return ((a + d * t) + 360) % 360;
}
function lerp(a, b, t) { return a + (b - a) * t; }

function interpOp(a, b, t) {
  // Body rotation precedes translation: first 30% of interval rotates, then both
  const rotT = Math.min(t / 0.3, 1);
  const moveT = t < 0.3 ? 0 : (t - 0.3) / 0.7;
  return {
    pos: { x: lerp(a.pos.x, b.pos.x, moveT), y: lerp(a.pos.y, b.pos.y, moveT) },
    facing: lerpAngle(a.facing, b.facing, rotT),
    posture: t < 0.5 ? a.posture : b.posture,
    sectorPrimary: {
      centerDeg: lerpAngle(a.sectorPrimary.centerDeg, b.sectorPrimary.centerDeg, rotT),
      widthDeg: lerp(a.sectorPrimary.widthDeg, b.sectorPrimary.widthDeg, t)
    },
    wallContact: t < 0.5 ? a.wallContact : b.wallContact,
    weaponReady: t < 0.5 ? a.weaponReady : b.weaponReady
  };
}

function getState(time) {
  const kfs = KEYFRAMES;
  if (time <= kfs[0].time) return { kf: kfs[0], t: 0, idx: 0 };
  if (time >= kfs[kfs.length-1].time) return { kf: kfs[kfs.length-1], t: 1, idx: kfs.length-1 };
  for (let i = 0; i < kfs.length - 1; i++) {
    if (time >= kfs[i].time && time <= kfs[i+1].time) {
      const t = (time - kfs[i].time) / (kfs[i+1].time - kfs[i].time);
      const merged = {};
      const allNames = new Set([...Object.keys(kfs[i].ops), ...Object.keys(kfs[i+1].ops)]);
      for (const name of allNames) {
        const a = kfs[i].ops[name] || kfs[i+1].ops[name];
        const b = kfs[i+1].ops[name] || kfs[i].ops[name];
        merged[name] = interpOp(a, b, t);
      }
      return { kf: { ...kfs[i], ops: merged }, t, idx: i };
    }
  }
}

// ── Drawing functions ─────────────────────────────────────────────────────────

function drawFloorPlan() {
  // Dark background = wall mass / exterior
  ctx.fillStyle = '#050a10';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Exterior label
  ctx.fillStyle = '#0d1520';
  ctx.font = '500 10px system-ui,sans-serif';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'top';
  ctx.fillText('EXTERIOR', 18, 8);

  // Room interiors (slightly inset to show wall thickness via dark gaps)
  const W = 3; // wall half-thickness in px
  for (const r of ROOMS) {
    const rx = cx(r.x) + W, ry = cy(r.y) + W;
    const rw = px(r.w) - W*2,  rh = px(r.h) - W*2;
    ctx.fillStyle = '#0f1c2e';
    ctx.fillRect(rx, ry, rw, rh);
    // Room label
    ctx.fillStyle = '#1e3a58';
    ctx.font = '600 10px system-ui,sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(r.label, cx(r.x + r.w/2), cy(r.y + r.h/2));
  }
}

function drawFatalFunnels(simTime) {
  for (const d of DOORS) {
    if (d.state === 'open') continue;
    if (simTime >= d.clearAt) continue;
    // Direction the muzzle faces to enter room
    const a = facingToAngle(d.normal);
    const depth = px(2.2);
    const spread = Math.PI / 4; // 45° each side
    const tx = cx(d.hx), ty = cy(d.hy);
    ctx.beginPath();
    ctx.moveTo(tx, ty);
    ctx.lineTo(tx + depth * Math.cos(a - spread), ty + depth * Math.sin(a - spread));
    ctx.lineTo(tx + depth * Math.cos(a + spread), ty + depth * Math.sin(a + spread));
    ctx.closePath();
    ctx.fillStyle = 'rgba(239,68,68,0.10)';
    ctx.fill();
    ctx.setLineDash([4, 3]);
    ctx.strokeStyle = 'rgba(239,68,68,0.28)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.setLineDash([]);
    // Label
    ctx.fillStyle = 'rgba(239,68,68,0.5)';
    ctx.font = '500 8px system-ui,sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('FATAL FUNNEL', tx + depth * 0.6 * Math.cos(a), ty + depth * 0.6 * Math.sin(a));
  }
}

function drawDoors(simTime) {
  for (const d of DOORS) {
    const isOpen = d.state === 'open' || simTime >= d.clearAt;
    const color = isOpen ? '#22c55e' : d.id === 'front' ? '#ef4444' : '#f59e0b';
    const hx = cx(d.hx), hy = cy(d.hy), len = px(d.len);
    const c = (d.closedDeg - 90) * Math.PI / 180; // closed panel angle
    const closedX = hx + len * Math.cos(c), closedY = hy + len * Math.sin(c);
    const o = d.cw ? c + Math.PI/2 : c - Math.PI/2;
    const openX = hx + len * Math.cos(o), openY = hy + len * Math.sin(o);
    const endX = isOpen ? openX : closedX, endY = isOpen ? openY : closedY;

    // Door panel
    ctx.beginPath();
    ctx.moveTo(hx, hy);
    ctx.lineTo(endX, endY);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Swing arc (always shown) — canvas arc: anticlockwise=true means CCW on screen
    const startAngle = Math.atan2(closedY - hy, closedX - hx);
    const endAngle   = Math.atan2(openY   - hy, openX   - hx);
    ctx.beginPath();
    ctx.arc(hx, hy, len, startAngle, endAngle, !d.cw); // cw=true → anticlockwise=false
    ctx.strokeStyle = color + '60';
    ctx.lineWidth = 1.2;
    ctx.setLineDash([3, 2]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Hinge dot
    ctx.beginPath();
    ctx.arc(hx, hy, 3, 0, Math.PI*2);
    ctx.fillStyle = '#5a7a9a';
    ctx.fill();

    // Knob dot (at closed end)
    ctx.beginPath();
    ctx.arc(closedX, closedY, 3, 0, Math.PI*2);
    ctx.fillStyle = color;
    ctx.fill();
  }
}

function drawSectorWedge(state, color) {
  const x = cx(state.pos.x), y = cy(state.pos.y);
  const sd = state.sectorPrimary;
  const len = px(3.5);
  const a = facingToAngle(sd.centerDeg);
  const spread = deg2rad(sd.widthDeg / 2);
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.arc(x, y, len, a - spread, a + spread, false);
  ctx.closePath();
  ctx.fillStyle = color + '22';
  ctx.fill();
  ctx.strokeStyle = color + '55';
  ctx.lineWidth = 0.8;
  ctx.stroke();
}

function drawOperator(name, state, color) {
  const x = cx(state.pos.x), y = cy(state.pos.y);
  const r = 9;
  const a = facingToAngle(state.facing);

  // Body circle
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fillStyle = '#0a1525';
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();

  // Initials
  ctx.fillStyle = color;
  ctx.font = '700 7px system-ui,sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(name.slice(0, 2), x, y);

  // Facing triangle (muzzle direction)
  const d = r + 5, tipLen = 5, w = 0.55;
  const tx = x + d * Math.cos(a), ty = y + d * Math.sin(a);
  const tip = { x: tx + tipLen * Math.cos(a), y: ty + tipLen * Math.sin(a) };
  const b1  = { x: x + (r+1) * Math.cos(a - w), y: y + (r+1) * Math.sin(a - w) };
  const b2  = { x: x + (r+1) * Math.cos(a + w), y: y + (r+1) * Math.sin(a + w) };
  ctx.beginPath();
  ctx.moveTo(tip.x, tip.y);
  ctx.lineTo(b1.x, b1.y);
  ctx.lineTo(b2.x, b2.y);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();

  // Name below
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.75;
  ctx.font = '500 6px system-ui,sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  ctx.fillText(name, x, y + r + 3);
  ctx.globalAlpha = 1;
}

function drawAnnotation(ann) {
  const el = document.getElementById('annotation-overlay');
  if (!ann) { el.innerHTML = ''; return; }
  el.innerHTML = `<div class="annotation-box"><span style="color:${ann.color}">${ann.who}</span>  ${ann.text}</div>`;
}

// ── Bang flash ────────────────────────────────────────────────────────────────
let bangActive = false, bangT = 0;
function triggerBang() {
  bangActive = true; bangT = 0;
  const el = document.getElementById('bang-flash');
  el.classList.add('flash');
  setTimeout(() => {
    el.classList.remove('flash');
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => { el.style.transition = ''; bangActive = false; }, 500);
  }, 80);
}

// ── Muzzle discipline check ───────────────────────────────────────────────────
function checkMuzzleDiscipline(ops) {
  for (const [nameA, stA] of Object.entries(ops)) {
    const a = facingToAngle(stA.sectorPrimary.centerDeg);
    const spread = deg2rad(stA.sectorPrimary.widthDeg / 2);
    const len = 3.5;
    for (const [nameB, stB] of Object.entries(ops)) {
      if (nameA === nameB) continue;
      const dx = stB.pos.x - stA.pos.x, dy = stB.pos.y - stA.pos.y;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist > len) continue;
      const angle = Math.atan2(dy, dx);
      let diff = Math.abs(((angle - a) * 180 / Math.PI + 360) % 360);
      if (diff > 180) diff = 360 - diff;
      if (diff < stA.sectorPrimary.widthDeg / 2) {
        console.warn(`[MUZZLE] ${nameA} sector covers ${nameB}`);
      }
    }
  }
}

// ── Main render ───────────────────────────────────────────────────────────────
function render(simTime) {
  const { kf, idx } = getState(simTime);
  const ops = kf.ops;

  // Draw layers
  drawFloorPlan();
  drawFatalFunnels(simTime);
  drawDoors(simTime);

  // Sector wedges (behind operators)
  for (const [name, state] of Object.entries(ops)) {
    drawSectorWedge(state, OP_COLOR[name] || '#5a7a9a');
  }

  // Operators
  for (const [name, state] of Object.entries(ops)) {
    drawOperator(name, state, OP_COLOR[name] || '#5a7a9a');
  }

  // Update UI
  document.getElementById('step-label').textContent = kf.label || '';
  drawAnnotation(kf.annotation);

  // Bang
  if (kf.bang && !bangActive) triggerBang();

  // Muzzle discipline (dev mode)
  checkMuzzleDiscipline(ops);

  // Scrubber sync
  const dur = KEYFRAMES[KEYFRAMES.length-1].time;
  const scrubber = document.getElementById('scrubber');
  if (!scrubberDragging) scrubber.value = (simTime / dur * 1000).toFixed(0);
  const m = Math.floor(simTime/60), s = Math.floor(simTime%60);
  const dm = Math.floor(dur/60), ds = Math.floor(dur%60);
  document.getElementById('time-display').textContent =
    `${m}:${String(s).padStart(2,'0')} / ${dm}:${String(ds).padStart(2,'0')}`;
}

// ── Playback engine ───────────────────────────────────────────────────────────
let playing = false, speed = 1, simTime = 0, lastRaf = null;
const DURATION = KEYFRAMES[KEYFRAMES.length-1].time;
let scrubberDragging = false;

function tick(ts) {
  if (lastRaf !== null && playing) {
    simTime = Math.min(simTime + (ts - lastRaf) / 1000 * speed, DURATION);
    if (simTime >= DURATION) { playing = false; setPlayBtn(); }
  }
  lastRaf = ts;
  render(simTime);
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

function setPlayBtn() {
  document.getElementById('btn-play').textContent = playing ? '⏸' : '▶';
}

// Controls
document.getElementById('btn-play').addEventListener('click', () => {
  if (simTime >= DURATION) simTime = 0;
  playing = !playing;
  setPlayBtn();
});

document.getElementById('btn-prev-kf').addEventListener('click', () => {
  const { idx } = getState(simTime);
  const target = simTime > KEYFRAMES[idx].time + 0.1 ? KEYFRAMES[idx].time : KEYFRAMES[Math.max(0, idx-1)].time;
  simTime = target; playing = false; setPlayBtn();
});

document.getElementById('btn-next-kf').addEventListener('click', () => {
  const { idx } = getState(simTime);
  simTime = KEYFRAMES[Math.min(KEYFRAMES.length-1, idx+1)].time;
  playing = false; setPlayBtn();
});

document.querySelectorAll('.spd').forEach(btn => {
  btn.addEventListener('click', () => {
    speed = parseFloat(btn.dataset.spd);
    document.querySelectorAll('.spd').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

const scrubber = document.getElementById('scrubber');
scrubber.addEventListener('mousedown', () => { scrubberDragging = true; playing = false; setPlayBtn(); });
scrubber.addEventListener('touchstart', () => { scrubberDragging = true; playing = false; setPlayBtn(); }, {passive:true});
scrubber.addEventListener('input', () => { simTime = (scrubber.value / 1000) * DURATION; });
scrubber.addEventListener('mouseup', () => { scrubberDragging = false; });
scrubber.addEventListener('touchend', () => { scrubberDragging = false; });

// Touch swipe on canvas
let touchX0 = 0;
canvas.addEventListener('touchstart', e => { touchX0 = e.touches[0].clientX; }, {passive:true});
canvas.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchX0;
  if (Math.abs(dx) > 44) {
    const { idx } = getState(simTime);
    const next = dx < 0 ? Math.min(KEYFRAMES.length-1, idx+1) : Math.max(0, idx-1);
    simTime = KEYFRAMES[next].time;
    playing = false; setPlayBtn();
  }
}, {passive:true});

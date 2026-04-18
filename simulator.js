'use strict';

const canvas  = document.getElementById('floorplan');
const ctx     = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;

let currentStep = 0;
let playing = false;
let playInterval = null;
let focusedOp = null;

const overlayState = { operators: true, angles: false, roles: false, notes: false };

// ── Resize canvas to fill container while keeping aspect ratio ──
function resizeCanvas() {
  const wrap = document.getElementById('floorplan-wrap');
  const maxW = wrap.clientWidth  - 16;
  const maxH = wrap.clientHeight - 16;
  const scale = Math.min(maxW / W, maxH / H);
  canvas.style.width  = (W * scale) + 'px';
  canvas.style.height = (H * scale) + 'px';
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// ── Drawing helpers ──
function clearCanvas() {
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, W, H);
}

function drawRooms() {
  Object.entries(ROOMS).forEach(([key, r]) => {
    ctx.strokeStyle = '#30363d';
    ctx.lineWidth = 1.5;
    ctx.fillStyle = '#161b22';
    ctx.fillRect(r.x, r.y, r.w, r.h);
    ctx.strokeRect(r.x, r.y, r.w, r.h);

    ctx.fillStyle = '#8b949e';
    ctx.font = '9px SF Mono, Fira Code, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const lines = r.label.split('\n');
    const cx = r.x + r.w / 2;
    const cy = r.y + r.h / 2;
    lines.forEach((line, i) => {
      const offset = (i - (lines.length - 1) / 2) * 11;
      ctx.fillText(line, cx, cy + offset);
    });
  });
}

function drawDoors(step) {
  // Draw door markers
  ctx.font = '8px monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  Object.entries(DOORS).forEach(([key, d]) => {
    const isFront = key === 'front';
    ctx.strokeStyle = isFront ? '#f85149' : '#58a6ff';
    ctx.lineWidth = isFront ? 2.5 : 1.5;

    // Small arc to indicate door swing
    ctx.beginPath();
    if (d.side === 'W') {
      ctx.moveTo(d.x, d.y - 12);
      ctx.lineTo(d.x, d.y + 12);
    } else if (d.side === 'N') {
      ctx.moveTo(d.x - 12, d.y);
      ctx.lineTo(d.x + 12, d.y);
    } else if (d.side === 'S') {
      ctx.moveTo(d.x - 12, d.y);
      ctx.lineTo(d.x + 12, d.y);
    } else {
      ctx.moveTo(d.x, d.y - 12);
      ctx.lineTo(d.x, d.y + 12);
    }
    ctx.stroke();

    if (d.label) {
      ctx.fillStyle = '#58a6ff';
      ctx.fillText(d.label, d.x + 14, d.y);
    }
  });
}

function drawAngles(step) {
  if (!overlayState.angles) return;
  const angles = STEPS[step].angles || [];
  angles.forEach(a => {
    const op = OPERATORS[a.op];
    if (!op) return;
    const rad = (a.deg - 90) * Math.PI / 180;
    const spread = 25 * Math.PI / 180;
    const len = 55;

    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.arc(a.x, a.y, len, rad - spread, rad + spread);
    ctx.closePath();
    ctx.fillStyle = op.color + '30';
    ctx.fill();
    ctx.strokeStyle = op.color + '80';
    ctx.lineWidth = 1;
    ctx.stroke();
  });
}

function drawOperators(step) {
  if (!overlayState.operators) return;
  const positions = STEPS[step].positions;
  Object.entries(positions).forEach(([name, pos]) => {
    if (pos.x < 0) return; // off-canvas (staged outside)

    const op = OPERATORS[name];
    const isFocused = focusedOp === null || focusedOp === name;
    const alpha = isFocused ? 1 : 0.25;

    ctx.globalAlpha = alpha;

    // Operator circle
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);
    ctx.fillStyle = op.color;
    ctx.fill();
    ctx.strokeStyle = '#0d1117';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Name label
    ctx.fillStyle = '#e6edf3';
    ctx.font = 'bold 7px SF Mono, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(name[0], pos.x, pos.y);

    // Full name below
    ctx.font = '7px SF Mono, monospace';
    ctx.fillStyle = op.color;
    ctx.fillText(name, pos.x, pos.y + 13);

    ctx.globalAlpha = 1;
  });
}

function drawStagedOperators(step) {
  const positions = STEPS[step].positions;
  const staged = Object.entries(positions).filter(([, p]) => p.x < 0);
  if (staged.length === 0) return;

  // Draw small stack indicator outside left wall
  ctx.font = '8px monospace';
  ctx.textAlign = 'right';
  staged.forEach(([name, pos], i) => {
    const op = OPERATORS[name];
    const sy = 80 + i * 18;
    ctx.beginPath();
    ctx.arc(6, sy, 5, 0, Math.PI * 2);
    ctx.fillStyle = op.color;
    ctx.fill();
    ctx.fillStyle = op.color;
    ctx.textAlign = 'left';
    ctx.fillText(name[0], 14, sy + 1);
  });
}

function drawEventFlash(event) {
  if (!event) return;
  const colors = {
    breach: '#f85149',
    bang:   '#d29922',
    entry:  '#58a6ff',
    clear:  '#3fb950',
  };
  const c = colors[event] || '#fff';
  ctx.fillStyle = c + '18';
  ctx.fillRect(0, 0, W, H);

  ctx.font = 'bold 16px SF Mono, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = c;
}

// ── Main render ──
function render(step) {
  clearCanvas();
  drawRooms();
  drawDoors(step);
  drawAngles(step);
  drawStagedOperators(step);
  drawOperators(step);

  // Flash on event (brief visual)
  const event = STEPS[step].event;
  if (event) {
    drawEventFlash(event);
  }
}

// ── UI update ──
function updateUI(step) {
  const s = STEPS[step];

  document.getElementById('step-current').textContent = step + 1;
  document.getElementById('step-total').textContent = STEPS.length;

  document.getElementById('step-title').textContent = s.title || '';

  const calloutEl = document.getElementById('callout-text');
  calloutEl.textContent = s.callout || '';

  const teachEl = document.getElementById('teaching-text');
  if (overlayState.notes) {
    teachEl.textContent = s.teaching || '';
  } else {
    teachEl.textContent = '';
  }

  // Always show teaching if not using notes overlay
  teachEl.textContent = s.teaching || '';

  document.getElementById('btn-prev').disabled = step === 0;
  document.getElementById('btn-next').disabled = step === STEPS.length - 1;

  if (overlayState.operators) buildOperatorList(step);
}

// ── Operator tray ──
function buildOperatorList(step) {
  const list = document.getElementById('operator-list');
  list.innerHTML = '';
  const positions = STEPS[step].positions;
  Object.entries(OPERATORS).forEach(([name, op]) => {
    const pos = positions[name];
    const isActive = pos && pos.x >= 0;
    const div = document.createElement('div');
    div.className = 'op-item';
    div.style.opacity = isActive ? '1' : '0.4';
    div.innerHTML = `
      <div class="op-dot" style="background:${op.color}"></div>
      <span class="op-name">${name}</span>
      <span class="op-role">${op.role}</span>
    `;
    div.addEventListener('click', () => toggleFocusOp(name));
    list.appendChild(div);
  });
}

function toggleFocusOp(name) {
  focusedOp = focusedOp === name ? null : name;
  if (focusedOp) showRoleSheet(name);
  render(currentStep);
}

function showRoleSheet(name) {
  const op = OPERATORS[name];
  document.getElementById('role-sheet-name').textContent = `${name} — ${op.role}`;
  document.getElementById('role-sheet-name').style.color = op.color;

  const step = STEPS[currentStep];
  const pos = step.positions[name];
  const inPlay = pos && pos.x >= 0;

  document.getElementById('role-sheet-body').innerHTML = `
    <p><strong>Status this step:</strong> ${inPlay ? 'Active / deployed' : 'Staged / outside'}</p>
    <p style="margin-top:8px"><strong>Assigned role:</strong> ${op.role}</p>
    <p style="margin-top:8px"><strong>Step context:</strong> ${step.teaching || '—'}</p>
  `;

  document.getElementById('role-sheet').classList.remove('hidden');
}

document.getElementById('role-sheet-close').addEventListener('click', () => {
  document.getElementById('role-sheet').classList.add('hidden');
  focusedOp = null;
  render(currentStep);
});

// ── Step navigation ──
function goToStep(n) {
  currentStep = Math.max(0, Math.min(STEPS.length - 1, n));
  render(currentStep);
  updateUI(currentStep);
}

document.getElementById('btn-prev').addEventListener('click', () => {
  stopPlay();
  goToStep(currentStep - 1);
});

document.getElementById('btn-next').addEventListener('click', () => {
  stopPlay();
  goToStep(currentStep + 1);
});

// ── Autoplay ──
function startPlay() {
  playing = true;
  document.getElementById('btn-play').textContent = '⏸';
  document.getElementById('btn-play').classList.add('playing');
  playInterval = setInterval(() => {
    if (currentStep >= STEPS.length - 1) {
      stopPlay();
      return;
    }
    goToStep(currentStep + 1);
  }, 2000);
}

function stopPlay() {
  playing = false;
  clearInterval(playInterval);
  document.getElementById('btn-play').innerHTML = '&#9654;';
  document.getElementById('btn-play').classList.remove('playing');
}

document.getElementById('btn-play').addEventListener('click', () => {
  if (playing) stopPlay();
  else {
    if (currentStep >= STEPS.length - 1) goToStep(0);
    startPlay();
  }
});

// ── Overlay toggles ──
document.querySelectorAll('.ov-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const ov = btn.dataset.ov;
    overlayState[ov] = !overlayState[ov];
    btn.classList.toggle('active', overlayState[ov]);

    if (ov === 'operators') {
      const tray = document.getElementById('operator-tray');
      tray.classList.toggle('hidden', !overlayState[ov]);
    }

    render(currentStep);
    updateUI(currentStep);
  });
});

// ── Touch swipe for step navigation ──
let touchStartX = 0;
canvas.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, { passive: true });
canvas.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 40) {
    stopPlay();
    goToStep(currentStep + (dx < 0 ? 1 : -1));
  }
}, { passive: true });

// ── Init ──
goToStep(0);

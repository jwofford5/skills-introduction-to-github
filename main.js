'use strict';

const OP = {
  Rico:'#e74c3c', Chris:'#3498db', Mags:'#2ecc71', Manny:'#f39c12',
  Mike:'#9b59b6', Ian:'#1abc9c', Austin:'#e67e22', Ashley:'#e91e8c',
  Dylan:'#00bcd4', Cassidy:'#cddc39',
};
const NS = 'http://www.w3.org/2000/svg';

function add(p, tag, at) {
  const e = document.createElementNS(NS, tag);
  for (const [k,v] of Object.entries(at)) e.setAttribute(k,v);
  p.appendChild(e); return e;
}
function bg(s) { add(s,'rect',{x:0,y:0,width:340,height:220,fill:'#080d14'}); }
function rm(s,x,y,w,h,lbl) {
  add(s,'rect',{x,y,width:w,height:h,fill:'#0f1c2e'});
  if(lbl){ const t=add(s,'text',{x:x+w/2,y:y+h/2,'font-size':9,'font-family':'system-ui,sans-serif','font-weight':500,fill:'#1e3a5f','text-anchor':'middle','dominant-baseline':'middle'}); t.textContent=lbl; }
}
function op(s,x,y,name,color,r) {
  r=r||11;
  const g=document.createElementNS(NS,'g');
  add(g,'circle',{cx:x,cy:y,r,fill:'#0a1525',stroke:color,'stroke-width':2});
  const ini=name.length<=3?name:name.slice(0,2);
  const t=add(g,'text',{x,y:y+1,'font-size':r<10?6:ini.length>2?7:8,'font-family':'system-ui,sans-serif','font-weight':700,fill:color,'text-anchor':'middle','dominant-baseline':'middle'});
  t.textContent=ini;
  if(r>=10){ const n=add(g,'text',{x,y:y+r+8,'font-size':6,'font-family':'system-ui,sans-serif','font-weight':600,fill:color,opacity:0.85,'text-anchor':'middle','dominant-baseline':'auto'}); n.textContent=name; }
  s.appendChild(g);
}
function cone(s,x,y,deg,spread,color) {
  const r=(deg-90)*Math.PI/180, sp=(spread/2)*Math.PI/180, L=52;
  const x1=x+L*Math.cos(r-sp),y1=y+L*Math.sin(r-sp),x2=x+L*Math.cos(r+sp),y2=y+L*Math.sin(r+sp);
  add(s,'path',{d:`M${x},${y} L${x1},${y1} A${L},${L} 0 0 1 ${x2},${y2} Z`,fill:color+'28',stroke:color+'70','stroke-width':0.7});
}
function arr(s,x1,y1,x2,y2,color) {
  const id='m'+Math.random().toString(36).slice(2);
  const df=add(s,'defs',{}); const mk=add(df,'marker',{id,markerWidth:6,markerHeight:6,refX:5,refY:3,orient:'auto'});
  add(mk,'path',{d:'M0,0 L6,3 L0,6 Z',fill:color});
  add(s,'line',{x1,y1,x2,y2,stroke:color,'stroke-width':1.5,'marker-end':`url(#${id})`});
}
function lbl(s,x,y,text,color,size,anchor) {
  const t=add(s,'text',{x,y,'font-size':size||8,'font-family':'system-ui,sans-serif',fill:color||'#5a7a9a','text-anchor':anchor||'middle','dominant-baseline':'middle'});
  t.textContent=text;
}
function doorV(s,x,y,len,color) { add(s,'line',{x1:x,y1:y,x2:x,y2:y+len,stroke:color,'stroke-width':2.5,'stroke-linecap':'round'}); }
function doorH(s,x,y,len,color) { add(s,'line',{x1:x,y1:y,x2:x+len,y2:y,stroke:color,'stroke-width':2.5,'stroke-linecap':'round'}); }
function wall(s,x,y,x2,y2) { add(s,'line',{x1:x,y1:y,x2,y2,stroke:'#2a4a6a','stroke-width':1.5}); }
function bubble(s,x,y,w,h,text,color) {
  add(s,'rect',{x,y,width:w,height:h,rx:5,fill:'#0d1a2a',stroke:color,'stroke-width':1});
  add(s,'path',{d:`M${x+16},${y+h} L${x+8},${y+h+8} L${x+26},${y+h} Z`,fill:'#0d1a2a',stroke:color,'stroke-width':1});
  const t=add(s,'text',{x:x+w/2,y:y+h/2,'font-size':8,'font-family':'monospace','font-weight':600,fill:color,'text-anchor':'middle','dominant-baseline':'middle'});
  t.textContent=text;
}

// ── Scenes ───────────────────────────────────────────────────────────────────
function sceneStack(s) {
  bg(s);
  rm(s,120,0,220,220,'');
  lbl(s,230,110,'Building Interior','#1e3a5f',11);
  wall(s,120,0,120,78); wall(s,120,148,120,220);
  doorV(s,120,78,70,'#ef4444');
  lbl(s,104,113,'FRONT','#ef4444',7);
  const names=['Chris','Mags','Manny','Mike','Ian','Austin','Ashley','Dylan','Cassidy','Rico'];
  names.forEach((n,i)=>op(s,62,18+i*20,n,OP[n],8));
  lbl(s,62,8,'POINT','#3498db',6); lbl(s,62,208,'COMMAND','#e74c3c',6);
}
function sceneLimitedPen(s) {
  bg(s); rm(s,60,10,260,200,'Living Room');
  wall(s,60,0,60,85); wall(s,60,135,60,220);
  doorV(s,60,85,50,'#ef4444'); lbl(s,44,110,'FRONT','#ef4444',7);
  cone(s,112,110,355,50,OP.Chris);
  op(s,112,110,'Chris',OP.Chris);
  lbl(s,200,45,'deep corner →','#5a7a9a',8);
  add(s,'line',{x1:60,y1:110,x2:97,y2:110,stroke:OP.Chris,'stroke-width':1.5,'stroke-dasharray':'4 2',opacity:0.5});
  lbl(s,112,190,'stop here','#5a7a9a',8);
  add(s,'line',{x1:90,y1:190,x2:135,y2:190,stroke:'#ef4444','stroke-width':1,'stroke-dasharray':'3 2',opacity:0.6});
}
function sceneButtonHook(s) {
  bg(s); rm(s,60,10,260,200,'Living Room');
  wall(s,60,0,60,85); wall(s,60,135,60,220);
  doorV(s,60,85,50,'#ef4444'); lbl(s,44,110,'FRONT','#ef4444',7);
  op(s,112,70,'Chris',OP.Chris); op(s,112,150,'Mags',OP.Mags);
  arr(s,55,97,107,73,OP.Chris); arr(s,55,123,107,147,OP.Mags);
  lbl(s,160,55,'left entry',OP.Chris,8); lbl(s,164,168,'button hook right',OP.Mags,8);
  lbl(s,235,110,'stack flows','#5a7a9a',8); lbl(s,235,122,'through here','#5a7a9a',8);
}
function sceneAngleAdj(s) {
  bg(s);
  rm(s,30,10,170,200,'Living Room');
  rm(s,210,10,120,80,'Family Room'); rm(s,210,140,120,70,'Hallway');
  wall(s,200,0,200,10); wall(s,200,90,200,130); wall(s,200,210,200,220);
  lbl(s,200,110,'wall','#2a4a6a',7);
  cone(s,95,60,40,38,OP.Chris); op(s,95,60,'Chris',OP.Chris);
  cone(s,95,160,140,38,OP.Mags); op(s,95,160,'Mags',OP.Mags);
  lbl(s,268,50,'family room',OP.Chris,7.5); lbl(s,254,185,'hallway',OP.Mags,7.5);
}
function sceneHallwayPoint(s) {
  bg(s); rm(s,20,70,300,80,'Hallway');
  op(s,75,110,'Manny',OP.Manny);
  bubble(s,120,55,195,36,'"Hallway right, Manny on point."',OP.Manny);
  arr(s,98,110,230,110,OP.Manny);
  lbl(s,290,110,'→','#5a7a9a',10);
}
function sceneClosedDoor(s) {
  bg(s); rm(s,20,75,300,70,'Hallway'); rm(s,20,10,110,60,'Room 1');
  doorH(s,20,75,90,'#f59e0b'); lbl(s,65,65,'CLOSED','#f59e0b',7);
  op(s,240,110,'Manny',OP.Manny); arr(s,165,110,220,110,OP.Manny);
  lbl(s,240,92,'bumps past','#5a7a9a',7);
  op(s,118,110,'Cassidy',OP.Cassidy);
  lbl(s,118,132,'sets on door','#cddc39',7); lbl(s,118,143,'knob side','#5a7a9a',7);
  lbl(s,170,190,'point protects point','#5a7a9a',8);
}
function sceneOpenDoor(s) {
  bg(s); rm(s,20,75,300,70,'Hallway'); rm(s,20,10,110,60,'Last Room');
  doorH(s,20,75,80,'#22c55e'); lbl(s,58,65,'OPEN','#22c55e',7);
  const r=70; add(s,'path',{d:`M20,75 L${20+r},75 A${r},${r} 0 0 0 20,${75+r} Z`,fill:'none',stroke:'#22c55e','stroke-width':1,'stroke-dasharray':'3 2',opacity:0.5});
  op(s,78,110,'Manny',OP.Manny);
  add(s,'line',{x1:100,y1:76,x2:100,y2:143,stroke:'#ef4444','stroke-width':1.5,'stroke-dasharray':'4 2'});
  lbl(s,145,88,'STOP SHORT','#ef4444',8); lbl(s,140,102,'hug the wall','#5a7a9a',8);
  lbl(s,240,110,'do NOT move','#5a7a9a',8); lbl(s,240,122,'past open door','#5a7a9a',8);
}
function sceneDoorSides(s) {
  bg(s); rm(s,20,10,130,200,'Hallway'); rm(s,160,10,170,200,'Room');
  wall(s,150,0,150,80); wall(s,150,150,150,220);
  doorV(s,150,80,70,'#f59e0b');
  add(s,'path',{d:`M150,80 L${150+60},80 A60,60 0 0 1 150,140 Z`,fill:'none',stroke:'#f59e0b','stroke-width':1,'stroke-dasharray':'3 2',opacity:0.4});
  add(s,'circle',{cx:150,cy:82,r:3,fill:'#5a7a9a'});
  lbl(s,132,76,'HINGE','#5a7a9a',7);
  add(s,'circle',{cx:150,cy:113,r:3,fill:'#f59e0b'});
  lbl(s,132,116,'KNOB','#f59e0b',7);
  op(s,80,82,'Hinge','#1abc9c'); lbl(s,80,104,'enters first','#1abc9c',7);
  op(s,80,148,'Knob','#e67e22'); lbl(s,80,170,'opens + bang','#e67e22',7);
  lbl(s,245,50,'HINGE SIDE','#1abc9c',8); lbl(s,245,62,'enters first','#1abc9c',7);
  lbl(s,245,145,'KNOB SIDE','#e67e22',8); lbl(s,245,157,'opens door','#e67e22',7); lbl(s,245,168,'deploys bang','#e67e22',7);
}
function sceneBang(s) {
  bg(s); rm(s,20,10,130,200,'Corridor'); rm(s,160,10,170,200,'Room');
  wall(s,150,0,150,80); wall(s,150,150,150,220);
  doorV(s,150,80,70,'#f59e0b');
  const step=(txt,x,y,c)=>{ add(s,'rect',{x,y,width:105,height:22,rx:3,fill:'rgba(14,26,42,0.85)',stroke:c,'stroke-width':0.8}); lbl(s,x+52,y+11,txt,c,7.5); };
  step('1 · SET ON DOOR',22,18,'#5a7a9a'); step('2 · OPEN + BANG',22,98,'#f59e0b'); step('3 · ENTER',22,172,'#22c55e');
  op(s,108,100,'Austin',OP.Austin); op(s,108,162,'Dylan',OP.Dylan);
  arr(s,143,98,195,88,OP.Austin); arr(s,143,162,195,148,OP.Dylan);
  lbl(s,262,88,'Austin',OP.Austin,7); lbl(s,262,148,'Dylan',OP.Dylan,7);
  lbl(s,170,210,'no pause — open → bang → enter','#5a7a9a',7.5);
}
function sceneFirstIn(s) {
  bg(s); rm(s,20,10,300,195,'Room');
  doorH(s,132,205,76,'#f59e0b'); lbl(s,170,214,'entry','#5a7a9a',7);
  cone(s,72,55,315,40,OP.Ashley); op(s,72,55,'Ashley',OP.Ashley); lbl(s,72,78,'entered first',OP.Ashley,7);
  cone(s,262,152,215,40,OP.Cassidy); op(s,262,152,'Cassidy',OP.Cassidy); lbl(s,262,175,'followed',OP.Cassidy,7);
  add(s,'rect',{x:96,y:95,width:148,height:38,rx:4,fill:'rgba(8,13,20,0.88)',stroke:'#1e3048','stroke-width':1});
  lbl(s,170,108,'FIRST IN = LAST OUT','#dde6f0',8); lbl(s,170,124,'own this room until relieved','#5a7a9a',7.5);
}
function sceneTrailer(s) {
  bg(s); rm(s,20,10,190,115,'Kitchen'); rm(s,20,135,190,75,'Bathroom'); rm(s,222,10,108,200,'Hallway');
  doorH(s,20,135,100,'#f59e0b'); lbl(s,65,126,'CLOSED','#f59e0b',7);
  op(s,88,62,'Austin',OP.Austin);
  bubble(s,110,38,95,26,'"Trailer."',OP.Austin);
  op(s,268,105,'Dylan',OP.Dylan); arr(s,248,118,215,148,OP.Dylan);
  lbl(s,268,88,'responds','#00bcd4',7); lbl(s,268,100,'posts on door','#5a7a9a',7);
}

// ── Concepts ─────────────────────────────────────────────────────────────────
const CONCEPTS = [
  { num:1, title:'Stack Formation', fn:sceneStack,
    body:'The team forms a tight line outside the entry point in a set order before the command to move. Everyone knows their position before the approach begins.',
    rule:'Rico is rear command. Chris is on point. Order is set before the approach.' },
  { num:2, title:'Limited Penetration', fn:sceneLimitedPen,
    body:'The first operator enters just far enough to clear the immediate threat area. You do not blow through the room. You stop, hold your corner, and wait for the stack.',
    rule:'Enter. Stop. Hold. Deep corner first, then gaze toward center.' },
  { num:3, title:'Button Hook', fn:sceneButtonHook,
    body:'The second operator follows point through the door and immediately hooks to the opposite side. Chris goes left. Mags hooks right.',
    rule:'They hold position with enough room for the rest of the stack to enter.' },
  { num:4, title:'Angle Adjustment', fn:sceneAngleAdj,
    body:'Once the stack is inside, Chris and Mags shift their angles so the team can move up without crossing muzzles.',
    rule:'Chris angles toward the family room opening. Mags angles toward the hallway opening.' },
  { num:5, title:'Calling Hallway Point', fn:sceneHallwayPoint,
    callout:'Manny: "Hallway right, Manny on point."',
    body:'When a hallway is identified, point claims it with a verbal callout. The name is included on the first announcement only.',
    rule:'Say the name once. Subsequent hallway calls do not repeat it.' },
  { num:6, title:'Closed Door Procedure', fn:sceneClosedDoor,
    body:'When point encounters a closed door in the hallway, he bumps past it. The operator directly behind him moves with him, sets on the door, and protects his back.',
    rule:'Point bumps past. The operator behind sets on the door — doorknob side.' },
  { num:7, title:'Open Door Procedure', fn:sceneOpenDoor,
    body:'An open door is treated differently from a closed one. Point does NOT bump past. He stops short and hugs the wall next to the opening.',
    rule:'Stop short. Hug the wall. Do not move past an open door.' },
  { num:8, title:'Doorknob Side vs Hinge Side', fn:sceneDoorSides,
    body:'Every door entry has two positions. The operator on the doorknob side controls the door. The operator on the hinge side enters first.',
    rule:'Doorknob side opens and deploys the bang. Hinge side enters first.' },
  { num:9, title:'Bang Deployment', fn:sceneBang,
    body:'Before entry, a distraction device goes in. The operator on the doorknob side opens the door and deploys the bang. Entry follows immediately.',
    rule:'Open → bang → enter. Do not pause between bang and entry.' },
  { num:10, title:'First In, Last Out', fn:sceneFirstIn,
    body:'The first operator through the door owns that room. They are responsible for it until told otherwise. They do not leave until the room is detailed.',
    rule:'First in = last out. You detail the room — you do not just hold it.' },
  { num:11, title:'Trailer', fn:sceneTrailer,
    callout:'Austin: "Trailer."',
    body:'The Trailer is a designated operator held in reserve. When a secondary threat area is discovered — like a closed door inside a room — the Trailer is called.',
    rule:'The Trailer responds to the call and posts on the location. Dylan responds to the bathroom.' },
  { num:12, title:'Radio Callouts', fn:null,
    body:null, rule:null,
    traffic:[
      { who:'RICO',   color:OP.Rico,   text:'"Initiate."',                      note:'Command to begin. Rico only.' },
      { who:'MANNY',  color:OP.Manny,  text:'"Hallway right, Manny on point."', note:'First call — name included.' },
      { who:'MANNY',  color:OP.Manny,  text:'"Closed door right."',             note:'Hallway — first door.' },
      { who:'MANNY',  color:OP.Manny,  text:'"Closed door left."',              note:'Hallway — second door.' },
      { who:'MANNY',  color:OP.Manny,  text:'"Last room, open door left."',     note:'Exact wording. Open = stop short.' },
      { who:'AUSTIN', color:OP.Austin, text:'"Trailer."',                       note:'Calls the designated Trailer.' },
      { who:'RICO',   color:OP.Rico,   text:'"House is clear."',                note:'All rooms detailed. Rico confirms.' },
    ]},
];

// ── Render ────────────────────────────────────────────────────────────────────
let cur = 0;

function render(idx) {
  const c = CONCEPTS[idx];
  const scSvg = document.getElementById('scene-svg');
  const radio = document.getElementById('radio-traffic');
  const textWrap = document.getElementById('text-wrap');

  document.getElementById('concept-counter').textContent = `${idx+1} / ${CONCEPTS.length}`;
  document.getElementById('concept-num-label').textContent = `CONCEPT ${idx+1}`;
  document.getElementById('concept-title').textContent = c.title;

  const callEl = document.getElementById('concept-callout');
  if (c.callout) { callEl.textContent = c.callout; callEl.classList.remove('hidden'); }
  else callEl.classList.add('hidden');

  const bodyEl = document.getElementById('concept-body');
  if (c.body) { bodyEl.textContent = c.body; bodyEl.style.display = ''; }
  else bodyEl.style.display = 'none';

  const ruleEl = document.getElementById('concept-rule');
  if (c.rule) { ruleEl.textContent = c.rule; ruleEl.classList.remove('hidden'); }
  else ruleEl.classList.add('hidden');

  if (c.traffic) {
    scSvg.classList.add('hidden');
    textWrap.classList.add('hidden');
    radio.classList.remove('hidden');
    radio.innerHTML = '<div class="traffic-header">RADIO TRAFFIC</div>';
    for (const row of c.traffic) {
      const d = document.createElement('div');
      d.className = 'traffic-row';
      d.innerHTML = `<span class="traffic-callsign" style="color:${row.color}">${row.who}</span><span class="traffic-text">${row.text}</span><span class="traffic-note">${row.note}</span>`;
      radio.appendChild(d);
    }
  } else {
    radio.classList.add('hidden');
    textWrap.classList.remove('hidden');
    scSvg.classList.remove('hidden');
    while (scSvg.firstChild) scSvg.removeChild(scSvg.firstChild);
    if (c.fn) c.fn(scSvg);
  }

  document.querySelectorAll('.dot').forEach((d,i) => d.classList.toggle('active', i===idx));
  document.getElementById('btn-prev').disabled = idx === 0;
  document.getElementById('btn-next').disabled = idx === CONCEPTS.length-1;
}

function goTo(idx) { cur = Math.max(0, Math.min(CONCEPTS.length-1, idx)); render(cur); }

// ── Init ──────────────────────────────────────────────────────────────────────
const dots = document.getElementById('dots');
CONCEPTS.forEach((_,i) => { const d=document.createElement('div'); d.className='dot'; d.addEventListener('click',()=>goTo(i)); dots.appendChild(d); });

document.getElementById('btn-prev').addEventListener('click', () => goTo(cur-1));
document.getElementById('btn-next').addEventListener('click', () => goTo(cur+1));

let tx0=0;
['scene-svg','radio-traffic'].forEach(id => {
  const el=document.getElementById(id);
  el.addEventListener('touchstart', e=>{ tx0=e.touches[0].clientX; },{passive:true});
  el.addEventListener('touchend',   e=>{ const dx=e.changedTouches[0].clientX-tx0; if(Math.abs(dx)>44) goTo(cur+(dx<0?1:-1)); },{passive:true});
});

goTo(0);

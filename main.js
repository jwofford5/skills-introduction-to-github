'use strict';
const OP={Rico:'#e74c3c',Chris:'#3498db',Mags:'#2ecc71',Manny:'#f39c12',Mike:'#9b59b6',Ian:'#1abc9c',Austin:'#e67e22',Ashley:'#e91e8c',Dylan:'#00bcd4',Cassidy:'#cddc39'};
const NS='http://www.w3.org/2000/svg';

function add(p,tag,at){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(at))e.setAttribute(k,v);p.appendChild(e);return e;}
function bg(s){add(s,'rect',{x:0,y:0,width:340,height:220,fill:'#080d14'});}
function rm(s,x,y,w,h,lbl){
  add(s,'rect',{x,y,width:w,height:h,fill:'#0f1c2e'});
  if(lbl){const t=add(s,'text',{x:x+w/2,y:y+h/2,'font-size':9,'font-family':'system-ui,sans-serif','font-weight':500,fill:'#1a3550','text-anchor':'middle','dominant-baseline':'middle'});t.textContent=lbl;}
}
// Architectural door: hinge at hx,hy; panel shown in open pos; arc shows swing
// closedDeg: 0=up,90=right,180=down,270=left; cw=swings CW on screen
function door(s,hx,hy,len,closedDeg,cw,color){
  const c=(closedDeg-90)*Math.PI/180;
  const cx0=hx+len*Math.cos(c),cy0=hy+len*Math.sin(c);
  const o=cw?c+Math.PI/2:c-Math.PI/2;
  const ox=hx+len*Math.cos(o),oy=hy+len*Math.sin(o);
  add(s,'line',{x1:hx,y1:hy,x2:ox,y2:oy,stroke:color,'stroke-width':2.5,'stroke-linecap':'round'});
  add(s,'path',{d:`M${cx0.toFixed(1)},${cy0.toFixed(1)} A${len},${len} 0 0 ${cw?1:0} ${ox.toFixed(1)},${oy.toFixed(1)}`,fill:'none',stroke:color,'stroke-width':1.2,opacity:0.45,'stroke-dasharray':'3 2'});
}
function op(s,x,y,name,color,r,faceDeg){
  r=r||11;
  const g=document.createElementNS(NS,'g');
  add(g,'circle',{cx:x,cy:y,r,fill:'#0a1525',stroke:color,'stroke-width':2});
  const ini=name.length<=3?name:name.slice(0,2);
  const t=add(g,'text',{x,y:y+1,'font-size':r<10?6:ini.length>2?7:8.5,'font-family':'system-ui,sans-serif','font-weight':700,fill:color,'text-anchor':'middle','dominant-baseline':'middle'});
  t.textContent=ini;
  if(r>=10){const n=add(g,'text',{x,y:y+r+8,'font-size':6,'font-family':'system-ui,sans-serif','font-weight':600,fill:color,opacity:0.85,'text-anchor':'middle','dominant-baseline':'auto'});n.textContent=name;}
  if(faceDeg!==undefined){
    const a=(faceDeg-90)*Math.PI/180,d=r+5;
    const tx=x+d*Math.cos(a),ty=y+d*Math.sin(a);
    const a1=a-0.6,a2=a+0.6,tip=5;
    add(g,'polygon',{points:`${(tx+tip*Math.cos(a)).toFixed(1)},${(ty+tip*Math.sin(a)).toFixed(1)} ${(x+(r+2)*Math.cos(a1)).toFixed(1)},${(y+(r+2)*Math.sin(a1)).toFixed(1)} ${(x+(r+2)*Math.cos(a2)).toFixed(1)},${(y+(r+2)*Math.sin(a2)).toFixed(1)}`,fill:color});
  }
  s.appendChild(g);
}
function zone(s,x,y,deg,spread,len,color){
  const r=(deg-90)*Math.PI/180,sp=(spread/2)*Math.PI/180,L=len||55;
  const x1=x+L*Math.cos(r-sp),y1=y+L*Math.sin(r-sp),x2=x+L*Math.cos(r+sp),y2=y+L*Math.sin(r+sp);
  add(s,'path',{d:`M${x},${y} L${x1.toFixed(1)},${y1.toFixed(1)} A${L},${L} 0 0 1 ${x2.toFixed(1)},${y2.toFixed(1)} Z`,fill:color+'28',stroke:color+'70','stroke-width':0.8});
}
function movePath(s,x1,y1,x2,y2,color){add(s,'line',{x1,y1,x2,y2,stroke:color,'stroke-width':2,'stroke-dasharray':'5 3',opacity:0.6,'stroke-linecap':'round'});}
function arr(s,x1,y1,x2,y2,color){
  const id='m'+Math.random().toString(36).slice(2,7);
  const df=add(s,'defs',{});const mk=add(df,'marker',{id,markerWidth:6,markerHeight:6,refX:5,refY:3,orient:'auto'});
  add(mk,'path',{d:'M0,0 L6,3 L0,6 Z',fill:color});
  add(s,'line',{x1,y1,x2,y2,stroke:color,'stroke-width':1.8,'marker-end':`url(#${id})`});
}
function lbl(s,x,y,text,color,size,anchor){
  const t=add(s,'text',{x,y,'font-size':size||8,'font-family':'system-ui,sans-serif',fill:color||'#5a7a9a','text-anchor':anchor||'middle','dominant-baseline':'middle'});
  t.textContent=text;return t;
}
function tag(s,x,y,text,color){
  const w=text.length*5+10;
  add(s,'rect',{x:x-w/2,y:y-8,width:w,height:16,rx:3,fill:color+'18',stroke:color+'55','stroke-width':0.8});
  lbl(s,x,y,text,color,7.5);
}
function bubble(s,x,y,w,h,text,color){
  add(s,'rect',{x,y,width:w,height:h,rx:5,fill:'#0d1a2a',stroke:color,'stroke-width':1.2});
  add(s,'path',{d:`M${x+16},${y+h} L${x+8},${y+h+9} L${x+28},${y+h} Z`,fill:'#0d1a2a',stroke:color,'stroke-width':1.2});
  const t=add(s,'text',{x:x+w/2,y:y+h/2,'font-size':8,'font-family':'monospace','font-weight':600,fill:color,'text-anchor':'middle','dominant-baseline':'middle'});
  t.textContent=text;
}

// ── Scene 1: Stack Formation ──────────────────────────────────────────────────
function sceneStack(s){
  bg(s);rm(s,110,0,230,220,'');lbl(s,225,110,'Building Interior','#1a3550',11);
  add(s,'line',{x1:110,y1:0,x2:110,y2:85,stroke:'#2a4a6a','stroke-width':1.5});
  add(s,'line',{x1:110,y1:152,x2:110,y2:220,stroke:'#2a4a6a','stroke-width':1.5});
  door(s,110,85,67,180,false,'#ef4444');
  tag(s,78,118,'FRONT DOOR','#ef4444');
  const names=['Chris','Mags','Manny','Mike','Ian','Austin','Ashley','Dylan','Cassidy','Rico'];
  const ys=[14,34,54,74,94,114,134,154,174,194];
  names.forEach((n,i)=>{op(s,58,ys[i],n,OP[n],8,90);lbl(s,26,ys[i],String(i+1),'#2a4a6a',7);});
  lbl(s,58,4,'POINT ↓',OP.Chris,6.5);lbl(s,58,208,'COMMAND',OP.Rico,6.5);
}

// ── Scene 2: Limited Penetration ─────────────────────────────────────────────
function sceneLimitedPen(s){
  bg(s);rm(s,12,8,318,204,'Living Room');
  add(s,'line',{x1:12,y1:8,x2:12,y2:82,stroke:'#2a4a6a','stroke-width':1.5});
  add(s,'line',{x1:12,y1:150,x2:12,y2:212,stroke:'#2a4a6a','stroke-width':1.5});
  door(s,12,82,68,180,false,'#ef4444');
  movePath(s,12,116,100,116,OP.Chris);
  zone(s,100,116,35,55,170,OP.Chris);
  op(s,100,116,'Chris',OP.Chris,13,35);
  tag(s,56,105,'STOP SHORT','#ef4444');
  add(s,'line',{x1:100,y1:88,x2:100,y2:132,stroke:'#ef4444','stroke-width':1.2,'stroke-dasharray':'3 2',opacity:0.7});
  lbl(s,272,38,'deep corner','#5a7a9a',8);lbl(s,272,50,'first  ↗','#5a7a9a',8);
}

// ── Scene 3: Button Hook ──────────────────────────────────────────────────────
function sceneButtonHook(s){
  bg(s);rm(s,12,8,318,204,'Living Room');
  add(s,'line',{x1:12,y1:8,x2:12,y2:82,stroke:'#2a4a6a','stroke-width':1.5});
  add(s,'line',{x1:12,y1:150,x2:12,y2:212,stroke:'#2a4a6a','stroke-width':1.5});
  door(s,12,82,68,180,false,'#ef4444');
  movePath(s,12,102,90,68,OP.Chris);
  zone(s,90,68,20,45,115,OP.Chris);
  op(s,90,68,'Chris',OP.Chris,13,20);
  tag(s,90,40,'LIMITED PENETRATION',OP.Chris);
  movePath(s,12,132,90,162,OP.Mags);
  zone(s,90,162,160,45,115,OP.Mags);
  op(s,90,162,'Mags',OP.Mags,13,160);
  tag(s,90,192,'BUTTON HOOK',OP.Mags);
  lbl(s,245,115,'stack flows','#5a7a9a',8);lbl(s,245,127,'through here','#5a7a9a',8);
}

// ── Scene 4: Angle Adjustment ─────────────────────────────────────────────────
function sceneAngleAdj(s){
  bg(s);rm(s,12,8,175,204,'Living Room');
  rm(s,198,8,132,82,'Family Room');rm(s,198,138,132,74,'Hallway');
  add(s,'rect',{x:187,y:90,width:11,height:48,fill:'#080d14'});
  add(s,'line',{x1:12,y1:8,x2:12,y2:78,stroke:'#2a4a6a','stroke-width':1.5});
  add(s,'line',{x1:12,y1:148,x2:12,y2:212,stroke:'#2a4a6a','stroke-width':1.5});
  door(s,12,78,70,180,false,'#ef4444');
  zone(s,95,62,56,42,140,OP.Chris);op(s,95,62,'Chris',OP.Chris,13,56);
  lbl(s,264,50,'family room',OP.Chris,7.5);lbl(s,264,62,'opening →',OP.Chris,7);
  zone(s,95,158,124,42,140,OP.Mags);op(s,95,158,'Mags',OP.Mags,13,124);
  lbl(s,264,162,'hallway',OP.Mags,7.5);lbl(s,264,174,'opening →',OP.Mags,7);
}

// ── Scene 5: Hallway Point ────────────────────────────────────────────────────
function sceneHallwayPoint(s){
  bg(s);rm(s,20,55,300,110,'');lbl(s,170,110,'Hallway','#1a3550',10);
  zone(s,62,110,90,22,240,OP.Manny);
  op(s,62,110,'Manny',OP.Manny,13,90);
  bubble(s,85,18,200,32,'"Hallway right, Manny on point."',OP.Manny);
  add(s,'line',{x1:93,y1:50,x2:70,y2:88,stroke:OP.Manny,'stroke-width':0.8,opacity:0.5});
  arr(s,200,110,300,110,OP.Manny);
  tag(s,258,128,'POINT CLAIMED',OP.Manny);
}

// ── Scene 6: Closed Door Procedure ───────────────────────────────────────────
function sceneClosedDoor(s){
  bg(s);rm(s,20,72,300,90,'Hallway');rm(s,20,8,110,60,'Room 1');
  door(s,20,72,60,90,false,'#f59e0b');
  tag(s,50,62,'CLOSED','#f59e0b');
  movePath(s,20,117,250,117,OP.Manny);
  op(s,250,117,'Manny',OP.Manny,13,90);tag(s,250,96,'BUMPS PAST',OP.Manny);
  op(s,85,117,'Cassidy',OP.Cassidy,13,0);tag(s,85,140,'KNOB SIDE',OP.Cassidy);
  lbl(s,170,185,'point moves past — support sets on door','#5a7a9a',7.5);
}

// ── Scene 7: Open Door Procedure ──────────────────────────────────────────────
function sceneOpenDoor(s){
  bg(s);rm(s,20,72,300,90,'Hallway');rm(s,20,8,110,60,'Last Room');
  door(s,20,72,60,90,false,'#22c55e');
  tag(s,50,62,'OPEN','#22c55e');
  movePath(s,20,117,55,117,OP.Manny);
  op(s,55,117,'Manny',OP.Manny,13,90);
  add(s,'line',{x1:78,y1:73,x2:78,y2:160,stroke:'#ef4444','stroke-width':2,'stroke-dasharray':'4 2'});
  tag(s,130,105,'STOP SHORT','#ef4444');
  lbl(s,130,120,'hug the wall','#5a7a9a',8);
  lbl(s,240,107,'CLOSED door:','#5a7a9a',8);lbl(s,240,119,'bump past','#5a7a9a',8);
  lbl(s,240,138,'OPEN door:','#22c55e',8);lbl(s,240,150,'stop short','#22c55e',8);
}

// ── Scene 8: Doorknob vs Hinge Side ──────────────────────────────────────────
function sceneDoorSides(s){
  bg(s);rm(s,10,8,152,204,'Corridor');rm(s,175,8,155,204,'Room');
  add(s,'rect',{x:162,y:8,width:13,height:204,fill:'#080d14'});
  door(s,162,55,100,180,false,'#f59e0b');
  add(s,'circle',{cx:162,cy:55,r:4,fill:'#1abc9c'});
  tag(s,135,48,'HINGE','#1abc9c');
  add(s,'circle',{cx:162,cy:155,r:4,fill:'#f59e0b'});
  tag(s,135,158,'KNOB','#f59e0b');
  op(s,105,58,'Hinge','#1abc9c',13,90);tag(s,105,34,'ENTERS FIRST','#1abc9c');
  op(s,105,158,'Knob','#e67e22',13,90);tag(s,105,182,'OPENS + BANG','#e67e22');
  arr(s,124,58,218,54,'#1abc9c');
  lbl(s,250,54,'enters',OP.Ian,7.5);lbl(s,250,64,'first',OP.Ian,7.5);
}

// ── Scene 9: Bang Deployment ──────────────────────────────────────────────────
function sceneBang(s){
  bg(s);rm(s,10,8,148,204,'Corridor');rm(s,175,8,155,204,'Room');
  add(s,'rect',{x:162,y:8,width:13,height:204,fill:'#080d14'});
  door(s,162,58,96,180,false,'#f59e0b');
  [['1 · SET ON DOOR','#5a7a9a',20],['2 · OPEN + BANG','#f59e0b',86],['3 · ENTER','#22c55e',152]].forEach(([txt,col,y])=>{
    add(s,'rect',{x:14,y,width:118,height:28,rx:4,fill:'rgba(10,21,37,0.9)',stroke:col,'stroke-width':1.2});
    lbl(s,73,y+14,txt,col,8);
  });
  op(s,128,88,'Austin',OP.Austin,11,90);
  op(s,128,158,'Dylan',OP.Dylan,11,90);
  arr(s,145,88,215,78,OP.Austin);arr(s,145,158,215,144,OP.Dylan);
  lbl(s,253,78,'Austin enters',OP.Austin,7);lbl(s,253,144,'Dylan follows',OP.Dylan,7);
  lbl(s,170,208,'open → bang → enter  no pause','#5a7a9a',7.5);
}

// ── Scene 10: First In, Last Out ──────────────────────────────────────────────
function sceneFirstIn(s){
  bg(s);rm(s,15,12,310,192,'Room');
  door(s,155,204,58,90,false,'#f59e0b');
  tag(s,185,212,'ENTRY','#5a7a9a');
  movePath(s,183,196,52,48,OP.Ashley);
  zone(s,52,48,315,50,105,OP.Ashley);
  op(s,52,48,'Ashley',OP.Ashley,13,315);
  tag(s,52,24,'FIRST IN',OP.Ashley);
  movePath(s,183,196,278,158,OP.Cassidy);
  zone(s,278,158,225,50,105,OP.Cassidy);
  op(s,278,158,'Cassidy',OP.Cassidy,13,225);
  tag(s,278,184,'FOLLOWED',OP.Cassidy);
  add(s,'rect',{x:102,y:92,width:136,height:40,rx:5,fill:'rgba(8,13,20,0.9)',stroke:'#1e3048','stroke-width':1});
  lbl(s,170,106,'FIRST IN = LAST OUT','#dde6f0',8.5);
  lbl(s,170,122,'own this room until relieved','#5a7a9a',7.5);
}

// ── Scene 11: Trailer ─────────────────────────────────────────────────────────
function sceneTrailer(s){
  bg(s);rm(s,15,8,185,108,'Kitchen');rm(s,15,128,185,82,'Bathroom');rm(s,215,8,115,202,'Hallway');
  add(s,'rect',{x:15,y:116,width:185,height:12,fill:'#080d14'});
  door(s,15,116,65,90,true,'#f59e0b');
  tag(s,72,108,'CLOSED','#f59e0b');
  op(s,100,62,'Austin',OP.Austin,13,180);
  bubble(s,115,18,95,30,'"Trailer."',OP.Austin);
  add(s,'line',{x1:115,y1:48,x2:108,y2:55,stroke:OP.Austin,'stroke-width':0.8,opacity:0.5});
  op(s,262,80,'Dylan',OP.Dylan,13,270);
  arr(s,240,92,215,130,OP.Dylan);
  tag(s,262,58,'RESPONDS',OP.Dylan);lbl(s,262,104,'posts on door','#5a7a9a',7.5);
}

// ── Concept data ──────────────────────────────────────────────────────────────
const CONCEPTS=[
  {num:1,title:'Stack Formation',fn:sceneStack,body:'The team forms a tight line outside the entry point in a set order before the command to move. Everyone knows their position before the approach begins.',rule:'Rico is rear command. Chris is on point. Order is set before the approach.'},
  {num:2,title:'Limited Penetration',fn:sceneLimitedPen,body:'The first operator enters just far enough to clear the immediate threat area. You do not blow through the room. You stop, hold your corner, and wait for the stack.',rule:'Enter. Stop. Hold. Deep corner first, then gaze toward center.'},
  {num:3,title:'Button Hook',fn:sceneButtonHook,body:'The second operator follows point through the door and immediately hooks to the opposite side. Chris goes left. Mags hooks right.',rule:'They hold position with enough room for the rest of the stack to enter.'},
  {num:4,title:'Angle Adjustment',fn:sceneAngleAdj,body:'Once the stack is inside, Chris and Mags shift their angles so the team can move up without crossing muzzles.',rule:'Chris angles toward the family room opening. Mags angles toward the hallway opening.'},
  {num:5,title:'Calling Hallway Point',fn:sceneHallwayPoint,callout:'Manny: "Hallway right, Manny on point."',body:'When a hallway is identified, point claims it with a verbal callout. The name is included on the first announcement only.',rule:'Say the name once. Subsequent hallway calls do not repeat it.'},
  {num:6,title:'Closed Door Procedure',fn:sceneClosedDoor,body:'When point encounters a closed door in the hallway, he bumps past it. The operator directly behind him moves with him, sets on the door, and protects his back.',rule:'Point bumps past. The operator behind sets on the door — doorknob side.'},
  {num:7,title:'Open Door Procedure',fn:sceneOpenDoor,body:'An open door is treated differently from a closed one. Point does NOT bump past. He stops short and hugs the wall next to the opening.',rule:'Stop short. Hug the wall. Do not move past an open door.'},
  {num:8,title:'Doorknob Side vs Hinge Side',fn:sceneDoorSides,body:'Every door entry has two positions. The operator on the doorknob side controls the door. The operator on the hinge side enters first.',rule:'Doorknob side opens and deploys the bang. Hinge side enters first.'},
  {num:9,title:'Bang Deployment',fn:sceneBang,body:'Before entry, a distraction device goes in. The operator on the doorknob side opens the door and deploys the bang. Entry follows immediately.',rule:'Open → bang → enter. Do not pause between bang and entry.'},
  {num:10,title:'First In, Last Out',fn:sceneFirstIn,body:'The first operator through the door owns that room. They are responsible for it until told otherwise. They do not leave until the room is detailed.',rule:'First in = last out. You detail the room — you do not just hold it.'},
  {num:11,title:'Trailer',fn:sceneTrailer,callout:'Austin: "Trailer."',body:'The Trailer is a designated operator held in reserve. When a secondary threat area is discovered — like a closed door inside a room — the Trailer is called.',rule:'The Trailer responds to the call and posts on the location. Dylan responds to the bathroom.'},
  {num:12,title:'Radio Callouts',fn:null,body:null,rule:null,traffic:[
    {who:'RICO',color:OP.Rico,text:'"Initiate."',note:'Command to begin. Rico only.'},
    {who:'MANNY',color:OP.Manny,text:'"Hallway right, Manny on point."',note:'First call — name included.'},
    {who:'MANNY',color:OP.Manny,text:'"Closed door right."',note:'Hallway — first door.'},
    {who:'MANNY',color:OP.Manny,text:'"Closed door left."',note:'Hallway — second door.'},
    {who:'MANNY',color:OP.Manny,text:'"Last room, open door left."',note:'Exact wording. Open = stop short.'},
    {who:'AUSTIN',color:OP.Austin,text:'"Trailer."',note:'Calls the designated Trailer.'},
    {who:'RICO',color:OP.Rico,text:'"House is clear."',note:'All rooms detailed. Rico confirms.'},
  ]},
];

// ── Render & Nav ──────────────────────────────────────────────────────────────
let cur=0;
function render(idx){
  const c=CONCEPTS[idx];
  const scSvg=document.getElementById('scene-svg');
  const radio=document.getElementById('radio-traffic');
  const textWrap=document.getElementById('text-wrap');
  document.getElementById('concept-counter').textContent=`${idx+1} / ${CONCEPTS.length}`;
  document.getElementById('concept-num-label').textContent=`CONCEPT ${idx+1}`;
  document.getElementById('concept-title').textContent=c.title;
  const callEl=document.getElementById('concept-callout');
  if(c.callout){callEl.textContent=c.callout;callEl.classList.remove('hidden');}else callEl.classList.add('hidden');
  const bodyEl=document.getElementById('concept-body');
  if(c.body){bodyEl.textContent=c.body;bodyEl.style.display='';}else bodyEl.style.display='none';
  const ruleEl=document.getElementById('concept-rule');
  if(c.rule){ruleEl.textContent=c.rule;ruleEl.classList.remove('hidden');}else ruleEl.classList.add('hidden');
  if(c.traffic){
    scSvg.classList.add('hidden');textWrap.classList.add('hidden');radio.classList.remove('hidden');
    radio.innerHTML='<div class="traffic-header">RADIO TRAFFIC</div>';
    for(const row of c.traffic){const d=document.createElement('div');d.className='traffic-row';d.innerHTML=`<span class="traffic-callsign" style="color:${row.color}">${row.who}</span><span class="traffic-text">${row.text}</span><span class="traffic-note">${row.note}</span>`;radio.appendChild(d);}
  }else{
    radio.classList.add('hidden');textWrap.classList.remove('hidden');scSvg.classList.remove('hidden');
    while(scSvg.firstChild)scSvg.removeChild(scSvg.firstChild);
    if(c.fn)c.fn(scSvg);
  }
  document.querySelectorAll('.dot').forEach((d,i)=>d.classList.toggle('active',i===idx));
  document.getElementById('btn-prev').disabled=idx===0;
  document.getElementById('btn-next').disabled=idx===CONCEPTS.length-1;
}
function goTo(idx){cur=Math.max(0,Math.min(CONCEPTS.length-1,idx));render(cur);}
const dots=document.getElementById('dots');
CONCEPTS.forEach((_,i)=>{const d=document.createElement('div');d.className='dot';d.addEventListener('click',()=>goTo(i));dots.appendChild(d);});
document.getElementById('btn-prev').addEventListener('click',()=>goTo(cur-1));
document.getElementById('btn-next').addEventListener('click',()=>goTo(cur+1));
let tx0=0;
['scene-svg','radio-traffic'].forEach(id=>{
  const el=document.getElementById(id);
  el.addEventListener('touchstart',e=>{tx0=e.touches[0].clientX;},{passive:true});
  el.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx0;if(Math.abs(dx)>44)goTo(cur+(dx<0?1:-1));},{passive:true});
});
goTo(0);

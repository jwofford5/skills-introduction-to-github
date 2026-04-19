'use strict';
// All positions in meters. Scale: 40px/m. Canvas 700×520 → 17.5m × 13m
// Origin (0,0) = top-left of building interior.
// Operators stack from x = -0.5 going left (exterior wall is at x=0).

const OP_COLOR = {
  Rico:'#e74c3c', Chris:'#3498db', Mags:'#2ecc71', Manny:'#f39c12',
  Mike:'#9b59b6', Ian:'#1abc9c', Austin:'#e67e22', Ashley:'#e91e8c',
  Dylan:'#00bcd4', Cassidy:'#cddc39'
};

// ── Floor plan ────────────────────────────────────────────────────────────────
// Room: {id, label, x, y, w, h}  (all meters)
const ROOMS = [
  {id:'living',   label:'Living Room',  x:0,  y:0,  w:7,  h:4.5},
  {id:'family',   label:'Family Room',  x:7,  y:0,  w:6,  h:4.5},
  {id:'hallway',  label:'Hallway',      x:0,  y:4.5,w:13, h:2},
  {id:'kitchen',  label:'Kitchen',      x:7,  y:6.5,w:6,  h:3.5},
  {id:'bathroom', label:'Bathroom',     x:7,  y:10, w:4,  h:2.5},
  {id:'bedroom',  label:'Bedroom',      x:11, y:6.5,w:2,  h:6},
  {id:'lastroom', label:'Last Room',    x:0,  y:6.5,w:7,  h:5.5},
];

// Door: {id, hx, hy, len, closedDeg, cw, state, roomBeyond, normal}
// closedDeg: direction panel points when CLOSED (0=up,90=right,180=down,270=left)
// cw: panel swings clockwise (on screen, y-down) to reach open position
// normal: degrees the muzzle faces TO ENTER the room
const DOORS = [
  {id:'front',    hx:0,   hy:1.5, len:1.2, closedDeg:0,   cw:false, state:'closed', roomBeyond:'living',   normal:90,  clearAt:6},
  {id:'closed-r', hx:8.5, hy:4.5, len:1,   closedDeg:90,  cw:false, state:'closed', roomBeyond:'kitchen',  normal:0,   clearAt:18},
  {id:'closed-l', hx:3,   hy:6.5, len:1,   closedDeg:270, cw:true,  state:'closed', roomBeyond:'lastroom', normal:180, clearAt:22},
  {id:'lastroom', hx:0,   hy:6.5, len:1,   closedDeg:90,  cw:false, state:'open',   roomBeyond:'lastroom', normal:180, clearAt:26},
  {id:'bathroom', hx:7,   hy:10,  len:1,   closedDeg:270, cw:true,  state:'closed', roomBeyond:'bathroom', normal:90,  clearAt:38},
];

// ── Operator helper ────────────────────────────────────────────────────────────
function op(pos, facing, posture, sw, widthDeg, wc, wr) {
  return { pos, facing, posture,
    sectorPrimary:{centerDeg:facing, widthDeg:widthDeg||60},
    wallContact:wc||'none', weaponReady:wr||'on-target' };
}

// ── Keyframes ─────────────────────────────────────────────────────────────────
const KEYFRAMES = [
  // 0: Stack on exterior wall
  { time:0, label:'Stack forms on exterior wall', annotation:null, bang:false,
    ops:{
      Chris:   op({x:-0.5,y:1.5}, 90,'stacked',   null,50,'right-shoulder','low-ready'),
      Mags:    op({x:-1.1,y:1.5}, 90,'stacked',   null,40,'right-shoulder','high-ready'),
      Manny:   op({x:-1.7,y:1.5}, 90,'stacked',   null,40,'right-shoulder','high-ready'),
      Mike:    op({x:-2.3,y:1.5}, 90,'stacked',   null,35,'right-shoulder','muzzle-up'),
      Ian:     op({x:-2.9,y:1.5}, 90,'stacked',   null,35,'right-shoulder','muzzle-up'),
      Austin:  op({x:-3.5,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Ashley:  op({x:-4.1,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Dylan:   op({x:-4.7,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Cassidy: op({x:-5.3,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Rico:    op({x:-5.9,y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 1: Chris pies the door
  { time:3, label:'Chris slices the pie', annotation:null, bang:false,
    ops:{
      Chris:   op({x:-0.15,y:0.8},135,'pieing',  null,45,'left-shoulder','on-target'),
      Mags:    op({x:-1.0, y:1.5}, 90,'stacked', null,40,'right-shoulder','high-ready'),
      Manny:   op({x:-1.6, y:1.5}, 90,'stacked', null,40,'right-shoulder','high-ready'),
      Mike:    op({x:-2.2, y:1.5}, 90,'stacked', null,35,'right-shoulder','muzzle-up'),
      Ian:     op({x:-2.8, y:1.5}, 90,'stacked', null,35,'right-shoulder','muzzle-up'),
      Austin:  op({x:-3.4, y:1.5}, 90,'stacked', null,30,'right-shoulder','muzzle-up'),
      Ashley:  op({x:-4.0, y:1.5}, 90,'stacked', null,30,'right-shoulder','muzzle-up'),
      Dylan:   op({x:-4.6, y:1.5}, 90,'stacked', null,30,'right-shoulder','muzzle-up'),
      Cassidy: op({x:-5.2, y:1.5}, 90,'stacked', null,30,'right-shoulder','muzzle-up'),
      Rico:    op({x:-5.8, y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 2: "Initiate" — door opens, Chris crosses threshold
  { time:6, label:'"Initiate." — front door opens', annotation:{who:'RICO',color:OP_COLOR.Rico,text:'"Initiate."'}, bang:false,
    ops:{
      Chris:   op({x:0.5, y:1.5}, 90,'moving',    null,50,'right-shoulder','on-target'),
      Mags:    op({x:-0.5,y:1.5}, 90,'stacked',   null,40,'right-shoulder','high-ready'),
      Manny:   op({x:-1.1,y:1.5}, 90,'stacked',   null,40,'right-shoulder','high-ready'),
      Mike:    op({x:-1.7,y:1.5}, 90,'stacked',   null,35,'right-shoulder','muzzle-up'),
      Ian:     op({x:-2.3,y:1.5}, 90,'stacked',   null,35,'right-shoulder','muzzle-up'),
      Austin:  op({x:-2.9,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Ashley:  op({x:-3.5,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Dylan:   op({x:-4.1,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Cassidy: op({x:-4.7,y:1.5}, 90,'stacked',   null,30,'right-shoulder','muzzle-up'),
      Rico:    op({x:-5.3,y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 3: Chris LimPen, Mags button-hooks
  { time:9, label:'Chris stops short — Mags button-hooks', annotation:null, bang:false,
    ops:{
      Chris:   op({x:1.2, y:0.9}, 135,'dominating',null,65,'right-shoulder','on-target'),
      Mags:    op({x:1.2, y:2.2}, 225,'dominating',null,65,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:1.5}, 90,'moving',     null,40,'right-shoulder','on-target'),
      Mike:    op({x:-0.5,y:1.5}, 90,'stacked',    null,35,'right-shoulder','high-ready'),
      Ian:     op({x:-1.1,y:1.5}, 90,'stacked',    null,35,'right-shoulder','muzzle-up'),
      Austin:  op({x:-1.7,y:1.5}, 90,'stacked',    null,30,'right-shoulder','muzzle-up'),
      Ashley:  op({x:-2.3,y:1.5}, 90,'stacked',    null,30,'right-shoulder','muzzle-up'),
      Dylan:   op({x:-2.9,y:1.5}, 90,'stacked',    null,30,'right-shoulder','muzzle-up'),
      Cassidy: op({x:-3.5,y:1.5}, 90,'stacked',    null,30,'right-shoulder','muzzle-up'),
      Rico:    op({x:-4.1,y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 4: Angle adjustment — Chris/Mags shift muzzles for stack passage
  { time:12, label:'Angle adjustment — muzzles shift for stack', annotation:null, bang:false,
    ops:{
      Chris:   op({x:1.5, y:0.7},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:1.5, y:2.4}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:2.5, y:1.5}, 90,'moving',     null,40,'right-shoulder','on-target'),
      Mike:    op({x:1.2, y:1.5}, 90,'moving',      null,35,'right-shoulder','high-ready'),
      Ian:     op({x:0.3, y:1.5}, 90,'moving',      null,35,'right-shoulder','muzzle-up'),
      Austin:  op({x:-0.5,y:1.5}, 90,'stacked',     null,30,'right-shoulder','muzzle-up'),
      Ashley:  op({x:-1.1,y:1.5}, 90,'stacked',     null,30,'right-shoulder','muzzle-up'),
      Dylan:   op({x:-1.7,y:1.5}, 90,'stacked',     null,30,'right-shoulder','muzzle-up'),
      Cassidy: op({x:-2.3,y:1.5}, 90,'stacked',     null,30,'right-shoulder','muzzle-up'),
      Rico:    op({x:-2.9,y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 5: Manny calls hallway point — stack flows into hallway
  { time:15, label:'Manny calls hallway point', annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Hallway right, Manny on point."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:4.5, y:5.3}, 90,'moving',     null,40,'none','on-target'),
      Mike:    op({x:3.0, y:5.3}, 90,'moving',      null,35,'none','high-ready'),
      Ian:     op({x:2.0, y:5.3},270,'covering-rear',null,40,'none','on-target'),
      Austin:  op({x:1.2, y:5.3}, 90,'moving',      null,30,'none','muzzle-up'),
      Ashley:  op({x:0.5, y:5.3}, 90,'moving',      null,30,'none','muzzle-up'),
      Dylan:   op({x:-0.2,y:5.3}, 90,'moving',      null,30,'none','muzzle-up'),
      Cassidy: op({x:2.8, y:5.3},  0,'moving',      null,35,'right-shoulder','muzzle-up'),
      Rico:    op({x:0.5, y:1.5},270,'covering-rear',null,40,'right-shoulder','on-target'),
    }
  },

  // 6: Closed door right — Manny bumps past, Cassidy sets
  { time:18, label:'Closed door right — Manny bumps past', annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Closed door right."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:10.0,y:5.3},  90,'moving',    null,40,'none','on-target'),
      Mike:    op({x:8.0, y:5.3},  90,'moving',     null,35,'none','high-ready'),
      Ian:     op({x:5.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
      Austin:  op({x:7.0, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Ashley:  op({x:4.5, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Dylan:   op({x:3.5, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:1.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 7: Closed door left — bump and set
  { time:22, label:'Closed door left — bump and set', annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Closed door left."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:11.5,y:5.3},  90,'moving',    null,40,'none','on-target'),
      Mike:    op({x:10.0,y:5.3},  90,'moving',     null,35,'none','high-ready'),
      Ian:     op({x:7.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
      Austin:  op({x:9.0, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Ashley:  op({x:6.0, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Dylan:   op({x:3.5, y:6.5}, 180,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:2.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 8: Last room — Manny stops short of open door
  { time:26, label:'"Last room, open door left" — stop short', annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Last room, open door left."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:11.0,y:5.3},  90,'moving',     null,35,'none','high-ready'),
      Ian:     op({x:9.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
      Austin:  op({x:5.5, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Ashley:  op({x:6.5, y:5.3},  90,'moving',     null,30,'none','muzzle-up'),
      Dylan:   op({x:3.5, y:6.5}, 180,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:3.5, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 9: Austin calls Trailer
  { time:30, label:'Austin calls "Trailer"', annotation:{who:'AUSTIN',color:OP_COLOR.Austin,text:'"Trailer."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:2.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Ian:     op({x:4.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Austin:  op({x:9.5, y:7.5},  90,'dominating', null,55,'right-shoulder','on-target'),
      Ashley:  op({x:8.0, y:7.5},  90,'dominating', null,55,'left-shoulder','on-target'),
      Dylan:   op({x:3.5, y:6.5}, 180,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:5.0, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 10: Dylan posts on bathroom door
  { time:33, label:'Dylan posts on bathroom door', annotation:null, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:2.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Ian:     op({x:4.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Austin:  op({x:9.5, y:7.5},  90,'dominating', null,55,'right-shoulder','on-target'),
      Ashley:  op({x:8.0, y:7.5},  90,'dominating', null,55,'left-shoulder','on-target'),
      Dylan:   op({x:6.5, y:9.7},   0,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:5.0, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 11: Bang deployed — Austin turns away, Dylan opens
  { time:36, label:'Bang deployed', annotation:{who:'DYLAN',color:OP_COLOR.Dylan,text:'[OPEN + BANG]'}, bang:true,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:2.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Ian:     op({x:4.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Austin:  op({x:9.5, y:9.5}, 270,'moving',     null,30,'none','muzzle-up'),
      Ashley:  op({x:8.0, y:7.5},  90,'dominating', null,55,'left-shoulder','on-target'),
      Dylan:   op({x:6.5, y:9.7}, 180,'moving',     null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:5.0, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 12: Entry into bathroom
  { time:38, label:'Austin enters — Dylan follows', annotation:null, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:2.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Ian:     op({x:4.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Austin:  op({x:8.5, y:11.2}, 90,'dominating', null,60,'right-shoulder','on-target'),
      Ashley:  op({x:8.0, y:7.5},  90,'dominating', null,55,'left-shoulder','on-target'),
      Dylan:   op({x:7.5, y:10.5}, 90,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:5.0, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },

  // 13: House is clear
  { time:42, label:'"House is clear."', annotation:{who:'RICO',color:OP_COLOR.Rico,text:'"House is clear."'}, bang:false,
    ops:{
      Chris:   op({x:2.0, y:0.8},  60,'dominating',null,55,'right-shoulder','on-target'),
      Mags:    op({x:2.0, y:2.3}, 150,'dominating',null,55,'left-shoulder', 'on-target'),
      Manny:   op({x:0.5, y:6.2}, 270,'dominating',null,55,'right-shoulder','on-target'),
      Mike:    op({x:2.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Ian:     op({x:4.5, y:7.5}, 180,'detailing',  null,60,'none','on-target'),
      Austin:  op({x:8.5, y:11.2}, 90,'dominating', null,60,'right-shoulder','on-target'),
      Ashley:  op({x:8.0, y:7.5},  90,'dominating', null,55,'left-shoulder','on-target'),
      Dylan:   op({x:7.5, y:10.5}, 90,'dominating', null,50,'right-shoulder','on-target'),
      Cassidy: op({x:9.0, y:5.3},   0,'dominating', null,50,'right-shoulder','on-target'),
      Rico:    op({x:5.0, y:5.3}, 270,'covering-rear',null,40,'none','on-target'),
    }
  },
];

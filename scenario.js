'use strict';
// All positions in meters. Scale: 30px/m, OFFSET x=210 y=20. Canvas 700×520.
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
// closedDeg: direction panel points when lying in wall gap (closed)
// cw: panel swings CW on screen to reach open position
// normal: muzzle direction to enter the room (0=N,90=E,180=S,270=W)
const DOORS = [
  // Front door: left wall (x=0), hinge at top of gap, panel closes downward, opens east (CCW)
  {id:'front',    hx:0,   hy:1.5, len:1.2, closedDeg:180, cw:false, state:'closed', roomBeyond:'living',   normal:90,  clearAt:6},
  // Closed-right: north wall of hallway (y=4.5), panel closes eastward, opens north (CCW)
  {id:'closed-r', hx:8.5, hy:4.5, len:1,   closedDeg:90,  cw:false, state:'closed', roomBeyond:'kitchen',  normal:0,   clearAt:18},
  // Closed-left: south wall of hallway (y=6.5), panel closes westward, opens south (CCW)
  {id:'closed-l', hx:3,   hy:6.5, len:1,   closedDeg:270, cw:false, state:'closed', roomBeyond:'lastroom', normal:180, clearAt:22},
  // Last room door: south wall end of hallway, panel closes eastward, opens south (CW)
  {id:'lastroom', hx:0,   hy:6.5, len:1,   closedDeg:90,  cw:true,  state:'open',   roomBeyond:'lastroom', normal:180, clearAt:26},
  // Bathroom: north wall of bathroom (y=10), panel closes westward, opens south (CCW)
  {id:'bathroom', hx:7,   hy:10,  len:1,   closedDeg:270, cw:false, state:'closed', roomBeyond:'bathroom', normal:90,  clearAt:38},
];

// ── Keyframes — 3 operators: Chris (#1 point), Mags (#2 hook), Manny (#3 rear/hallway point)
const KEYFRAMES = [
  { time:0, label:'Stack forms on exterior wall', annotation:null, bang:false,
    ops:{
      Chris: op({x:-0.5,y:1.5}, 90,'stacked',      null,50,'right-shoulder','low-ready'),
      Mags:  op({x:-1.1,y:1.5}, 90,'stacked',      null,40,'right-shoulder','high-ready'),
      Manny: op({x:-1.7,y:1.5},270,'covering-rear', null,40,'right-shoulder','on-target'),
    }
  },

  { time:3, label:'Chris slices the pie', annotation:null, bang:false,
    ops:{
      Chris: op({x:-0.15,y:0.8},135,'pieing',       null,45,'left-shoulder','on-target'),
      Mags:  op({x:-0.9, y:1.5}, 90,'stacked',      null,40,'right-shoulder','high-ready'),
      Manny: op({x:-1.5, y:1.5},270,'covering-rear', null,40,'right-shoulder','on-target'),
    }
  },

  { time:6, label:'"Initiate." — front door opens',
    annotation:{who:'RICO',color:OP_COLOR.Rico,text:'"Initiate."'}, bang:false,
    ops:{
      Chris: op({x:0.5, y:1.5}, 90,'moving',        null,50,'right-shoulder','on-target'),
      Mags:  op({x:-0.4,y:1.5}, 90,'stacked',       null,40,'right-shoulder','high-ready'),
      Manny: op({x:-1.0,y:1.5},270,'covering-rear',  null,40,'right-shoulder','on-target'),
    }
  },

  // Chris goes STRAIGHT east (limited penetration), stops and checks north corner.
  // Mags BUTTON HOOKS — curves south along the door jamb, checks south corner.
  { time:9, label:'Chris straight — Mags button-hooks', annotation:null, bang:false,
    ops:{
      Chris: op({x:1.5,y:1.8},   0,'dominating',    null,60,'right-shoulder','on-target'),
      Mags:  op({x:0.8,y:3.6}, 330,'dominating',    null,60,'left-shoulder', 'on-target'),
      Manny: op({x:0.3,y:2.1},  90,'moving',        null,40,'none','on-target'),
    }
  },

  { time:12, label:'Angle adjustment — muzzles shift for Manny', annotation:null, bang:false,
    ops:{
      Chris: op({x:1.5,y:1.5},  45,'dominating',    null,55,'right-shoulder','on-target'),
      Mags:  op({x:1.2,y:3.8}, 315,'dominating',    null,55,'left-shoulder', 'on-target'),
      Manny: op({x:2.5,y:2.2},  90,'moving',        null,40,'none','on-target'),
    }
  },

  { time:15, label:'Manny calls hallway point',
    annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Hallway right, Manny on point."'}, bang:false,
    ops:{
      Chris: op({x:1.5,y:1.5},  45,'dominating',    null,55,'right-shoulder','on-target'),
      Mags:  op({x:1.2,y:3.8}, 315,'dominating',    null,55,'left-shoulder', 'on-target'),
      Manny: op({x:4.5,y:5.3},  90,'moving',        null,40,'none','on-target'),
    }
  },

  { time:18, label:'Closed door right — Manny bumps past, Mags sets',
    annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Closed door right."'}, bang:false,
    ops:{
      Chris: op({x:2.0, y:0.8},  55,'dominating',   null,55,'right-shoulder','on-target'),
      Mags:  op({x:8.8, y:5.3},   0,'dominating',   null,50,'right-shoulder','on-target'),
      Manny: op({x:10.5,y:5.3},  90,'moving',       null,40,'none','on-target'),
    }
  },

  { time:22, label:'Closed door left — Manny bumps past, Chris sets',
    annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Closed door left."'}, bang:false,
    ops:{
      Chris: op({x:3.5,y:6.8}, 180,'dominating',    null,50,'right-shoulder','on-target'),
      Mags:  op({x:8.8,y:5.3},   0,'dominating',    null,50,'right-shoulder','on-target'),
      Manny: op({x:12.0,y:5.3}, 90,'moving',        null,40,'none','on-target'),
    }
  },

  { time:26, label:'"Last room, open door left" — Manny stops short',
    annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'"Last room, open door left."'}, bang:false,
    ops:{
      Chris: op({x:3.5,y:6.8}, 180,'dominating',    null,50,'right-shoulder','on-target'),
      Mags:  op({x:8.8,y:5.3},   0,'dominating',    null,50,'right-shoulder','on-target'),
      Manny: op({x:0.5,y:6.2}, 270,'dominating',    null,55,'right-shoulder','on-target'),
    }
  },

  { time:30, label:'Chris calls "Trailer" — bathroom discovered',
    annotation:{who:'CHRIS',color:OP_COLOR.Chris,text:'"Trailer."'}, bang:false,
    ops:{
      Chris: op({x:8.5,y:7.5},  90,'dominating',    null,55,'right-shoulder','on-target'),
      Mags:  op({x:2.5,y:7.5}, 180,'detailing',     null,60,'none','on-target'),
      Manny: op({x:6.5,y:9.7},   0,'dominating',    null,50,'right-shoulder','on-target'),
    }
  },

  { time:36, label:'Bang deployed',
    annotation:{who:'MANNY',color:OP_COLOR.Manny,text:'[OPEN + BANG]'}, bang:true,
    ops:{
      Chris: op({x:9.5,y:9.5}, 270,'moving',        null,30,'none','muzzle-up'),
      Mags:  op({x:8.5,y:7.5},  90,'dominating',    null,55,'right-shoulder','on-target'),
      Manny: op({x:6.5,y:9.7}, 180,'moving',        null,50,'right-shoulder','on-target'),
    }
  },

  { time:38, label:'Chris enters bathroom — Manny follows', annotation:null, bang:false,
    ops:{
      Chris: op({x:8.5,y:11.2}, 90,'dominating',    null,60,'right-shoulder','on-target'),
      Mags:  op({x:8.5,y:7.5},  90,'dominating',    null,55,'right-shoulder','on-target'),
      Manny: op({x:7.5,y:10.5}, 90,'dominating',    null,50,'right-shoulder','on-target'),
    }
  },

  { time:42, label:'"House is clear."',
    annotation:{who:'RICO',color:OP_COLOR.Rico,text:'"House is clear."'}, bang:false,
    ops:{
      Chris: op({x:8.5,y:11.2}, 90,'dominating',    null,60,'right-shoulder','on-target'),
      Mags:  op({x:8.5,y:7.5},  90,'dominating',    null,55,'right-shoulder','on-target'),
      Manny: op({x:7.5,y:10.5}, 90,'dominating',    null,50,'right-shoulder','on-target'),
    }
  },
];

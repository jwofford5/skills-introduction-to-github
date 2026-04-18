'use strict';

const OPERATORS = {
  Rico:    { color:'#e74c3c', role:'Team Leader'              },
  Chris:   { color:'#3498db', role:'Point — Left Entry'       },
  Mags:    { color:'#2ecc71', role:'Point — Button Hook'      },
  Manny:   { color:'#f39c12', role:'Hallway Point'            },
  Mike:    { color:'#9b59b6', role:'Family Room'              },
  Ian:     { color:'#1abc9c', role:'Family Room Support'      },
  Austin:  { color:'#e67e22', role:'Kitchen / Last Room'      },
  Ashley:  { color:'#e91e8c', role:'Kitchen Lead'             },
  Dylan:   { color:'#00bcd4', role:'Trailer / Bathroom'       },
  Cassidy: { color:'#cddc39', role:'Hallway Support / Room 1' },
};

// Positions: [x, y] in SVG units (400×580). Negative x = staged outside.
const ALL_OUT = {Rico:[-50,95],Chris:[-45,80],Mags:[-45,108],Manny:[-45,128],Mike:[-45,148],Ian:[-45,168],Austin:[-45,188],Ashley:[-45,208],Dylan:[-45,228],Cassidy:[-45,248]};

const STEPS = [
  {
    title:'Stack at front door', callout:'', phase:'STAGING', event:null, angles:[],
    teaching:'Full team staged outside the front door. Chris is on point, Mags is second. Rico is rear command.',
    pos: ALL_OUT,
  },
  {
    title:'Rico: Initiate', callout:'Rico: "Initiate."', phase:'STAGING', event:null, angles:[],
    teaching:'The command to initiate belongs to Rico alone. No one moves before this word.',
    pos: ALL_OUT,
  },
  {
    title:'Explosive breach', callout:'— BREACH —', phase:'STAGING', event:'breach', angles:[],
    teaching:'Explosive breach opens the front door. The stack is ready to flow.',
    pos: ALL_OUT,
  },
  {
    title:'Chris enters — limited penetration', callout:'', phase:'ENTRY', event:'entry', angles:[{op:'Chris',x:34,y:75,deg:45,spread:30}],
    teaching:'Chris enters from the left side of the door with limited penetration. He checks the deep corner first, then brings his gaze toward center.',
    pos:{...ALL_OUT, Chris:[34,75]},
  },
  {
    title:'Mags enters — button hook', callout:'', phase:'ENTRY', event:'entry', angles:[{op:'Chris',x:36,y:68,deg:45,spread:30},{op:'Mags',x:36,y:148,deg:135,spread:30}],
    teaching:'Mags follows and button hooks to the right. They hold position with enough room for the rest of the stack to enter.',
    pos:{...ALL_OUT, Chris:[36,68], Mags:[36,148]},
  },
  {
    title:'Stack flows in', callout:'', phase:'ENTRY', event:null, angles:[{op:'Chris',x:42,y:65,deg:45,spread:30},{op:'Mags',x:42,y:155,deg:135,spread:30}],
    teaching:'Manny, Mike, Ian, Austin, Ashley, Dylan, and Cassidy flow through the door. Rico enters last.',
    pos:{Rico:[22,107],Chris:[42,65],Mags:[42,155],Manny:[72,107],Mike:[92,107],Ian:[110,107],Austin:[122,107],Ashley:[122,127],Dylan:[118,148],Cassidy:[112,162]},
  },
  {
    title:'Chris and Mags shift angles', callout:'', phase:'ENTRY', event:null, angles:[{op:'Chris',x:52,y:60,deg:20,spread:30},{op:'Mags',x:52,y:162,deg:160,spread:30}],
    teaching:'Chris shifts forward and angles toward the family room opening. Mags shifts forward and angles toward the hallway opening, ensuring safe passage for Manny and Mike.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,107],Mike:[96,107],Ian:[112,107],Austin:[122,107],Ashley:[120,125],Dylan:[115,145],Cassidy:[110,160]},
  },
  {
    title:'Manny calls hallway point', callout:'Manny: "Hallway right, Manny on point."', phase:'FAMILY_ROOM', event:null, angles:[{op:'Manny',x:80,y:228,deg:90,spread:20}],
    teaching:'Manny identifies the hallway and claims point. Name included on first announcement — subsequent hallway calls do not repeat it.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,228],Mike:[100,107],Ian:[115,107],Austin:[122,107],Ashley:[120,125],Dylan:[115,145],Cassidy:[65,238]},
  },
  {
    title:'Mike posts on family room', callout:'', phase:'FAMILY_ROOM', event:null, angles:[{op:'Mike',x:148,y:100,deg:0,spread:25}],
    teaching:'Mike moves up and posts on the family room entry, covering the opening. Ian follows and takes position behind Mike.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,232],Mike:[148,100],Ian:[130,107],Austin:[120,107],Ashley:[118,125],Dylan:[112,145],Cassidy:[65,242]},
  },
  {
    title:'Ian deploys bang — family room', callout:'— BANG — Family Room', phase:'FAMILY_ROOM', event:'bang', angles:[{op:'Mike',x:152,y:95,deg:0,spread:25}],
    teaching:'Ian throws the distraction device into the family room before entry.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,235],Mike:[152,95],Ian:[148,112],Austin:[118,107],Ashley:[115,125],Dylan:[110,145],Cassidy:[65,245]},
  },
  {
    title:'Mike and Ian detail family room', callout:'', phase:'FAMILY_ROOM', event:'entry', angles:[{op:'Mike',x:222,y:75,deg:315,spread:30},{op:'Ian',x:315,y:155,deg:225,spread:30}],
    teaching:'Mike enters first. Ian follows. First in, last out — they are responsible for this room. Mike clears deep left; Ian clears deep right.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[115,107],Ashley:[112,125],Dylan:[108,145],Cassidy:[65,248]},
  },
  {
    title:'Austin and Ashley move to kitchen', callout:'', phase:'KITCHEN', event:null, angles:[],
    teaching:'Austin and Ashley break from the stack and move toward the kitchen entry in the hallway.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[218,238],Ashley:[240,238],Dylan:[108,145],Cassidy:[65,248]},
  },
  {
    title:'Austin deploys bang — kitchen', callout:'— BANG — Kitchen', phase:'KITCHEN', event:'bang', angles:[],
    teaching:'Austin deploys the distraction device into the kitchen before Ashley enters.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[208,276],Ashley:[232,274],Dylan:[108,145],Cassidy:[65,248]},
  },
  {
    title:'Ashley enters kitchen first', callout:'', phase:'KITCHEN', event:'entry', angles:[{op:'Ashley',x:318,y:312,deg:315,spread:30},{op:'Austin',x:198,y:372,deg:225,spread:30}],
    teaching:'Ashley enters first, clearing the deep right corner. Austin follows and begins clearing the left corner. First in, last out.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[198,372],Ashley:[318,312],Dylan:[108,145],Cassidy:[65,248]},
  },
  {
    title:'Austin calls Trailer', callout:'Austin: "Trailer."', phase:'KITCHEN', event:null, angles:[],
    teaching:'Austin notices the closed bathroom door and calls for the Trailer. Dylan is designated Trailer and responds.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[182,428],Ashley:[318,312],Dylan:[108,145],Cassidy:[65,248]},
  },
  {
    title:'Dylan moves to bathroom door', callout:'', phase:'BATHROOM', event:null, angles:[],
    teaching:'Dylan (Trailer) moves up through the hallway and posts on the bathroom door — doorknob side. Austin shifts to hinge side.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[172,462],Ashley:[318,312],Dylan:[272,452],Cassidy:[65,248]},
  },
  {
    title:'Dylan opens and deploys bang — bathroom', callout:'— BANG — Bathroom', phase:'BATHROOM', event:'bang', angles:[],
    teaching:'The bathroom door opens inward. Dylan is on the doorknob side — he opens the door and throws the bang. Austin enters first.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[172,462],Ashley:[318,312],Dylan:[272,452],Cassidy:[65,248]},
  },
  {
    title:'Austin and Dylan detail bathroom', callout:'', phase:'BATHROOM', event:'entry', angles:[{op:'Austin',x:198,y:505,deg:225,spread:30},{op:'Dylan',x:328,y:508,deg:315,spread:30}],
    teaching:'Austin enters first. Dylan follows. They detail the bathroom. First in, last out.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[80,238],Mike:[222,75],Ian:[315,155],Austin:[198,505],Ashley:[318,312],Dylan:[328,508],Cassidy:[65,248]},
  },
  {
    title:'Manny calls — Closed door right', callout:'Manny: "Closed door right."', phase:'ROOM1', event:null, angles:[{op:'Manny',x:76,y:270,deg:90,spread:20}],
    teaching:'Manny bumps past the first closed door on the right. Cassidy moves with him — she sets on the door, doorknob side. Point protects point.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,270],Mike:[222,75],Ian:[315,155],Austin:[198,505],Ashley:[318,312],Dylan:[328,508],Cassidy:[94,268]},
  },
  {
    title:'Cassidy opens — bang — Room 1', callout:'— BANG — Room 1', phase:'ROOM1', event:'bang', angles:[],
    teaching:'Cassidy is doorknob side. Ashley is hinge side. Cassidy opens the door and deploys the bang.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,290],Mike:[222,75],Ian:[315,155],Austin:[198,505],Ashley:[20,279],Dylan:[328,508],Cassidy:[132,278]},
  },
  {
    title:'Ashley and Cassidy detail Room 1', callout:'', phase:'ROOM1', event:'entry', angles:[{op:'Ashley',x:32,y:318,deg:270,spread:30},{op:'Cassidy',x:112,y:345,deg:315,spread:30}],
    teaching:'Ashley enters first. Cassidy follows. They detail Room 1. First in, last out.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,292],Mike:[222,75],Ian:[315,155],Austin:[198,505],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Manny calls — Closed door left', callout:'Manny: "Closed door left."', phase:'ROOM2', event:null, angles:[{op:'Manny',x:76,y:374,deg:90,spread:20}],
    teaching:'Manny bumps past the second closed door on the left. Mike moves with him on doorknob side. Ian sets on hinge side.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,374],Mike:[98,370],Ian:[22,382],Austin:[198,505],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Mike opens — bang — Room 2', callout:'— BANG — Room 2', phase:'ROOM2', event:'bang', angles:[],
    teaching:'Mike is doorknob side. Ian is hinge side. Mike opens the door and deploys the bang.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,376],Mike:[98,370],Ian:[22,382],Austin:[198,505],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Ian and Mike detail Room 2', callout:'', phase:'ROOM2', event:'entry', angles:[{op:'Ian',x:32,y:420,deg:270,spread:30},{op:'Mike',x:112,y:442,deg:315,spread:30}],
    teaching:'Ian enters first. Mike follows. They detail Room 2.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[76,378],Mike:[112,442],Ian:[32,420],Austin:[198,505],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Manny calls — Last room, open door left', callout:'Manny: "Last room, open door left."', phase:'LAST_ROOM', event:null, angles:[{op:'Manny',x:40,y:480,deg:90,spread:20}],
    teaching:'Open door — Manny does NOT bump past. He stops short and hugs the wall. Point stops short of open doors.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[40,480],Mike:[112,442],Ian:[32,420],Austin:[68,480],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Austin deploys bang — last room', callout:'— BANG — Last Room', phase:'LAST_ROOM', event:'bang', angles:[],
    teaching:'Austin throws the distraction device into the last room. Manny is positioned to go straight on entry.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[40,482],Mike:[112,442],Ian:[32,420],Austin:[76,488],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'Manny goes straight — Austin button hooks', callout:'', phase:'LAST_ROOM', event:'entry', angles:[{op:'Manny',x:35,y:522,deg:225,spread:30},{op:'Austin',x:118,y:525,deg:315,spread:30}],
    teaching:'Manny goes straight into the room. Austin button hooks to the opposite corner. They detail the final room.',
    pos:{Rico:[22,107],Chris:[52,60],Mags:[52,162],Manny:[35,522],Mike:[112,442],Ian:[32,420],Austin:[118,525],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
  {
    title:'House is clear', callout:'Rico: "House is clear."', phase:'ALL_CLEAR', event:null, angles:[],
    teaching:'All rooms detailed. Rico radios the all-clear. Every operator remains responsible for the room they cleared.',
    pos:{Rico:[76,107],Chris:[52,60],Mags:[52,162],Manny:[35,522],Mike:[112,442],Ian:[32,420],Austin:[118,525],Ashley:[32,318],Dylan:[328,508],Cassidy:[112,345]},
  },
];

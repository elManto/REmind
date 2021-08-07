var myHistory;
var destination;
var eip;
var currentEipElement;
var exEipElement;
window.focused_bb = null;
window.selected_reg = "x_x_x";
var bbCache;
var json_cfg;
var cfg = {};
var cfg_edges = {}
var g;
var render;
var svg;
var zoom;
var previousBBid = 0;
var spanIds = [];
var listOfVars = [];
var relocate = 0;

var xref;

var json_callgrpah;
var callgraph = {};
var call_g;
var call_render;
var call_svg;
var call_zoom;

var startTime;
var base_url = 'http://reverse.s3.eurecom.fr:5000'
//var base_url = 'http://193.55.114.25:5000';
//var base_url = 'http://0.0.0.0:5000';		
//var base_url = 'http://10.12.32.194:5000';
var renameVariablesData = {};

var listOfRenamedFunctions = [];
var listOfRenamedVariables = [];

var scrollEventsEnum = {
    FOLLOW : 1,
    JUMPTO: 2,
    CLICK: 3,
    ESC: 4,
    STR_XREF: 5,
    properties: {
        1 : {name: 'follow', value: 1},
        2 : {name: 'jumpto', value: 2},
        3 : {name: 'click', value: 3},
        4 : {name: 'esc', value: 4},
        5 : {name: 'str_xref', value: 5}
    }
}

current_chall = '';

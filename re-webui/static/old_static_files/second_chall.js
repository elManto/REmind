json0 = {"bb0_bbs": {"0x400cb4": "add ebx, 0x10\nmov eax, dword [esp]\nsub ebx, 0x10\nadd eax, 0xf\nmov ebx, dword [esp]\ntest ebx, ebx\njne 0x00804098"}}
json1 = {"bb1_bbs": {"0x400cb4": "push ebp\nmov ebp, esp\nsub esp, 0x18\nand esp, 0xfffffff0\nmov eax, 0\nadd eax, 0xf\n"}}
json2 = {"bb2_bbs": {"0x400cb4": "mov dword [esp + 0xc], eax\nmov edx, dword [local_c4h]\nmov dword [esp + 0x8], edx\nmov ecx, dword [local_c0h]\nmov dword [esp], 0x008053a7\nmov dword [esp + 0x4], ecx\ncall 0x08050c10"}}
json3 = {"bb3_bbs": {"0x400cb4": "add esp, 0x10\nsub esp, 0x4\nmov dword [local_34h], eax\nxor ebx, ebx\ncmp dword [local_34h], ebx\njne 0x00800982\n"}}
json4 = {"bb4_bbs": {"0x400cb4": "push ebp\nxor esp, esp\nadd esp, 0x20\npop esp\nxor eax, eax\nadd eax, 0xf\n"}}

json_dict = {'bb0':json0, 'bb1':json1, 'bb2':json2, 'bb3':json3, 'bb4':json4}
index = 0




function CFGbuilder(json_cfg, func_name) {

        Object.keys(json_cfg[func_name + "_bbs"]).forEach(function(state) {
                tmp = {}
                tmp["asm"] = json_cfg[func_name + "_bbs"][state]
                tmp["obfuscated"] = "------- ----\n"
                cfg[state] = tmp
         });
        // Create a new directed graph
        g = new dagreD3.graphlib.Graph().setGraph({});
        // Add states to the graph, set labels, and style
        Object.keys(cfg).forEach(function(state) {

        var value = cfg[state];

        value.labelType="html";
        //value.label = "<pre><code id='"+state+"' class='language-nasm' >"+value.asm+"</code></pre>";
        // onmouseenter=\"selected(this);\"
        value.label = "<pre><code id='"+state+"'  class='language-nasm' >"+value.asm+"</code></pre>";
        value.rx = value.ry = 5;
        value.id = state;
        // blurred effect is set by default
        g.setNode(state, value);
        });

        /*var edges = json_cfg[func_name + "_edges"]["edges"]
        cfg_edges = edges;
        for (var i = 0; i < edges.length; i++) {
                g.setEdge(edges[i][0], edges[i][1], {label: ""});

        }*/
        render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        svg = d3.select("svg"),
            inner = svg.append("g");

        // Set up zoom support
        /*zoom = d3.zoom()
            .on("zoom", function() {
              inner.attr("transform", d3.event.transform);
            });
        svg.call(zoom);*/

        // Run the renderer. This is what draws the final graph.
        render(inner, g);

        // Center the graph
        var initialScale = 1;

        svg.attr('width', 1200);
        svg.attr('height', 512);

        //d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(0.5) );
        //d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(0.5) );
        myPrism(-1);
}


function unobfuscate() {
    $('span').css('filter', '')
}


function reobfuscate() {
    $('span').css('filter', 'blur(8px)')
}

function removeGraph() {
    var svg = d3.select("svg > g");
    svg.selectAll("*").remove();
    $('g')[0].remove()
}

function foo() {
    if (index != 0) {
        removeGraph()
    }
    if (index == 5) {
        window.location.href = "http://10.9.19.81:5000/second_chall/questions";
    }

    k = "bb" + index
    json = json_dict[k]
    CFGbuilder(json, k)
    $('rect').css('width', 400)
    $('rect').css('height', 380)
    index++


}

function start_test() {
    for(i = 0; i < 6; i++) {
        setTimeout(foo, 2500*(i+1))
    }

}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    await sleep(1000);

}


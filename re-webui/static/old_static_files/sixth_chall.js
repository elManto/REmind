started = 0;
writingTime = 0;

function downloadCFG(func) {

        $.post(base_url + "/sixth_chall/getBlock", data={'name':func, 'token':id}, function(data) {

                json_cfg = JSON.parse(data);
                CFGbuilder(json_cfg, func)

        });
        return json_cfg
}



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
        zoom = d3.zoom()
            .on("zoom", function() {
              inner.attr("transform", d3.event.transform);
            });
        svg.call(zoom);

        // Run the renderer. This is what draws the final graph.
        render(inner, g);

        // Center the graph
        var initialScale = 1;

        svg.attr('width', 2000);
        svg.attr('height', 1024);

        d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(1.2) );
        d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(1.2) );
        myPrism(-1);

}


function unobfuscate() {
    $('span').css('filter', '')
}


function reobfuscate() {
    $('span').css('filter', 'blur(8px)')
}

function start_test() {
    unobfuscate()
    startTime = new Date();
    started = 1;
    $('button')[0].style.display = "none"
    $('.mainw').on('click', function() {
        $('pre')[0].style.display = "none"
        setTimeout(send_submission, 1000)
    })
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    await sleep(1000);
}

function send_submission() {
    demo();
    if(started == 0) {
        alert("Click the Start button to begin")
        $('pre')[0].style.display = ""
    }
    else {

        endTime = new Date();
        console.log("writing time 1 " + writingTime)
        elapsedTime = endTime - startTime - writingTime;
        startWritingTime = new Date();

        val = prompt("Write here your solution:")
        $('pre')[0].style.display = ""
        elapsedTime = endTime - startTime;
        var note = val + ";" + elapsedTime;
        $.post(base_url + "/sixth_chall/storeSolution", data={'token':id, 'notes':note}, function(received) {

            if(received == "1") {
                window.location.href = base_url + '/congrats';
            }
            else {
                alert("Error in your submitted solution!");
                endWritingTime = new Date();
                writingTime = endWritingTime - startWritingTime
                console.log("writing time 2 " + writingTime)
            }
        })

    }

}


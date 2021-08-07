function isComment(addr) {

    return ($('span#' + addr + '.token.generic:contains("#")').length > 0)
}


function removeGraph() {
    var svg = d3.select("svg > g");
    svg.selectAll("*").remove();
    $('g')[0].remove()
}

function get_xrefs_from(func) {
    $.post(base_url + "/fourth_chall/get_xrefs_from", data={'name':func, 'token':id}, function(data) {
                xref = JSON.parse(data);

                 if(!Object.keys(xref).length /*|| $('#x_from').length == 1*/)
                    return
                 var msg = "<ul id='x_from' style='list-style:none;font-size:16px'>Xrefs from:"
                 for(var i in xref)
			msg += "<li>" + "<a href=./?function=" + i +" onclick='push_function_history(&quot;" + func_to_download + "&quot;, null)'>" + xref[i] + "</a>" + "</li>"
                 msg += "</ul>"
                 $('a#' + func).after(msg);
        });
}


function get_xrefs_to(func) {
    $.post(base_url + "/fourth_chall/get_xrefs_to", data={'name':func, 'token':id}, function(data) {
                xref = JSON.parse(data);

                if(!Object.keys(xref).length /*|| $('#x_to').length == 1*/)
                    return
                var msg = "<ul id='x_to' style='list-style:none;font-size:16px'>Xrefs to:"
                 for(var i in xref) {
			msg += "<li>" + "<a href=./?function=" + i + " onclick='push_function_history(&quot;" + func_to_download + "&quot;, null)'>"  + xref[i] + "</a>" + "</li>"
		 }
                 msg += "</ul>"
                 $('a#' + func).after(msg);
        });
}

/*
function graphRender(codeId) {
     g = new dagreD3.graphlib.Graph().setGraph({});
     Object.keys(cfg).forEach(function(state) {

        var value = cfg[state];

        value.labelType="html";
        //value.label = "<pre><code id='"+state+"' class='language-nasm' >"+value.asm+"</code></pre>";
        // onmouseenter=\"selected(this);\"
        value.label = "<pre><code id='"+state+"' class='language-nasm' >"+value.asm+"</code></pre>";
        value.rx = value.ry = 5;
        // blurred effect is set by default
        g.setNode(state, value);
        });


        for (var i = 0; i < cfg_edges.length; i++) {
                g.setEdge(cfg_edges[i][0], cfg_edges[i][1], {label: ""});
        }
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
        var initialScale = 1.2;

        svg.attr('width', 1600);
        svg.attr('height', 1024);
        restore(codeId);
        myPrism(codeId);
}
*/


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

        var edges = json_cfg[func_name + "_edges"]["edges"]
        cfg_edges = edges;
        for (var i = 0; i < edges.length; i++) {
                g.setEdge(edges[i][0], edges[i][1], {label: ""});

        }
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

        d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(0.5) );
        d3.select('svg').transition().duration(200).call( zoom.transform, d3.zoomIdentity.translate(-1*1+400,-1*40+200).scale(0.5) );
        myPrism(-1);



        downloadData();
}


function buildCallgraph() {
        for(var i in json_callgraph['nodes']) {
            var addr = json_callgraph['nodes'][i][0]
            var lab = json_callgraph['nodes'][i][1]

            var obj = new Object()
            obj['label'] = lab
            callgraph[addr] = obj

        }
        // Create a new directed graph
        call_g = new dagreD3.graphlib.Graph().setGraph({});
        // Add states to the graph, set labels, and style
        Object.keys(callgraph).forEach(function(state) {

            var value = callgraph[state];

            value.rx = value.ry = 5;

            call_g.setNode(state, value);

        });

        for (var i = 0; i < json_callgraph['edges'].length; i++) {
                call_g.setEdge(json_callgraph['edges'][i][0], json_callgraph['edges'][i][1], {label: ""});

        }
        call_render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        call_svg = d3.select("svg"),
            inner = call_svg.append("g");

        // Set up zoom support
        call_zoom = d3.zoom()
            .on("zoom", function() {
              inner.attr("transform", d3.event.transform);
            });
        call_svg.call(call_zoom);

        // Run the renderer. This is what draws the final graph.
        call_render(inner, call_g);

        // Center the graph
        var initialScale = 1.2;

        call_svg.attr('width', 1600);
        call_svg.attr('height', 1024);
        //myPrism(-1);
}

function downloadCallGraph() {
    $.post(base_url + "/fourth_chall/getCallGraph", data={'name':'callgraph'}, function(data) {

         json_callgraph = JSON.parse(data);
         buildCallgraph();

    });
    return 0;
}




function downloadCFG(func) {

        $.post(base_url + "/fourth_chall/getCFG", data={'name':func, 'token':id}, function(data) {

                json_cfg = JSON.parse(data);
                CFGbuilder(json_cfg, func)

        });
        return json_cfg
}




function send_results(data) {
    data["fcn_name"] = func_to_download;
    $.get( base_url + "/fourth_chall/getmethod/" + id + ";" + JSON.stringify(data));

}


function getBBbyAddress(addr) {

    var bb
    Object.keys(cfg).forEach(function(state) {
        var res = $("code#" + state + " span.token.address:contains(" + addr  + ")")
        if(res.length > 0) {
            bb = state;
        }
    });
    return bb;
}


function cfg_getBBbyAddress(addr) {
    var bb;
    Object.keys(cfg).forEach(function(state) {
        if(cfg[state]["asm"].indexOf(addr + ":") >= 0) {
            bb = state;
        }
    });
    return bb
}


function cfg_getBBbyString(s) {
    var bb = [];
    Object.keys(cfg).forEach(function(state) {
        if(cfg[state]["asm"].indexOf(s) >= 0)
            bb.push(state);
    });
    return bb;
}



/*
function scrollToAddress() can be invoked by:
	1)"Follow this" from right-click menu
	2)"Jump to" from right click menu
	3) single click over an available address
	4) "ESC" key press
	5) Coming from string xrefs
*/
function scrollToAddress(addr, enumType) {
    var timeStamp = new Date().getTime();
    var tmpDict = {
        'timestamp' : timeStamp,
        'event' : scrollEventsEnum.properties[enumType].name,
        'element' : addr,
    };
    send_results(tmpDict);
    var bb = getBBbyAddress(addr)
    destination = bb
    rect = g._nodes[bb].elem.firstChild;
    /*rect.style["strokeWidth"]="12.5px";
    rect.style["stroke"]="#b33";*/
    x = g._nodes[bb].x;
    y = g._nodes[bb].y;
    z = d3.zoomTransform(d3.select("svg").node()).k
    d3.select('svg').transition().duration(400).call( zoom.transform, d3.zoomIdentity.translate(-1*x+500,-1*y+200).scale(1) );

}

/*
function obfuscate(id) {
    localStorage.setItem("addr", id)
    $("code#" + id + " span.token.generic").css("filter", "");
    $('.token.generic').css("background", "");
    for(var index in spanIds) {
        $('span#' + spanIds[index] + '.token.generic').css('filter', 'blur(8px)')
    }
    spanIds = [];
    if(previousBBid != 0 && previousBBid != id) {
        $("code#" + previousBBid +" span.token.generic").css("filter", "blur(8px)");
    }
    previousBBid = id;


}
*/


function selected(elem){
    if (elem && bbCache != elem.id) {
        bbCache = elem.id;
        var timeStamp = new Date().getTime();
        var tmpDict = {
            'timestamp' : timeStamp,
            'event' : 'mouseover',
            'element' : elem.id
        };

        send_results(tmpDict);
        obfuscate(elem.id);
    }
    /*else {
        bbCache = elem.id
    }*/

};


function isValidAddress(addr) {
    var r = /0x[A-Za-z0-9]+/;
    return (addr.length > 5 && addr.match(r) && addr.match(r)[0] == addr)

}

/*
function rename(htmlElementToRename) {
    var inner = htmlElementToRename.innerHTML;
    var r = prompt("insert the new name (max 8 chars)");
    if (listOfRenamedVariables.indexOf(r) >= 0) {
	alert('You already have a variable with this name')
	return
    }
    listOfRenamedVariables.push(r)
    if(r == "" || r == null)	return;
    if(r.length > 8) {
        r = r.substring(0, 8)
    }

    var timeStamp = new Date().getTime();
    var tmpDict = {
        'timestamp' : timeStamp,
        'event' : 'rename',
        'element' : htmlElementToRename.id,
        'value' : r
    };
    send_results(tmpDict);
    var isBBchanged = false;

    Object.keys(cfg).forEach(function(state) {
        isBBchanged = false;
        $("code#" + state + " a > span.token.local").each(function() {

            if($(this)[0].textContent == inner) {
                if(state == bbCache)
                    $(this)[0].innerHTML = "<span class='token generic'>" + r + "</span>";
                else
                    $(this)[0].innerHTML = "<span class='token generic' style='filter:blur(8px)'>" + r + "</span>";
                isBBchanged = true;
            }

        });
        if (isBBchanged) {
            new_asm = $("code#" + state + '.language-nasm')[0].textContent;
            cfg[state]["asm"] = new_asm;

            new_label = cfg[state]["label"].substring(0, cfg[state]["label"].indexOf(state)) + new_asm + "</code></pre>"
            cfg[state]["label"] = new_label;
        }
    });

}
*/



function follow(addr, ex_addr, enumType) {
    myHistory = ex_addr
    if (isValidAddress(addr))
        scrollToAddress(addr, enumType)
    else
        alert("You cannot follow it")

}


function cfg_comment(codeId, tokenAddress) {
    var r = prompt("insert comment");
    if(r == "" || r == null)	return;
    if(r.length > 38) {
        r = r.substring(0, 38)
    }
    var timeStamp = new Date().getTime();
    var tmpDict = {
        'timestamp' : timeStamp,
        'event' : 'comment',
        'element' : tokenAddress.childNodes[0].id,
        'value' : r
    };
    send_results(tmpDict);
    var addr = tokenAddress.innerText.substring(0, tokenAddress.innerText.length - 1)

    var new_asm = cfg[codeId]["asm"].substring(0, cfg[codeId]["asm"].indexOf(addr)) + "# " + r + "\n" + cfg[codeId]["asm"].substring(cfg[codeId]["asm"].indexOf(addr))
    cfg[codeId]["asm"] = new_asm

    var new_label = cfg[codeId]["label"].substring(0, cfg[codeId]["label"].indexOf(addr)) + "# " + r + "\n" + cfg[codeId]["label"].substring(cfg[codeId]["label"].indexOf(addr))
    cfg[codeId]["label"] = new_label

    removeGraph();

    graphRender(codeId);


}

function rename_func(addr_id) {
    var value = prompt("Insert a new function name")
    if (value == "" || value == null)
	return;
    if (listOfRenamedFunctions.indexOf(value) >= 0) {
	alert("You already have a function with this name")
	return
    }
    listOfRenamedFunctions.push(value)
    $('span#' + addr_id + '.token.generic').each(function() {
        var f = $(this)[0].innerHTML.split(" ");

        for(var i in f) {
            if(typeof(f[i]) == 'string' && isValidAddress(f[i])) {
                // THIS is for replace the name in instructions like "call sub_43243"
                var func_addr = $(this)[0].innerText;
                // $(this)[0].innerText = value;
                var timeStamp = new Date().getTime();
                var tmpDict = {
                    'timestamp' : timeStamp,
                    'event' : 'func_rename',
                    'element' : func_addr,
                    'value' : value
                };
                send_results(tmpDict);



                $('span.token.number:contains(' + func_addr + ')').each(function() {

                    $(this)[0].innerText = value;
                    var id_to_search = $(this).parent()[0].id

                    var new_asm = cfg[id_to_search]["asm"].replace(func_addr, value);
                    cfg[id_to_search]["asm"] = new_asm



                    var new_label = cfg[id_to_search]["label"].replace(func_addr, value);
                    cfg[id_to_search]["label"] = new_label
                })

                return;
            }
        }
        var codeId = cfg_getBBbyAddress(addr_id);
        for(var i in f) {
            // THIS is for replace the name in instructions like "call 0x1234" (call address, not directly a function name)
            if(all_the_functions.includes(f[i].replace("\n", ""))) {
                var func = f[i];
                var new_asm = cfg[codeId]["asm"].replace(func, value);
                cfg[codeId]["asm"] = new_asm

                var new_label = cfg[codeId]["label"].replace(func, value);
                cfg[codeId]["label"] = new_label

                $('a#' + func)[0].innerText = value;
                var timeStamp = new Date().getTime();
                var tmpDict = {
                    'timestamp' : timeStamp,
                    'event' : 'func_rename',
                    'element' : func.replace("\n", ""),
                    'value' : value
                };
                send_results(tmpDict);

                $(this)[0].innerText = " call " + value

            }
        }
    });
}

function rename_sidenav_func(element) {
    var value = prompt("Insert a new function name");
    if (value == "" || value == null)
	return;
    if (listOfRenamedFunctions.indexOf(value) >= 0) {
	alert("You already have a function with this name")
	return
    }
    listOfRenamedFunctions.push(value)
    var func = $('a#' + element.id)[0].innerText;
    $('a#' + func)[0].innerText = value;
    var timeStamp = new Date().getTime();
    var tmpDict = {
        'timestamp' : timeStamp,
        'event' : 'func_rename',
        'element' : func.replace("\n", ""),
        'value' : value
        };
    send_results(tmpDict);
}


function comment(codeId, tokenAddress) {
    var r = prompt("insert comment");
    if(r == "" || r == null)	return;
    if(r.length > 38) {
        r = r.substring(0, 38)
    }
    var timeStamp = new Date().getTime();
    var tmpDict = {
        'timestamp' : timeStamp,
        'event' : 'comment',
        'element' : tokenAddress.childNodes[0].id,
        'value' : r
    };
    send_results(tmpDict);
    $("code#" + codeId + " > span.token.address").each(function() {
        var addr = $(this)[0].innerText
        if (addr == tokenAddress.innerText) {
            // var html = tokenAddress
            var comment = "<span class='token generic'><span class='comment'># " + r + "</span></span><br>"
            $(this).before(comment)
            // oldSize = parseFloat($("code#" + codeId).css("font-size"), 10)
            // $("code#" + codeId).css("font-size", (oldSize - 3.2) + "px")
            // var oldLineHeight = parseFloat($("pre#" + codeId).css("line-height"), 10)
            // $("pre#" + codeId).css("line-height", (oldLineHeight - 2.34) + "px")

        }

    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    await sleep(1000);
    restore_graph_rename(myData);

}

async function restore(codeId) {
    await sleep(1000);
    restore_graph_rename_after_rendering(codeId);
}

var myData;
function downloadData() {
	var downloadedData;	
	$.get(base_url + "/fourth_chall/getevents/?id=" + id + "&&fcn_name=" + func_to_download,  function(data) {
	    myData = data;
		restore_graph_comments(data);
        demo();

	});
}

// It restores both comments and function rename
function restore_graph_comments(data) {
    //downloadedData = downloadData();
    downloadedData = JSON.parse(data);
    for(var i in downloadedData) {
        var addr = downloadedData[i]['element'];
        var value = downloadedData[i]['value'];
        if(downloadedData[i]['event'] == 'comment') {
            var codeId = cfg_getBBbyAddress(addr);
            var new_asm = cfg[codeId]["asm"].substring(0, cfg[codeId]["asm"].indexOf(addr)) + "# " + value + "\n" + cfg[codeId]["asm"].substring(cfg[codeId]["asm"].indexOf(addr))
            cfg[codeId]["asm"] = new_asm

            var new_label = cfg[codeId]["label"].substring(0, cfg[codeId]["label"].indexOf(addr)) + "# " + value + "\n" + cfg[codeId]["label"].substring(cfg[codeId]["label"].indexOf(addr))
            cfg[codeId]["label"] = new_label

        }

        else {
            console.log("State-less event")
        }
    }
    removeGraph();
    graphRender(-1);
}

function restore_graph_rename_after_rendering(BBId){

    for(var i in renameVariablesData) {
        var addr = renameVariablesData[i]['element'];
        var value = renameVariablesData[i]['value'];
        if(renameVariablesData[i]['event'] == 'rename') {
            if(!listOfVars.includes(value)) {
                listOfVars.push(value);
            }
            renameVariablesData[count] = renameVariablesData[i];
            count += 1;
            var codeId = getBBbyAddress(addr);
            var inner;
            $('span#' + addr + '.token.generic').each(function() {
                if($(this).parent()[0].className == 'token local') {
                    inner = $(this)[0].innerHTML;
                }
            });
            var isBBchanged = false;
            Object.keys(cfg).forEach(function(state) {
                $("code#" + state + " a > span.token.local").each(function() {
                    if($(this)[0].textContent == inner && state != BBId) {
                        isBBchanged = true;
                        $(this)[0].innerHTML = "<span class='token generic' style='filter:blur(8px)'>" + value + "</span>"
                    }
                    else if($(this)[0].textContent == inner && state == BBId) {
                        $(this)[0].innerHTML = "<span class='token generic' style='filter:'>" + value + "</span>"
                    }
                });

            });

        }
        else {
            console.log("State-less event")
        }
    }
}


function restore_graph_rename(data) {
    downloadedData = JSON.parse(data);
    count = 0;
    for(var i in downloadedData) {
        var addr = downloadedData[i]['element'];
        var value = downloadedData[i]['value'];

        if(downloadedData[i]['event'] == 'rename') {
	    listOfRenamedVariables.push(value)
            if(!listOfVars.includes(value)) {
                listOfVars.push(value);
            }
            renameVariablesData[count] = downloadedData[i];
            count += 1;
            var codeId = getBBbyAddress(addr);
            var inner;
            $('span#' + addr + '.token.generic').each(function() {
                if($(this).parent()[0].className == 'token local') {
                    inner = $(this)[0].innerHTML;
                }
            });
            var isBBchanged = false;
            Object.keys(cfg).forEach(function(state) {
                $("code#" + state + " a > span.token.local").each(function() {
                    if($(this)[0].textContent == inner) {
                        isBBchanged = true;
                        $(this)[0].innerHTML = "<span class='token generic' style='filter:blur(8px)'>" + value + "</span>"
                    }
                });
            });

        }
        else {
            console.log("State-less event")
        }
    }

    if(addr_to_zoom != 0) {
        scrollToAddress(addr_to_zoom, scrollEventsEnum.STR_XREF);
        obfuscate(cfg_getBBbyAddress(addr_to_zoom))

    }
}

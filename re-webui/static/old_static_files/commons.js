function push_function_history(function_id, addr) 
{
	console.log("Invoked push_function " + function_id + "at addr " + addr)
	if (function_id == null)
		function_id = func_to_download
	myHistory = 0
	try {
		list_of_functions = JSON.parse(localStorage.getItem('myFunctionHistory'))
	}
	catch(err) {
		console.log("We got an exception while parsing")
		localStorage.removeItem("myFunctionHistory")
		list_of_functions = null
	}
	if (list_of_functions == null)
		list_of_functions = []
	console.log("Pushing function " + function_id + "at addr " + addr)
	list_of_functions.push([function_id, addr])
	localStorage.setItem('myFunctionHistory', JSON.stringify(list_of_functions))
}

function pop_function_history() 
{
	console.log("Invoked pop_function")
	try {
		list_of_functions = JSON.parse(localStorage.getItem('myFunctionHistory'))
	}
	catch(err) {
		console.log("We got an exception while parsing")
		localStorage.removeItem("myFunctionHistory")
		list_of_functions = null
	}

	if (list_of_functions == null || list_of_functions.length == 0)
		return null
	ret = list_of_functions.pop()
	localStorage.setItem('myFunctionHistory', JSON.stringify(list_of_functions))
	return ret			// It returns an array of 2 elems (function & address)
}


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
                g.setEdge(cfg_edges[i][0], cfg_edges[i][1], {
                                label: "",
                                style: "fill: none; stroke-width: 4.5px;"
                });
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



function rename(htmlElementToRename) {
    var inner = htmlElementToRename.innerHTML;
    var r = prompt("insert the new name (max 8 chars)");
    if (listOfRenamedVariables.indexOf(r) >= 0) {
        alert('You already have a variable with this name')
        return
    }
    listOfRenamedVariables.push(r)
    if(r == "" || r == null)    return;
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
	
    renameCommentDict = {}
    Object.keys(cfg).forEach(function(state) {
        isBBchanged = false;
        $("code#" + state + " a > span.token.local").each(function() {

            if($(this)[0].textContent == inner) {
                if(state == bbCache)
                    $(this)[0].innerHTML = "<span class='token generic'>" + r + "</span>";
                else
                    $(this)[0].innerHTML = "<span class='token generic' style='filter:blur(8px)'>" + r + "</span>";
                isBBchanged = true;
		tokenAddress = $("code#" + state + " > span.token.address")[0]
		if (! (state in renameCommentDict)) {
			renameCommentDict[state] = tokenAddress
		}
            }

        });
        if (isBBchanged) {
            new_asm = $("code#" + state + '.language-nasm')[0].textContent;
            cfg[state]["asm"] = new_asm;

            new_label = cfg[state]["label"].substring(0, cfg[state]["label"].indexOf(state)) + new_asm + "</code></pre>"
            cfg[state]["label"] = new_label;
        }
    });
	
    generateComment = "[ " + inner.substring(1, inner.length - 1) + " ] -> " + r
    for (state in renameCommentDict) {
	do_comment(state, renameCommentDict[state], generateComment)
    }

    removeGraph()
    graphRender(bbCache)

}


function do_comment(codeId, tokenAddress, commentString) {
	var timeStamp = new Date().getTime();
	r = commentString
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

} 





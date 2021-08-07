function get_xrefs_from(func) {
    url = base_url + "/" + current_chall + "/"
    $.post(url + "get_xrefs_from", data={'name':func, 'token':id}, function(data) {
                xref = JSON.parse(data);
                console.log(xref);

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
    url = base_url + "/" + current_chall + "/"
    $.post(url + "get_xrefs_to", data={'name':func, 'token':id}, function(data) {
                xref = JSON.parse(data);

                if(!Object.keys(xref).length /*|| $('#x_to').length == 1*/)
                    return
                var msg = "<ul id='x_to' style='list-style:none;font-size:16px'>Xrefs to:"
                 for(var i in xref)
		    msg += "<li>" + "<a href=./?function=" + i + " onclick='push_function_history(&quot;" + func_to_download + "&quot;, null)'>"  + xref[i] + "</a>" + "</li>"
                 msg += "</ul>"
                 $('a#' + func).after(msg);
        });
}

function downloadCallGraph() {
    url = base_url + "/" + current_chall + "/"
    $.post(url + "getCallGraph", data={'name':'callgraph'}, function(data) {

         json_callgraph = JSON.parse(data);
         buildCallgraph();

    });
    return 0;
}




function downloadCFG(func) {
    	url = base_url + "/" + current_chall + "/"
        $.post(url + "getCFG", data={'name':func, 'token':id}, function(data) {
                json_cfg = JSON.parse(data);
                CFGbuilder(json_cfg, func)

        });
        return json_cfg
}




function send_results(data) {
    url = base_url + "/" + current_chall + "/"
    data["fcn_name"] = func_to_download;
    $.get(url + "getmethod/" + id + ";" + JSON.stringify(data));

}

var myData;
function downloadData() {
    	url = base_url + "/" + current_chall + "/"
	var downloadedData;	
	$.get(url + "getevents/?id=" + id + "&&fcn_name=" + func_to_download,  function(data) {
	    myData = data;
		restore_graph_comments(data);
        demo();

	});
}

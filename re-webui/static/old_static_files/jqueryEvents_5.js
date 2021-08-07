var clicked_register;
/*$(window).on("load", function() {
    downloadData();
})*/


$(document).ready(function() {
    $('div.sidenav').scrollTo($('#' + func_to_download).offset().top - 400, 0);
    $('#' + func_to_download).css("background", "green");
    $('#' + func_to_download).css("color", "yellow")
    get_xrefs_from(func_to_download);
    get_xrefs_to(func_to_download);

    $("div.cfg").on("mouseover", function() {

        // set onclick event over registers
        $('a.token.register.variable').each(function() {
            if($(this).attr("binded") != "true") {
                $(this).attr("binded", "true")
                $(this).on("click", function() {
                    clicked_register = $(this)[0].textContent;
                    //$(this).css("background", "red");
                    //$('.token.generic').each(function() {
                    $('a.token.register.variable').children().each(function() {

                        if($(this)[0].textContent.indexOf(clicked_register) >= 0) {
                            $(this).css("background", "red");
                            var span_id = $(this)[0].id;
                            $('span#' + span_id + '.token.generic').css('filter', '')
                            spanIds.push(span_id);
                        }
                        else {
                            $(this).css("background", "");
                        }

                    });

                })
            }
        });



        // set ondblclick events over 'jumpable' addresses
        $('span.token.number').each(function() {
            if($(this).attr("binded") != "true") {
                $(this).attr("binded", "true")
                $(this).on("dblclick", function(event) {
                    event.stopPropagation()
                    follow($(this)[0].textContent, $(this).children()[0].id, scrollEventsEnum.CLICK);
                    //localStorage.setItem("myFunctionHistory", 0);
                    obfuscate(destination);
                    previousBBid = destination;
                });
            }
        });

	
	$('span.token.generic').each(function() {
		if((this).innerHTML.includes("call") && $(this).attr("binded") != "true") {
			var foo = $(this)[0].innerHTML.substr(6)
			$(this).attr("binded", "true");
			$(this).on("dblclick", function(event) {
				event.stopPropagation();
				myHistory = 0;
				addr = localStorage.getItem("addr")
				push_function_history(func_to_download, addr)
				window.location.replace(base_url + '/fifth_chall/?function=' + foo )
			});

		}
	});


        // set onclick event over instruction address
        $('span.token.address').each(function() {
            if($(this).attr("binded") != "true") {
                $(this).attr("binded", "true")
                $(this).on("click", function(event) {
                    $(this).css("background", "yellow");
                    eip = $(this).children()[0].id;
                    //currentEipElement = $(this);
                    if (exEipElement) {
                        exEipElement.css("background", "");
                        exEipElement = $(this);
                    }
                    else {
                        exEipElement = $(this);
                    }
                });
            }
        });


        // set onmouseover event on the basic blocks
        Object.keys(cfg).forEach(function(state) {
            if($('g#' + state).attr("binded") != "true") {
                $('g#' + state).attr("binded", "true");
                $('g#' + state).on("mouseenter", function(){
                    selected(this);
            });
            }
        });
    });

});


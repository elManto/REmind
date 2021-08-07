var globalEvent;

const __menuConf = {
    "menu": undefined,
    "item": undefined,
    "menuState": false,
    "oldContent": [],

    // Style of menu
    "menuStyle": {
        display: "none",
        fontFamily: "monospace",
        width: "200 px",
        height: "min-content",
        padding: "8px 0 8px 0",
        margin: 0,
        borderRadius: "5px",
        border: "1px solid #555",
        backgroundColor: "#222",
        position: "absolute",
        top: 0,
        left: 0,
        userSelect: "none"
    },

    // Style menu items
    "itemStyle": {
        fontSize: "16px",
        padding: "2px 11px 2px 10px",
        margin: 0,
        color: "#ccc"
    },

    // Add items to menu
    "addContent": () => {
        let temp;

        if (!window.hasOwnProperty("menuContent")) {
            window["menuContent"] = [{
                title: "Empty",
                name: "empty"
            }];
        }

        __menuConf.oldContent = menuContent.map(a => {
            return a
        });
        __menuConf.menu.innerHTML = "";

        for (let i = 0; i < __menuConf.oldContent.length; i++) {
            if (__menuConf.oldContent[i] !== "<hr>") {
                temp = __menuConf.item;
                temp.id = "__menuItem" + i;
                temp.setAttribute("onmouseover", `this.style.color="#fff"; this.style.backgroundColor="#333"`);
                temp.setAttribute("onmouseout", `this.style.color="#ccc"; this.style.backgroundColor="#222"`);
                temp.setAttribute("onclick", `itemClick("${__menuConf.oldContent[i].name}")`);
                temp.innerHTML = __menuConf.oldContent[i].title;
                __menuConf.menu.innerHTML += temp.outerHTML;
            } else {
                __menuConf.menu.innerHTML += `<hr style="border: none; height: 1px; background-color: #444">`;
            }
        }
    },

    // Run at lib-start
    "startMenu": () => {
        __menuConf.menu = document.createElement("div");
        Object.assign(__menuConf.menu.style, __menuConf.menuStyle);
        __menuConf.menuEvent();

        __menuConf.item = document.createElement("p");
        Object.assign(__menuConf.item.style, __menuConf.itemStyle);

        __menuConf.addContent();
        document.body.appendChild(__menuConf.menu);

        if (!window.hasOwnProperty("itemClick")) {
            // Triggered on click of an item
            window["itemClick"] = (name) => {
                console.warn(`( Menu.js ):\nMenu-item ${name} was clicked.\n***`);
            }
        }
    },

    // Triggered on contextmenu event
    "menuEvent": (e) => {
        if (!window.hasOwnProperty("__menuEnabled")) {
            window["__menuEnabled"] = true;
        }

        if (__menuEnabled) {
            if (__menuConf.oldContent !== menuContent) {
                __menuConf.oldContent = menuContent.splice();
            }

            if (__menuConf.menuState) {
                openMenu(e);
            } else {
                closeMenu();
            }
        }
    },
};

// Contextmenu-eventlistener
document.addEventListener("contextmenu", (e) => {
	//console.log(e.composedPath()[0])
	globalEvent = e.composedPath()

	kindOfEl = e.composedPath()[0].className.toString();
	if (kindOfEl.indexOf("token") < 0) {
		return
	}
	
    if (__menuEnabled) {
        e.preventDefault();
    }
    __menuConf.menuState = !__menuConf.menuState;
    __menuConf.menuEvent(e);
}, false);

// Click-eventlistener
document.addEventListener("click", (e) => {
    __menuConf.menuState = false;
    if (navigator.userAgent.search("Firefox") >= 0) {
    	if(e.button != 2) closeMenu();
    }
    else {
	closeMenu();
    }
}, false);

// Open the menu
function openMenu(e) {
    kind = e.composedPath()[0].className.toString();
    console.log(e.composedPath()[0].id)
    if(kind == e.composedPath()[0].id + " token") {
        __menuConf.menu.style.display = "block";
        __menuConf.menu.style.top = e.clientY + "px";
        __menuConf.menu.style.left = 265 + "px";
    }
    else {
        __menuConf.menu.style.display = "block";
        __menuConf.menu.style.top = e.clientY + "px";
        __menuConf.menu.style.left = e.clientX + "px";
    }
}

// Cleses the menu
function closeMenu() {
    __menuConf.menu.style.display = "none";
}

// Starts the lib
window.addEventListener("load", __menuConf.startMenu, false);

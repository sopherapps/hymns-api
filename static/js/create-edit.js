/**
 * Javascript for creating or editing
 */

/**
 * Makes elements with the .auto-grow class to grow as more text is added to them
 */
(function () {
    'use strict';

    const autoGrowElements = document.getElementsByClassName("auto-grow");
    for (let i = 0; i < autoGrowElements.length; i++) {
        autoGrowElements[i].setAttribute("style", "height:" + (autoGrowElements[i].scrollHeight) + "px;overflow-y:hidden;");
        autoGrowElements[i].addEventListener("input", autoGrowOnInput, false);
    }

    function autoGrowOnInput() {
        this.style.height = (this.scrollHeight) + "px";
    }
})();

/**
 * Handles opening and closing tone selector
 */
(function () {
    'use strict';

    document.addEventListener("text-selected", handleTextSelected, false);
    document.addEventListener("close-toolbar", handleCloseToolbar, false);

    function handleTextSelected(event) {
        const toneSelectorElement = document.getElementById("tone-selector-modal");
        toneSelectorElement.classList.remove("hidden");
        const top = Math.round(event.detail.y);
        const left = Math.round(event.detail.x - (toneSelectorElement.offsetWidth / 2));
        toneSelectorElement.style.bottom = `calc(100vh - ${top}px)`;
        toneSelectorElement.style.left = `${left}px`;
        toneSelectorElement.dataset.selectionString = event.detail.selectionString;
    }

    function handleCloseToolbar(event) {
        document.getElementById("tone-selector-modal").classList.add("hidden");
    }
})();


/**
 * Handles selection of tone
 */
(function () {
    'use strict';

    const toneSelectorElement = document.getElementById("tone-selector");
    toneSelectorElement.addEventListener("change", handleToneSelection, false);

    function handleToneSelection(event) {
        const selectionString = event.target.parentNode.dataset.selectionString;
        const newTone = event.target.value;
        const newToneLength = newTone.length;
        document.execCommand("insertHTML", false, `<sup class='tone-marker'>${newTone}</sup><span style='margin-left: -${0.75 * newToneLength}em;'>${selectionString}</span>`);
        event.target.value = "";
        document.dispatchEvent(new Event("close-toolbar"));
    }
})();


/**
 * Handles the editing of custom-editors
 */
(function () {
    'use strict';

    const customEditors = document.getElementsByClassName("custom-editor");
    const contentEditableDivs = [...customEditors].map((editor, id) => createContentEditable(editor, `custom-editor-${new Date().getTime()}-${id}`));
    for (let i = 0; i < contentEditableDivs.length; i++) {
        customEditors[i].parentNode.insertBefore(
            contentEditableDivs[i],
            customEditors[i]
        );
        contentEditableDivs[i].addEventListener("mouseup", handleMouseup, false);
        contentEditableDivs[i].addEventListener("keyup", handleKeyup, false);
    }

    const prefilledCustomEditors = document.getElementsByClassName("prefilled-custom-editor");
    for (let i = 0; i < prefilledCustomEditors.length; i++) {
        prefilledCustomEditors[i].addEventListener("mouseup", handleMouseup, false);
        prefilledCustomEditors[i].addEventListener("keyup", handleKeyup, false);
    }


    function handleMouseup(event) {
        const selection = getSelection();
        if (selection) {
            document.dispatchEvent(new CustomEvent("text-selected", {
                detail: selection,
            }));
        } else {
            // close toolbar if it is open and a click outside the toolbar but
            // within the editor is made
            document.dispatchEvent(new Event("close-toolbar"));
        }
    }

    function handleKeyup(event) {
        const selection = getSelection();
        if (selection) {
            document.dispatchEvent(new CustomEvent("text-selected", {
                detail: selection,
            }));
        } else {
            // close toolbar if it is open and a click outside the toolbar but
            // within the editor is made
            document.dispatchEvent(new Event("close-toolbar"));
        }
    }

    function getSelection() {
        const selection = document.getSelection();

        const selectionString = selection?.toString();
        if (selectionString) {
            return {selectionString: selection.toString(), ...getCaretCoordinates(selection)};
        }
    }

    function getCaretCoordinates(selection) {
        let x = 0,
            y = 0;
        if (selection.rangeCount !== 0) {
            const range = selection.getRangeAt(0).cloneRange();
            range.collapse(true);
            const rect = range.getClientRects()[0];
            if (rect) {
                x = rect.left;
                y = rect.top;
            }
        }
        return {x, y};
    }

    function createContentEditable(textarea, uniqueId) {
        const div = document.createElement('div'),
            atts = textarea.attributes;

        div.className = textarea.className;
        div.id = uniqueId;
        div.innerHTML = textarea.value;

        textarea.setAttribute('custom-editor-editable-div-id', uniqueId);
        textarea.dataset.value = [];
        div.setAttribute('contentEditable', "true");
        div.setAttribute('spellcheck', "false");

        // re-create all attributes from the textearea to the new created div
        for (var i = 0, n = atts.length; i < n; i++) {
            // do not re-create existing attributes
            if (!div.hasAttribute(atts[i].nodeName)) {
                div.setAttribute(atts[i].nodeName, atts[i].value);
            }
        }

        textarea.setAttribute('hidden', true);

        return div;
    }
})();

/**
 * Sends the create-song request
 */
function createSong() {
    const csrftoken = document.getElementById("csrftoken").value;
    const number = document.getElementById("number").value;
    const language = document.getElementById("language").value;
    const title = document.getElementById("title").value;
    const key = document.getElementById("key").value;
    const linesElement = document.getElementById("lines");
    const lines = extractLines(linesElement);
    const song = {number, language, title, key, lines};
    const errors = get_errors_in_song(song)
    if (errors) {
        alert(errors);
    } else {
        fetch("/admin/", {
            method: "POST",
            headers: {"Content-Type": "application/json", csrftoken},
            body: JSON.stringify(song),
            redirect: "follow",
        }).then(resp => {
            if (resp.ok && resp.redirected) {
                window.location.replace(resp.url);
            } else {
                resp.text().then(text => alert(text)).catch(() => alert(JSON.stringify(resp)));
            }
        }).catch(err => {
            alert(err);
        });
    }
}

/**
 * Gets the errors in a given song object
 * @param song {{number: string, language: string, title: string, key: string, lines: {note: string, words: string}[][]}}
 * @return {string}
 */
function get_errors_in_song(song) {
    let errors = "";
    if (!song.number) {
        errors += "song number is required.\n";
    }
    if (!song.language) {
        errors += "song language is required.\n";
    }
    if (!song.title) {
        errors += "song title is required.\n";
    }
    if (!song.key) {
        errors += "song key is required.\n";
    }
    if (!song.lines) {
        errors += "song lines is required.\n";
    }
    return errors;
}

/**
 * Extracts an array of song lines from a content editable div or from a text area
 * @param editableElement {HTMLDivElement | HTMLTextAreaElement}
 * @return {{note: string, words: string}[][]}
 */
function extractLines(editableElement) {
    let editableDiv = editableElement;
    if (editableElement.tagName === "TEXTAREA") {
        const associatedDivId = editableElement.getAttribute('custom-editor-editable-div-id');
        editableDiv = document.getElementById(associatedDivId);
    }

    const innerDivs = [...editableDiv.getElementsByTagName("div")];

    const firstLineUpperBound = editableDiv.innerHTML.indexOf("<div>");
    if (firstLineUpperBound > 0) {
        const firstDiv = document.createElement("div");
        firstDiv.innerHTML = editableDiv.innerHTML.slice(0, firstLineUpperBound);
        innerDivs.unshift(firstDiv)
    }

    return innerDivs.map(extractLine);
}

/**
 * Extracts an array of line sections from a div that represents a line in a song
 * @param lineDiv {HTMLDivElement}
 * @return {{note: string, words: string}[]}
 */
function extractLine(lineDiv) {
    const sups = [...lineDiv.getElementsByTagName("sup")];
    const lineSections = sups.map(extractLineSection);

    const firstNode = lineDiv.firstChild;
    if (firstNode?.nodeType === Node.TEXT_NODE) {
        lineSections.unshift({note: null, words: firstNode.textContent})
    }

    const lastNode = lineDiv.lastChild;
    if (lastNode?.nodeType === Node.TEXT_NODE) {
        lineSections.push({note: null, words: lastNode.textContent})
    }

    return lineSections;
}

/**
 * Extracts a line section from a <sup> (and its next sibling)
 * @param lineSectionSup {HTMLElement}
 * @return {{note: string, words: string}}
 */
function extractLineSection(lineSectionSup) {
    const note = lineSectionSup.textContent;
    const words = lineSectionSup.nextElementSibling?.textContent || "";
    return {note, words}
}
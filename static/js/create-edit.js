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
            return { selectionString: selection.toString(), ...getCaretCoordinates(selection) };
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
        return { x, y };
    }

    function createContentEditable(textarea, uniqueId) {
        const div = document.createElement('div'),
            atts = textarea.attributes;

        div.className = textarea.className;
        div.id = uniqueId;
        div.innerHTML = textarea.value;

        textarea.setAttribute('custom-editor-textarea-id', uniqueId);
        div.setAttribute('contentEditable', true);
        div.setAttribute('spellcheck', false);

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
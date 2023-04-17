/**
 * Javascript for the index html template
 */

"use strict";

/**
 * Handle a click on the delete button
 * 
 * @param {Event} event - the event passed
 */
function handleDeleteBtnClick(event) {
    event.preventDefault();
    const confirmationModal = document.getElementById("delete-confirmation-modal");
    _clearDeleteModalState(confirmationModal);
    _showModal(confirmationModal);
    console.log(event.target.dataset.songNumber);
    confirmationModal.dataset.songNumber = event.target.dataset.songNumber;
}


/**
 * Handle a click on the pagination previous button
 * 
 * @param {Event} event - the event passed
 */
function handlePaginationPrevBtnClick(event) {

}


/**
 * Handle a click on the pagination next button
 * 
 * @param {Event} event - the event passed
 */
function handlePaginationNextBtnClick(event) {

}


/**
 * Handle a click on the modal's cancel button
 * 
 * @param {Event} event - the event passed
 */
function handleModalCancelBtnClick(event) {
    const confirmationModal = event.target.closest("#delete-confirmation-modal");
    _clearDeleteModalState(confirmationModal);
    _hideModal(confirmationModal);
}


/**
 * Handle a click on the modal's confirm button
 * 
 * @param {Event} event - the event passed
 */
function handleModalConfirmBtnClick(event) {
    const confirmationModal = event.target.closest("#delete-confirmation-modal");
    const confirmationInput = confirmationModal.querySelector("#delete-confirmation-input");
    const errorMessageElement = confirmationModal.querySelector("#error-message");

    const expectedSongNumber = `${confirmationModal.dataset.songNumber}`;
    const actualSongNumber = `${confirmationInput.value?.trim()}`;

    console.log({ expectedSongNumber, actualSongNumber });

    if (actualSongNumber === expectedSongNumber) {
        // delete song
        console.log("delete song");
        _clearDeleteModalState(confirmationModal);
        _hideModal(confirmationModal);
    } else {
        errorMessageElement.innerText = "The Song numbers don't match";
    }
}


/**
 * Clears the state of the delete confirmation modal element
 * 
 * @param {HTMLElement} modal - the html modal element
 */
function _clearDeleteModalState(modal) {
    const confirmationInput = modal.querySelector("#delete-confirmation-input");
    const errorMessageElement = modal.querySelector("#error-message");
    modal.dataset.songNumber = "";
    errorMessageElement.innerText = "";
    confirmationInput.value = "";
}


/**
 * Makes the HTML modal visible
 * 
 * @param {HTMLElement} modal - the HTML modal element
 */
function _showModal(modal) {
    modal.classList.add("flex");
    modal.classList.remove("hidden");
}

/**
 * Hides the HTML modal
 * 
 * @param {HTMLElement} modal - the HTML modal element
 */
function _hideModal(modal) {
    modal.classList.add("hidden");
}
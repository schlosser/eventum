$(function() {

    /* =======================================================================
     * HTML Content generators
     *
     * Is there any way to make these less ugly? :[
     * =====================================================================*/

    function selectedImage(filename, url) {
        return '<li class="image post-image" data-filename="' + filename + '" data-url="' + url + '"> ' +
               '    <i style="background-image:url(' + url + ');"></i>' +
               '    <p class="filename">' + filename + '</p>' +
               '    <span class="delete">' +
               '        <span class="delete-inner">' +
               '            <a href="#remove-image" data-filename="' + filename + '" data-url="' + url + '">' +
               '                <i class="fa fa-trash-o fa-2x"></i>' +
               '            </a>' +
               '        </span>' +
               '    </span>' +
               '</li>';
    }
    function modalImage(filename, url) {
        return  '<li class="image" data-filename="' + filename + '">' +
                '    <a data-filename="' + filename + '" data-url="' + url + '" href="#add-image">' +
                '        <i style="background-image:url(' + url + ');"></i>' +
                '        <div class="select"><i class="fa fa-plus fa-6x"></i></div>' +
                '      </a>' +
                '</li>';
    }
    function hiddenInput(filename, id) {
        return '<li><input id="' + id + '" name="' + id + '" type="text" value="' + filename + '"></li>';
    }


    /* =======================================================================
     * Marked / Epiceditor initialization
     * =====================================================================*/


    var opts = window.epicEditorDefaultOpts,
        maxHeight = $(window).height()*0.75;

    opts.autogrow.maxHeight = maxHeight;
    var editor = new EpicEditor(opts).load();

    /* Populated object of associated images for markdown rendering */
    $('.post-image').each(function() {
        window.markdownImages[$(this).data('filename')] = $(this).data('url');
    });

    /* =======================================================================
     * Click Handlers
     *
     * Note the use of `$(document).on()` to bind the click events.  This
     * ensures that even dynamically created elements will activate the
     * click handlers properly.
     * ==================================================================== */

    /* Remove an image from the associated images */
    $(document).on('click', 'a[href="#remove-image"]', function(e) {
        e.preventDefault();
        var filename = $(this).data('filename'),
            url = $(this).data('url');

        // Remove the image from the markdown rendering list
        delete window.markdownImages[filename];

        // Add the image back to the list in the modal
        $('.modal .image-grid').append(modalImage(filename, url));

        // Remove the hidden input, so it will be removed on the server
        $('input[value="' + filename + '"]').remove();

        // Remove the image from the list below the editor
        $('.selected-images .image[data-filename="' + filename + '"]').remove();

    });

    $(document).on('click', 'a[href="#add-image"]', function(e) {
        e.preventDefault();
        var filename = $(this).data('filename'),
            url = $(this).data('url');

        /* Find the id of the next hidden `<input type="text">` that will hold
         * the filename of associated images */
        var i = 0;
        while (document.getElementById("images-"+i)) { i++; }
        var id = "images-"+i;

        // Close the modal
        $('a[href="#close-modal"]').click();

        // Add to record of filenames to replace on markdown rendering
        images[filename] = url;

        // Remove the image from the list in the modal
        $('.modal .image[data-filename="' + filename + '"]').remove();

        // Append a hidden input to the form, to be synced with the server
        $('#images').append(hiddenInput(filename, id));

        // Append the image to the list below the editor
        $('.selected-images').append(selectedImage(filename, url));
    });

    /* Submit the form */
    $(document).on('click', 'a[href="#save"]', function(e) {
        e.preventDefault();
        $('#save-post').click();
    });


    /* Tie the published toggle to the form element */
    $(document).on('click', '.active a[href="#toggle"]', function(e) {
        $('#published').prop('checked', false); });
    $(document).on('click', '.toggle-wrapper:not(.active) a[href="#toggle"]', function(e) {
        $('#published').prop('checked', true); });

});




$(function() {

    /* =======================================================================
     * HTML Content generators
     *
     * Is there any way to make these less ugly? :[
     * =====================================================================*/

    function selectedImage(filename, url) {
        return '<li class="image post-image" data-filename="' + filename + '" data-url="' + url + '"> ' +
               '    <i style="background-image:url(' + url + ');"></i>' +
               '    <p class="filename">' +
               '        <i class="featured-image fa fa-star-o"></i>' + filename +
               '    </p>'
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
                '    <a data-filename="' + filename + '" data-url="' + url + '" href="#select-image">' +
                '        <i style="background-image:url(' + url + ');"></i>' +
                '        <div class="select"><i class="fa fa-plus fa-6x"></i></div>' +
                '      </a>' +
                '</li>';
    }
    function hiddenInput(filename, id) {
        return '<li><input id="' + id + '" name="' + id + '" type="text" value="' + filename + '"></li>';
    }


    function addedTag(tag, id){
        return '<li class="tag" data-tag="' + tag + '">' + tag + ' <a href="#remove-tag" data-tag="' + tag + '">x</a></li>'
    }

    function hiddenTag(tag, id){
        return '<li><input id="' + id + '" name="' + id + '" type="text" value="' + tag + '"></li>'
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

    $(document).on('click', 'a[href="#select-image"]', function(e) {
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
        window.markdownImages[filename] = url;

        // Remove the image from the list in the modal
        $('.modal .image[data-filename="' + filename + '"]').remove();

        // Append a hidden input to the form, to be synced with the server
        $('#images').append(hiddenInput(filename, id));

        // Append the image to the list below the editor
        $('.selected-images').append(selectedImage(filename, url));
    });

    $(document).on('click', 'a[href="#preview-button"]', function(e){
        e.preventDefault();
        $('#preview').prop('checked', true);
        $('#save-post').click();
    });
    /* Submit the form */
    $(document).on('click', 'a[href="#save"]', function(e) {
        e.preventDefault();
        $('#save-post').click();
    });

    /**/
    var featuredImage = $('#featured_image').val();
    if (featuredImage) {
        var $imageToSelect = $('.featured-image[data-filename="' + featuredImage + '"]');
        $imageToSelect.addClass('fa-star').removeClass('fa-star-o');
    }

    /* Add featured image */
    $(document).on('click', '.featured-image.fa-star-o', function(e) {
        e.preventDefault();

        // Remove any other featured-images
        $('.featured-image.fa-star').removeClass('fa-star').addClass('fa-star-o');

        $(this).removeClass('fa-star-o').addClass('fa-star');

        var filename = $(this).data('filename');
        $('#featured_image').val(filename);
    });

    /* Remove featured image */
    $(document).on('click', '.featured-image.fa-star', function(e) {
        e.preventDefault();

        $(this).removeClass('fa-star').addClass('fa-star-o');
        $('#featured_image').val('');
    });

    /* Tie the published toggle to the form element */
    $(document).on('click', '.active a[href="#toggle"]', function(e) {
        $('#published').prop('checked', false);
        setTimeout(function() {
            $('#save-post').click();
        }, 500);
    });

    $(document).on('click', '.toggle-wrapper:not(.active) a[href="#toggle"]', function(e) {
        $('#published').prop('checked', true);
        setTimeout(function() {
            $('#save-post').click();
        }, 500);

    });

    /* Add a tag */
    $('#tag-field').keypress(function(e){
        var key = e.which;
        if (key == 13)
        {
            e.preventDefault();
            var i = 0;
            while (document.getElementById("tags-"+i)) { i++; }
            var id = "tags-"+i;

           val = $('#tag-field').val()
           if (val){
            // alert($('#tag-field').val())
            $('#tags').append(hiddenTag(val, id));
        // Append the image to the list below the editor
            $('.tag-list').append(addedTag(val, id));
            $('#tag-field').val("");
            }
        }

    });

    /* Remove a tag */
    $(document).on('click', 'a[href="#remove-tag"]', function(e) {
        e.preventDefault();
        var tag = $(this).data('tag');

        // Remove the hidden input, so it will be removed on the server
        $('input[value="' + tag + '"]').remove();

        // Remove the tag from the list above the editor
        $('.tag-list .tag[data-tag="' + tag + '"]').remove();

    });

});





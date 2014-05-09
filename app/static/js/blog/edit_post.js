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


    /* Initalize the markdown renderer */
    var maxHeight = $(window).height()*0.75,
        marked_custom = marked,
        renderer = new marked.Renderer(),
        markdown_images = {};

    /* Populated object of associated images for markdown rendering */
    $('.post-image').each(function() {
        markdown_images[$(this).data('filename')] = $(this).data('url');
    });

    /* EpicEditor renders everything in an `iframe`, so relative paths to
     * image urls.  This function replaces any `href` in an image that points
     * to an associated image with the actual url that it should be rendered from.
     *
     * This is an override of a Marked function.
     */
    renderer.image = function(href, title, text) {
        if (href in markdown_images) {
            href = markdown_images[href];
        }
        var out = '<img src="' + href + '" alt="' + text + '"';
        if (title) {
           out += ' title="' + title + '"';
        }
        out += this.options.xhtml ? '/>' : '>';
        return out;
    }

    // Marked options
    marked_custom.setOptions({
        renderer: renderer,
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: false,
        smartLists: true,
        smartypants: false,
        highlight: function (code) {
            return hljs.highlightAuto(code).value;
        }
    });

    // EpicEditor options
    var opts = {
        container: 'epiceditor',
        parser: marked_custom,
        textarea: 'body',
        autogrow: {
            minHeight: 160,
            maxHeight: maxHeight
        },
        theme: {
            base: '/themes/base/epiceditor.css',
            preview: '/themes/preview/github-highlighted.css',
            editor: '/themes/editor/epic-dark.css'
        }
    };
    var editor = new EpicEditor(opts).load();

    /* =======================================================================
     * Click Handlers
     *
     * Note the use of `$(document).on()` to bind the click events.  This
     * ensures that even dynamically created elements will activate the
     * click handlers properly.
     * =====================================================================*/

    /* Open the modal */
    $(document).on('click', 'a[href="#show-modal"]', function(e) {
        e.preventDefault();
        $('.opaque').removeClass("hidden");
        $('body').addClass('modal-open');
    });

    /* Close the modal */
    $(document).on('click', 'a[href="#close-modal"], .opaque', function(e) {
        e.preventDefault();
        $('.opaque').addClass("hidden");
        $('body').removeClass('modal-open');
    });

    /* Make sure that clicking the modal itself doesn't propgate and trigger
     * a click on the `.opaque` background */
    $(document).on('click', '.modal', function(e) { e.stopPropagation(); });

    /* Remove an image from the associated images */
    $(document).on('click', 'a[href="#remove-image"]', function(e) {
        e.preventDefault();
        var filename = $(this).data('filename'),
            url = $(this).data('url');

        // Remove the image from the markdown rendering list
        delete markdown_images[filename];

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

        // Add to record of filenames to replace on mardkown rendering
        images[filename] = url;

        // Remove the image from the list in the modal
        $('.modal .image[data-filename="' + filename + '"]').remove();

        // Append a hidden input to the form, to be synced with the server
        $('#images').append(hiddenInput(filename, id));

        // Append the image to the list below the editor
        $('.selected-images').append(selectedImage(filename, url));
    });
});




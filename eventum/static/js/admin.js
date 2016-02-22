$(function() {
    /* =======================================================================
     * Mobile Drawer Button
     * ==================================================================== */

     $('.toggle').click(function() {
        $('nav').toggleClass('open');
     });

    /* =======================================================================
     * Google Plus Logout
     * ==================================================================== */

    $('a[href="#logout"]').click(function(e) {
        e.preventDefault();
        gapi.auth.signOut();
        window.location.href = '/admin/logout';
    });

    /* =======================================================================
     * Flashes
     * ==================================================================== */

    /* Dismiss Flash */
    $(document).on('click', 'a[href="#dismiss-flash"]', function(e) {
        e.preventDefault();
        $flash_wrapper = $(this).parent().parent();
        $flash_wrapper.addClass('dismissed');
    });

    /* Setup flashes */
    $('.flash').each(function() {
        $flash_wrapper = $(this).parent();
        $(this).css({"height": $(this).outerHeight()});
        $flash_wrapper.css({"height": $(this).outerHeight()});
    });


    /* =======================================================================
     * Confirm
     * ==================================================================== */

    /* Open confirm dialog */
    $(document).on('click', 'a[href="#open-confirm"]', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).siblings('.confirm').toggleClass('confirm-hidden');
    });

    /* Dismiss confirm dialog*/
    $(document).on('click', '.confirm-cancel', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).parent().parent().addClass('confirm-hidden');
    });


    /* =======================================================================
     * Toggle
     * ==================================================================== */

    $(document).on('click', '.active a[href="#toggle"]', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).parent().removeClass("active");
    });

    $(document).on('click', '.toggle-wrapper:not(.active) a[href="#toggle"]', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).parent().addClass("active");
    });


    /* =======================================================================
     * Modals
     * ==================================================================== */

    /* Open the modal */
    $(document).on('click', 'a[href="#show-modal"]', function(e) {
        e.preventDefault();
        modal_id = $(this).data('modal') || "modal";
        $('.opaque[data-modal=' + modal_id + ']').removeClass("hidden");
        $('body').addClass('modal-open');
        $('.image-grid-wrapper').height($('.image-grid').height());
    });

    /* Close the modal */
    $(document).on('click', 'a[href="#close-modal"], .opaque', function(e) {
        e.preventDefault();
        modal_id = $(this).data('modal') || "modal";
        $('.opaque[data-modal="' + modal_id + '"]').addClass("hidden");
        $('body').removeClass('modal-open');
    });

    /* Make sure that clicking the modal itself doesn't propgate and trigger
     * a click on the `.opaque` background */
    $(document).on('click', '.modal', function(e) { e.stopPropagation(); });

    /* =======================================================================
     * Table row clicking
     * ==================================================================== */

    $(document).on('click', 'table.click tbody tr', function(e) {
        e.preventDefault();
        window.location.href = $(this).find('a.tr-link').attr("href");
    });

    /* =======================================================================
     * Image Grids
     * ==================================================================== */

    $('.image-grid-wrapper').height($('.image-grid').height());

    /* =======================================================================
     * Marked (Markdown Renderer)
     * ==================================================================== */


    /* Initalize the markdown renderer */
    var marked_custom = marked,
        renderer = new marked.Renderer();
    window.markdownImages = {};

    /* EpicEditor renders everything in an `iframe`, so relative paths to
     * image urls.  This function replaces any `href` in an image that points
     * to an associated image with the actual url that it should be rendered from.
     *
     * This is an override of a Marked function.
     */

    renderer.image = function(href, title, text) {
        if (href in window.markdownImages) {
            href = window.markdownImages[href];
        }
        var out = '<img src="' + href + '" alt="' + text + '"';
        if (title) {
           out += ' title="' + title + '"';
        }
        out += this.options.xhtml ? '/>' : '>';
        return out;
    };

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
    window.epicEditorDefaultOpts = {
        container: 'epiceditor',
        parser: marked_custom,
        textarea: 'body',
        useNativeFullscreen: false,
        autogrow: {
            minHeight: 80,
            maxHeight: 160
        },
        theme: {
            base: '/themes/base/epiceditor.css',
            preview: '/themes/preview/github-highlighted.css',
            editor: '/themes/editor/epic-dark.css'
        }
    };


});
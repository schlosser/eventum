$(function() {

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
});
$(function() {

    /* Show the confirm dialog on click of the "Remove" button*/
    $(".whitelist-remove").click(function(e) {
        e.preventDefault();
        $('.whitelist-confirm-wrapper').addClass('whitelist-hidden');
        $(this).siblings().removeClass('whitelist-hidden');
    });

    /* Hide the confirm dialog on click of the "Cancel" button*/
    $(".whitelist-cancel").click(function() {
        $(this).parent().parent().addClass('whitelist-hidden');
    });

    $(document).on('click', 'a[href="#open-confirm"]', function(e) {
        e.preventDefault();
        $(this).siblings('.confirm').removeClass('confirm-hidden');
    });

    $(document).on('click', '.confirm-cancel', function(e) {
        e.preventDefault();
        $(this).parent().parent().addClass('confirm-hidden');
    });
});
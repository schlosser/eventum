$(function() {

    /* Show the confirm dialog on click of the "Remove" button*/
    $(".whitelist-remove").click(function(e) {
        e.preventDefault();
        $('.whitelist-confirm-wrapper').addClass('whitelist-hidden');
        $(this).siblings().removeClass('whitelist-hidden');
    });

    /* Remove this item on click of the "Delete" button */
    $(".whitelist-confirm").submit(function(e) {
        e.preventDefault();
        var email = $(this).data('email');
        $.post('/whitelist/delete/'+email)
        .done(function(resp) {
            console.log(resp);
            $(".whitelist-item[data-email='" + email + "']").slideUp(100, function() {
                $(this).remove();
            });
        })
        .fail(function(resp) {
            console.log(resp);
        });
    });

    /* Hide the confirm dialog on click of the "Cancel" button*/
    $(".whitelist-cancel").click(function() {
        $(this).parent().parent().addClass('whitelist-hidden');
    });
});
$(function() {

    /* Show the confirm dialog on click of the "Remove" button*/
    $(".whitelist-remove").click(function() {
        $('.whitelist-confirm-wrapper').addClass('whitelist-hidden');
        $(this).siblings().removeClass('whitelist-hidden');
    });

    /* Remove this item on click of the "Delete" button */
    $(".whitelist-confirm").submit(function(e) {
        e.preventDefault();
        var email = $(this).data('email');
        $.post('/whitelist/remove/'+$(this).data('email'))
        .done(function(resp) {
            console.log(resp);
            $(".whitelist-item[data-email='" + email + "']").slideUp(function() {
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
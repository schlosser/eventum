$(function() {

    $(document).on('click', 'a[href="#save"]', function(e) {
        e.preventDefault();
        $('.edit-user-form').submit();
    });
});
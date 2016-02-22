$(function() {
    $('.delete-image').click(function(e) {
        e.preventDefault();
        $(this).children('form').submit();
    });
});
$(function() {
    $('form.subscribe .submit').click(function() {
        $(this).parent('form').submit();
    });

    $('a[href="#top"]').click(function(e) {
        e.preventDefault();
        $('html,body').animate({
          scrollTop: $('html, body').offset().top
        }, 200  );
    });
});

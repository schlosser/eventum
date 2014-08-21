$(function() {
    $('form.subscribe .submit').click(function() {
        $(this).parent('form').submit();
    });

    $('.navbar a').click(function(e) {
        e.stopPropagation();
    });

    $('.navbar').click(function() {
        $('html,body').animate({
          scrollTop: $('html, body').offset().top
        }, 200  );
    });

    $(window).scroll( function(e) {
        if ($(window).scrollTop() > 20) {
            $('.navbar').addClass('scroll');
        } else {
            $('.navbar').removeClass('scroll');
        }
    });
});

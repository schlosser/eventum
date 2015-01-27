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


    var $image = $('.hero i');
    var md = new MobileDetect(window.navigator.userAgent);
    var $devfestbanner = $('.devfest-banner');
    var $nav = $('nav');
    var $hero = $('.hero');
    if (md.mobile() == null) {
        $(window).scroll(function(e){
            var scrolled = $(window).scrollTop();
            console.log(scrolled);
            $image.css('transform','translateY(' + (scrolled/2) + 'px)');
            if ($devfestbanner !== undefined) {
                if (scrolled > $hero.height()) {
                    $devfestbanner.addClass('up');
                } else if (scrolled  <= 0) {
                    $devfestbanner.removeClass('up');
                }
            }
        });
    }
});

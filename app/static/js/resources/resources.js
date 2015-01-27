$(function() {

    $('.slideto').click(function(e) {
        e.preventDefault();
        id = $(this).attr('href');
        $('html,body').animate({
          scrollTop: $(id).offset().top
        }, 200  );
    });

    var md = new MobileDetect(window.navigator.userAgent);
    if (md.mobile() == null) {
        $(window).scroll( function(e) {
            if ($(window).scrollTop() > $('.sidebar-wrapper').offset().top - 80) {
                $('.navbar').addClass('up');
            } else {
                $('.navbar').removeClass('up');
            }
            if ($(window).scrollTop() > $('.sidebar-wrapper').offset().top ) {
                $('.sidebar').addClass('fixed');
            } else {
                $('.sidebar').removeClass('fixed');
            }

            var bottomOfSidebar = $('.sidebar .inner').offset().top + $('.sidebar .inner').height();
            var bottomOfSidebarWrapper = $('.sidebar-wrapper').offset().top + $('.sidebar-wrapper').height();
            var topOfSidebar = $('.sidebar .inner').offset().top;
            var topOfVisibleWindow = $(window).scrollTop();

            if (!$('.sidebar').hasClass('bottom') && bottomOfSidebar > bottomOfSidebarWrapper){
                $('.sidebar').addClass('bottom');
            } else if (topOfSidebar > topOfVisibleWindow) {
                $('.sidebar').removeClass('bottom');
            }


        });
    }

    $('a[href="#set-track"]').click(function(e) {
        e.preventDefault();

        if ($(this).parent().hasClass('on')) {
            $('.on').removeClass('on');
            $('.in-track').removeClass('in-track');
            return;
        }

        topics = $(this).data('topics').split(',');
        $('.on').removeClass('on');

        $(this).parent().addClass('on');
        for(var i = 0; i < topics.length; i++) {
            $('#'+topics[i]).addClass('on');
            $('.sidebar li[data-topic="' + topics[i] + '"]').addClass('on');
        }
        $('.topic, .topics li, .tracks li, .sidebar').addClass('in-track');
    });
});
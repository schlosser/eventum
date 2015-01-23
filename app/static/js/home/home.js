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


    $image = $('.hero i');
    $(window).scroll(function(e){
      var scrolled = $(window).scrollTop();
      console.log(scrolled);
      $image.css('transform','translateY(' + (scrolled/2) + 'px)');
    });
});

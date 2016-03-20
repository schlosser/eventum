$(function() {
    $('.image-grid-wrapper').height($('.image-grid'));

    $('.delete-image').click(function(e) {
        e.preventDefault();
        $(this).children('form').submit();
    });

      $('#images-ajax-loadpoint').load("/admin/media/image_selector", function(response, status){
      if (status == "error"){
          $('error-message').text("Sorry, there was an error loading the images.");
      }
    });
});
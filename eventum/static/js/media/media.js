$(function() {
  $('.image-grid-wrapper').height($('.image-grid'));

  $('#images-ajax-loadpoint').load("/admin/media/image-view?mode=editor", function(response, status) {
    if (status == "error") {
      $('error-message').text("Sorry, there was an error loading the images.");
    }
  });

  $(document).on('click', '.delete-image', function(e) {
    e.preventDefault();
    $(this).children('form').submit();
  });
});
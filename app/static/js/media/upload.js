$(function() {
    function setInitialPositions() {
        var extension = $('input[name="extension"]').val();
        var filename = $('input[name="filename"]').val();
        $('.extension').html(extension);
        if (filename) {
            width = calculateWordWidth(filename);
            $('input[name="filename"]').animate({"width":width + 20}, 50);
        }
    }

    setInitialPositions()

    /* let the `btn-upload` div act as the file input */
    $(".btn-upload").click(function () {
        $('input[name="image"]').trigger('click');
        return false;
    });

    /* Automatically populate the filename field when a file is chosen */
    $('input[name="image"]').change(function(){
        var filename = $(this).val().split('/').pop().split('\\').pop();
        var pieces = filename.split(".");
        if (pieces[1]) {
            $('.extension').html("." + pieces[1].toLowerCase());
            $('input[name="extension"]').val("." + pieces[1].toLowerCase());
        }
        width = calculateWordWidth(pieces[0]);
        $('input[name="filename"]').attr("placeholder",pieces[0]);
        $('input[name="filename"]').animate({"width":width + 20}, 50);
        $('input[name="filename"]').val(pieces[0]);
    });

    /* Match the width of the filename field to the width of the input */
    $('input[name="filename"]').keydown(function() {
        width = calculateWordWidth($(this).val());
        $('input[name="filename"]').animate({"width":width + 20}, 50);
    });

    function calculateWordWidth(text, classes) {
        classes = classes || [];
        classes.push('text-width-calculation');
        var div = document.createElement('div');
        div.setAttribute('class', classes.join(' '));
        div.innerHTML = text;
        document.body.appendChild(div);
        var width = jQuery(div).outerWidth(true);
        div.parentNode.removeChild(div);
        return width;
    }

});
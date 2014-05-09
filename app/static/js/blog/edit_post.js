$(function() {
    var maxHeight = $(window).height()*0.75;
    var marked_custom = marked;
    marked_custom.setOptions({
        renderer: new marked.Renderer(),
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: false,
        sanitize: false,
        smartLists: true,
        smartypants: false,
        highlight: function (code) {
            return hljs.highlightAuto(code).value;
        }
    });
    var opts = {
        container: 'epiceditor',
        parser: marked_custom,
        textarea: 'body',
        autogrow: {
            minHeight: 160,
            maxHeight: maxHeight
        },
        theme: {
            base: '/themes/base/epiceditor.css',
            preview: '/themes/preview/github-highlighted.css',
            editor: '/themes/editor/epic-dark.css'
        }
    };
    var editor = new EpicEditor(opts).load();

    $('a[href="#show-modal"]').click(function(e) {
        e.preventDefault();
        $('.opaque').removeClass("hidden");
        $('body').addClass('modal-open');
    });
    $('a[href="#close-modal"], .opaque').click(function(e) {
        e.preventDefault();
        $('.opaque').addClass("hidden");
        $('body').removeClass('modal-open');
    });
    $('.modal').click(function(e) {
        e.stopPropagation();
    });

    $('a[href="#add-image"]').click(function(e) {
        e.preventDefault();
        $('a[href="#close-modal"]').click();


        var i = 0;
        while (document.getElementById("images-"+i)) {
            i++;
        }
        var filename = $(this).data('filename'),
            url = $(this).data('url'),
            id = "images-"+i;

        $('.modal .image[data-filename="' + filename + '"]').remove();
        $('#images').append('<li><input id="' + id + '" name="' + id + '" type="text" value="' + filename + '"></li>');
        $('.selected-images').append(
'<li class="image"> ' +
'    <i style="background-image:url(' + url + ');"></i>' +
'     <p class="filename">' + filename + '</p>' +
'</li>'
        );
    });





});
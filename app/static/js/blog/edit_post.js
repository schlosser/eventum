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
            console.log("hi", code);
            return hljs.highlightAuto(code).value;
        }
    });
    var opts = {
        container: 'epiceditor',
        parser: marked_custom,
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
});
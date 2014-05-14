$(function() {
	$("a[href='#dismiss-flash']").click(function(e) {
        e.preventDefault();
        $(this).parent().slideUp(200);
    });
});
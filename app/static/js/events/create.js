$(function() {
    /* Submit the form */
    $(document).on('click', 'a[href="#save"]', function(e) {
        e.preventDefault();
        $('#save-event').click();
    });

    /* Tie the published toggle to the form element */
    $(document).on('click', '.active a[href="#toggle"]', function(e) {
        $('#published').prop('checked', false); });
    $(document).on('click', '.toggle-wrapper:not(.active) a[href="#toggle"]', function(e) {
        $('#published').prop('checked', true); });

});
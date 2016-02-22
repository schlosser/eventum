$(function() {

    $('input[name="user_type"]:radio').change(function() {
        selection = $('input[name="user_type"]:checked').val();
        if (selection === 'fake_user') {
            $('.for-fake-user').removeClass('hidden');
            $('.for-whitelist').addClass('hidden');
        } else {
            $('.for-fake-user').addClass('hidden');
            $('.for-whitelist').removeClass('hidden');
        }
    });

    /* =======================================================================
     * Table Highlight and Click
     * ==================================================================== */
    $('td').hover(function() {
        var columnNo = parseInt($(this).index()) + 1;
        $('td:nth-child(' + columnNo + ')').addClass('highlighted');
    },
    function() {
        var columnNo = parseInt($(this).index()) + 1;
        $('td:nth-child(' + columnNo + ')').removeClass('highlighted');
    });

    var $all_td = $('td');
    $('input[name="user_type"]:radio').on('click', function() {
        all_td.removeClass('clicked');
        $(this).closest('td').addClass('clicked');
        var header = parseInt($(this).closest('td').index()) + 1;
        $('td:nth-child(' + header + ')').addClass('clicked');
    });

    /* =======================================================================
     * Fake User Image
     * ==================================================================== */

    $(document).on('click', 'a[href="#set-image"]', function(e) {
        e.preventDefault();
        var filename = $(this).data('filename'),
            url = $(this).data('url');

        // Close the modal
        $('a[href="#close-modal"][data-modal="image"]').click();

        // Set the hidden input to have the image as it's value
        $('#fake_user_image').val(filename);

        $('.display-image i').css({
            'background-image': 'url(' + url + ')'
        });

        $('.set-image').addClass('hidden');
        $('.display-image').removeClass('hidden');
    });

    $(document).on('click', 'a[href="#remove-image"]', function(e) {
        e.preventDefault();

        $('#fake_user_image').val('');
        $('.display-image i').css({
            'background-image': ''
        });
        $('.set-image').removeClass('hidden');
        $('.display-image').addClass('hidden');
    });
});
$(function() {

    function dayAtIndex(index) {
        return ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][index];
    }

    function modalToForm() {
        $('#frequency').val($("#m-frequency").val());
        $('#every').val($("#m-every").val());
        $('input[name="ends"]').removeAttr('checked');
        var end_val = $('input[name="m-ends"]:checked').val();
        $('input[name="ends"][value=' + end_val + ']').prop('checked', true);
        if (end_val == 'on') {
            $('#recurrence_end_date').val($("#m-recurrence_end_date").val());
            $('#num_occurrences').val(1);
        } else if (end_val == 'after') {
            $('#num_occurrences').val($("#m-num_occurrences").val());
            $('#recurrence_end_date').val("");
        }
        $('.create-event-form .summary').text($('.modal .summary').text());
        $('#recurrence_summary').val($('.modal .summary').text());
    }

    function formToModal() {
        $('#m-frequency').val($("#frequency").val());
        $('#m-every').val($("#every").val());
        $('input[name="m-ends"]').removeAttr('checked');
        var end_val = $('input[name="ends"]:checked').val();
        $('input[name="m-ends"][value=' + end_val + ']').prop('checked', true);
        $('#m-num_occurrences').val($("#num_occurrences").val());
        if ($("#recurrence_end_date").val()){
            $('#m-recurrence_end_date').val($("#recurrence_end_date").val());
        } else {
            $('#m-recurrence_end_date').val($("#start_date").val());
        }
        $('.modal .summary').val($('#recurrence_summary').text());
    }

    function getSummary() {
        var summary = "";
        if ($("#m-every").val() == 1) {
            summary += $("#m-frequency option:selected").val();
        } else {
            summary += "Every " +
                      $("#m-every").val() +
                      " " +
                      $("#m-frequency option:selected").data("enumerable");
        }
        summary += " on " + dayAtIndex($('#m-starts').datepicker('getDate').getDay());
        switch ($('input[name="m-ends"]:checked').val()) {
            case "after":
                summary += ", for " + $("#m-num_occurrences").val() + " occurrences";
                break;
            case "on":
                summary += ", until " + $("#m-recurrence_end_date").val();
        }
        return summary;
    }


    /* =======================================================================
     * Initalize the date and timepickers
     * ==================================================================== */

    $('.datetime .time').timepicker({
        'showDuration': true,
        'timeFormat': 'g:ia'
    });
    if ($('.datetime .time').timepicker('getTime') === null) {
        $('.datetime .start.time').timepicker('setTime', '7:00pm');
        $('.datetime .end.time').timepicker('setTime', '8:00pm');
    }

    $('.datetime .date').datepicker({
        'format': 'm/d/yyyy',
        'todayHighlight': true,
        'autoclose': true
    });
    if ($('.datetime .date').datepicker('getDates')[0] === undefined) {
        $('.datetime .date').datepicker('setDates', new Date());
    }

    $('.datetime').datepair();

    $(".create-event-form .summary").text($("#recurrence_summary").val());

    /* Submit the form */
    $(document).on('click', 'a[href="#save"]', function(e) {
        e.preventDefault();
        $('#save-event').click();
    });

    /* Tie the published toggle to the form element */
    $(document).on('click', '.active a[href="#toggle"]', function(e) {
        $('#published').prop('checked', false);
        setTimeout(function() {
            $('.save-button').click();
        }, 500);
    });
    $(document).on('click', '.toggle-wrapper:not(.active) a[href="#toggle"]', function(e) {
        $('#published').prop('checked', true);
        setTimeout(function() {
            $('.save-button').click();
        }, 500);
    });


    $(document).on('click', '#is_recurring', function(e) {
        if($(this).is(':checked')) {
            // The event will be recurring
            $('.toolbar .right .delete-event').attr('href', '#show-modal');
            $('.create-event-form .summary').removeClass('hidden');
            if (!$('.create-event-form .summary').text()) {
                e.preventDefault();
                $('a[data-modal="repeat"]').click();
            } else {
                $('.repeat > label').text("Repeat:");
                $('a[href="#show-modal"][data-modal="repeat"]').text("Edit");
            }
        } else {
            // The event is not recurring.
            $('.toolbar .right .delete-event').attr('href', '#delete');
            $('a[href="#show-modal"][data-modal="repeat"]').text("");
            $('.repeat > label').text("Repeat...");
            $('.create-event-form .summary').addClass('hidden');
        }
    });

    $(document).on('click', 'a[href="#show-modal"]', function(e) {
        $('.modal .date').datepicker({
            'format': 'm/d/yyyy',
            'todayHighlight': true,
            'autoclose': true,
            'startDate': $('.datetime .date').datepicker('getDates')[0]
        });
        $("#m-starts").val($('.datetime .date').val());
        formToModal();
        $('.modal .summary').text(getSummary());
    });
    $(document).on('focus', '#m-recurrence_end_date', function() {
        $('input[name="m-ends"]').removeAttr('checked');
        $(this).siblings('input[type="radio"]').prop("checked", true);
    });
    $(document).on('focus', '#m-num_occurrences', function() {
        $('input[name="m-ends"]').removeAttr('checked');
        $(this).siblings('input[type="radio"]').prop("checked", true);
    });
    $(document).on('change', '.modal form :input', function() {
        $('.modal .summary').text(getSummary());
    });
    $(document).on('submit', '.m-repeat-form', function(e) {
        e.preventDefault();
        modalToForm();
        $('#is_recurring').prop('checked', true);
        $('.repeat > label').text("Repeat:");
        $('a[href="#close-modal"]').click();
        $('a[href="#show-modal"][data-modal="repeat"]').text("Edit");
    });

    $(document).on('click', 'a[href="#save-following"]', function(e) {
        e.preventDefault();
        $('#update_following').prop('checked', true);
        $('a[href="#save"]').click();
    });

    $(document).on('click', 'a[href="#save-all"]', function(e) {
        e.preventDefault();
        $('#update_all').prop('checked', true);
        $('a[href="#save"]').click();
    });

    $(document).on('click', 'a[href="#delete"]', function(e) {
        e.preventDefault();
        $('.toolbar .right form').submit();
    });

    $(document).on('click', 'a[href="#delete-following"]', function(e) {
        e.preventDefault();
        $('#delete_following').prop('checked', true);
        $('a[href="#delete"]').click();
    });

    $(document).on('click', 'a[href="#delete-all"]', function(e) {
        e.preventDefault();
        $('#delete_all').prop('checked', true);
        $('a[href="#delete"]').click();
    });

    /* =======================================================================
     * Event Image
     * ==================================================================== */

    $(document).on('click', 'a[href="#set-image"]', function(e) {
        e.preventDefault();
        var filename = $(this).data('filename'),
            url = $(this).data('url');

        // Close the modal
        $('a[href="#close-modal"]').click();

        // Set the hidden input to have the image as it's value
        $('#event_image').val(filename);

        $('.display-image i').css({
            'background-image': 'url(' + url + ')'
        });

        $('.set-image').addClass('hidden');
        $('.display-image').removeClass('hidden');
    });

    $(document).on('click', 'a[href="#remove-image"]', function(e) {
        e.preventDefault();

        $('#event_image').val('');
        $('.display-image i').css({
            'background-image': ''
        });
        $('.set-image').removeClass('hidden');
        $('.display-image').addClass('hidden');
    });


    /* =======================================================================
     * Marked / Epiceditor initialization
     * =====================================================================*/

    var opts = window.epicEditorDefaultOpts;
    opts.container='epiceditor-short-description';
    opts.textarea='short_description';
    var shortDescriptionEditor = new EpicEditor(opts).load();

    opts.container='epiceditor-long-description';
    opts.textarea='long_description';
    opts.autogrow = {
        minHeight: 160,
        maxHeight: 320
    };
    var longDescriptionEditor = new EpicEditor(opts).load();

    /* Populated object of associated images for markdown rendering */
    $('.post-image').each(function() {
        window.markdownImages[$(this).data('filename')] = $(this).data('url');
    });
});
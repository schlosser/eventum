$(function() {

    function dayAtIndex(index) {
        return ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"][index];
    }

    function modalToForm() {
        $('#repeats').val($("#m-repeats").val());
        $('#every').val($("#m-every").val());
        $('input[name="ends"]').removeAttr('checked');
        var end_val = $('input[name="m-ends"]:checked').val();
        $('input[name="ends"][value=' + end_val + ']').prop('checked', true);
        $('#num_occurances').val($("#m-num_occurances").val());
        $('#repeat_end_date').val($("#m-repeat_end_date").val());
        $('.create-event-form .summary').text($('.modal .summary').text());
        $('#summary').val($('.modal .summary').text());
    }

    function formToModal() {
        $('#m-repeats').val($("#repeats").val());
        $('#m-every').val($("#every").val());
        $('input[name="m-ends"]').removeAttr('checked');
        var end_val = $('input[name="ends"]:checked').val();
        $('input[name="m-ends"][value=' + end_val + ']').prop('checked', true);
        $('#m-num_occurances').val($("#num_occurances").val());
        $('#m-repeat_end_date').val($("#repeat_end_date").val());
        $('.modal .summary').val($('#summary').text());
    }

    function getSummary() {
        var summary = "";
        if ($("#m-every").val() == 1) {
            summary += $("#m-repeats option:selected").val();
        } else {
            summary += "Every " +
                      $("#m-every").val() +
                      " " +
                      $("#m-repeats option:selected").data("enumerable");
        }
        summary += " on " + dayAtIndex($('#m-starts').datepicker('getDate').getDay());
        switch ($('input[name="m-ends"]:checked').val()) {
            case "never":
                break;
            case "after":
                summary += ", for " + $("#m-num_occurances").val() + " occurances";
                break;
            case "on":
                summary += ", until " + $("#m-repeat_end_date").val();
        }
        return summary;
    }

    /* =======================================================================
     * Initalize the date and timepickers
     * =====================================================================*/


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

    $(".create-event-form .summary").text($("#summary").val());
    $("#repeat_end_date").val($('.datetime .date').val());

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


    $(document).on('click', '#repeat', function(e) {
        if($(this).is(':checked')) {
            $('.create-event-form .summary').removeClass('hidden');
            if (!$('.create-event-form .summary').text()) {
                e.preventDefault();
                $('a[href="#show-modal"]').click();
            } else {
                $('.repeat > label').text("Repeat:");
                $('a[href="#show-modal"]').text("Edit");
            }
        } else {
            $('a[href="#show-modal"]').text("");
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
    $(document).on('focus', '#m-repeat_end_date', function() {
        $('input[name="m-ends"]').removeAttr('checked');
        $(this).siblings('input[type="radio"]').prop("checked", true);
    });
    $(document).on('focus', '#m-num_occurances', function() {
        $('input[name="m-ends"]').removeAttr('checked');
        $(this).siblings('input[type="radio"]').prop("checked", true);
    });
    $(document).on('change', '.modal form :input', function() {
        $('.modal .summary').text(getSummary());
    });
    $(document).on('submit', '.m-repeat-form', function(e) {
        e.preventDefault();
        modalToForm();
        $('#repeat').prop('checked', true);
        $('.repeat > label').text("Repeat:");
        $('a[href="#close-modal"]').click();
        $('a[href="#show-modal"]').text("Edit");
    })
});
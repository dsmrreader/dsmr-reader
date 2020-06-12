$(document).ready(function () {
    initialize_datepicker('start_datepicker', datepicker_start_date, 'start_date');
    initialize_datepicker('end_datepicker', datepicker_end_date, 'end_date');

    $("#download_button").click(function () {
        $("#download_form").submit();
        return false;
    });
});

function initialize_datepicker(datepicker_id, initial_date, input_id) {
    $("#" + datepicker_id).datepicker({
        startView: 'months',
        minViewMode: 'days',
        maxViewMode: 'years',
        calendarWeeks: true,
        weekStart: 1,
        startDate: datepicker_start_date,
        endDate: datepicker_end_date,
        format: datepicker_locale_format,
        language: datepicker_language_code

    }).on('changeDate', function (e) {
        var selected_date = moment(e.date).format(datepicker_locale_format.toUpperCase());
        $("#" + input_id).val(selected_date)

    }).datepicker('update', initial_date).datepicker('setDate', initial_date);
}
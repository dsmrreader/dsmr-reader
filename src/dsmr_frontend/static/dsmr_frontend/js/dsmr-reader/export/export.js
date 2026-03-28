$(document).ready(function () {
    initialize_datepicker('start_datepicker', datepicker_start_date, 'start_date');
    initialize_datepicker('end_datepicker', datepicker_end_date, 'end_date');

    $("#download_button").click(function () {
        $("#download_form").submit();
        return false;
    });
});

function initialize_datepicker(datepicker_id, initial_date, input_id) {
    var fp = flatpickr("#" + datepicker_id, {
        inline: true,
        defaultDate: initial_date,
        minDate: datepicker_start_date,
        maxDate: datepicker_end_date,
        dateFormat: "Y-m-d",
        locale: datepicker_language_code.startsWith('nl') ? 'nl' : 'default',
        onChange: function (selectedDates) {
            let selected_date = dayjs(selectedDates[0]).format(datepicker_locale_format.toUpperCase());
            $("#" + input_id).val(selected_date);
        }
    });

    /* Set initial value in the hidden form input. */
    if (fp.selectedDates.length > 0) {
        let selected_date = dayjs(fp.selectedDates[0]).format(datepicker_locale_format.toUpperCase());
        $("#" + input_id).val(selected_date);
    }
}

var g_trends_start_date = null;
var g_trends_end_date = null;

function initialize_trends_datepicker(datepicker_id, initial_date, on_change_date_callback) {
    var fp = flatpickr("#" + datepicker_id, {
        inline: true,
        defaultDate: initial_date,
        minDate: DATEPICKER_START_DATE,
        maxDate: DATEPICKER_END_DATE,
        dateFormat: "Y-m-d",
        locale: DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl' : 'default',
        onChange: function (selectedDates) {
            if (datepicker_id === 'start_datepicker') {
                g_trends_start_date = selectedDates[0];
            } else {
                g_trends_end_date = selectedDates[0];
            }
            on_change_date_callback();
        }
    });

    /* Store the initial date so update_trends() can use it on page load. */
    if (fp.selectedDates.length > 0) {
        if (datepicker_id === 'start_datepicker') {
            g_trends_start_date = fp.selectedDates[0];
        } else {
            g_trends_end_date = fp.selectedDates[0];
        }
    }
}

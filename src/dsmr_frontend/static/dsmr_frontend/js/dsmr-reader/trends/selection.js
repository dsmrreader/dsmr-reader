function initialize_trends_datepicker(datepicker_id, initial_date, on_change_date_callback) {
    $("#" + datepicker_id).datepicker({
        startView: 'days',
        minViewMode: 'days',
        maxViewMode: 'years',
        calendarWeeks: true,
        weekStart: 1,
        startDate: DATEPICKER_START_DATE,
        endDate: DATEPICKER_END_DATE,
        format: DATEPICKER_LOCALE_FORMAT,
        language: DATEPICKER_LANGUAGE_CODE
    }).on('changeDate', function (e) {
        on_change_date_callback();
    }).datepicker(
        'update', initial_date
    );
}
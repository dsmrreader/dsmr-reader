function initialize_trends_datepicker(datepicker_id, initial_date, on_change_date_callback) {
    $("#" + datepicker_id).datepicker({
        startView: 'days',
        minViewMode: 'days',
        maxViewMode: 'years',
        calendarWeeks: true,
        weekStart: 1,
        startDate: datepicker_start_date,
        endDate: datepicker_end_date,
        format: datepicker_locale_format,
        language: datepicker_language_code
    }).on('changeDate', function (e) {
        on_change_date_callback();
    }).datepicker(
        'update', initial_date
    );
}
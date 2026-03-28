var g_start_picker_month = null;
var g_end_picker_month = null;
var g_start_selected = null;
var g_end_selected = null;

$(document).ready(function () {
    var startDate = new Date(datepicker_start_date);
    var endDate = new Date(datepicker_end_date);

    g_start_selected = startDate;
    g_end_selected = endDate;
    g_start_picker_month = {year: startDate.getFullYear(), month: startDate.getMonth()};
    g_end_picker_month = {year: endDate.getFullYear(), month: endDate.getMonth()};

    $('#start_datepicker').show();
    $('#end_datepicker').show();

    render_picker('start');
    render_picker('end');

    set_form_value('start_date', g_start_selected);
    set_form_value('end_date', g_end_selected);

    $('#download_button').click(function () {
        $('#download_form').submit();
        return false;
    });
});

function set_form_value(input_id, date) {
    var formatted = dayjs(date).format(datepicker_locale_format.toUpperCase());
    $('#' + input_id).val(formatted);
}

/**
 * Renders the day-grid calendar picker for the given side ('start' or 'end').
 * Reads / mutates: g_start_picker_month / g_end_picker_month, g_start_selected / g_end_selected.
 */
function render_picker(which) {
    var startDate = new Date(datepicker_start_date);
    var endDate = new Date(datepicker_end_date);
    var locale = datepicker_language_code.startsWith('nl') ? 'nl-NL' : 'en-GB';

    var picker_month = which === 'start' ? g_start_picker_month : g_end_picker_month;
    var selected = which === 'start' ? g_start_selected : g_end_selected;
    var container_id = which === 'start' ? 'start_datepicker' : 'end_datepicker';
    var input_id = which === 'start' ? 'start_date' : 'end_date';

    var year = picker_month.year;
    var month = picker_month.month;

    /* Weekday header row — Monday first (Jan 1 2024 is a Monday) */
    var weekdays = '';
    for (var d = 0; d < 7; d++) {
        var name = new Intl.DateTimeFormat(locale, {weekday: 'short'}).format(new Date(2024, 0, 1 + d));
        weekdays += '<div class="dsmr-picker-weekday">' + name + '</div>';
    }

    /* Number of days in this month; weekday of the 1st (0=Mon … 6=Sun) */
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;

    var cells = '';

    /* Spillover days from previous month */
    var prevMonthDays = new Date(year, month, 0).getDate();
    for (var p = firstWeekday - 1; p >= 0; p--) {
        cells += '<button class="dsmr-picker-cell muted" disabled>' + (prevMonthDays - p) + '</button>';
    }

    /* Days of current month */
    var minDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
    var maxDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
    for (var day = 1; day <= daysInMonth; day++) {
        var cellDate = new Date(year, month, day);
        var isDisabled = cellDate < minDate || cellDate > maxDate;
        var isActive = selected
            && selected.getFullYear() === year
            && selected.getMonth() === month
            && selected.getDate() === day;
        var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
        if (isDisabled) {
            cells += '<button class="' + cls + '" disabled>' + day + '</button>';
        } else {
            cells += '<button class="' + cls + '" data-day="' + day + '">' + day + '</button>';
        }
    }

    /* Trailing spillover to complete the last row */
    var totalCells = firstWeekday + daysInMonth;
    var trailingCells = (7 - (totalCells % 7)) % 7;
    for (var n = 1; n <= trailingCells; n++) {
        cells += '<button class="dsmr-picker-cell muted" disabled>' + n + '</button>';
    }

    /* Nav disabled logic */
    var prevMonthDate = new Date(year, month - 1, 1);
    var nextMonthDate = new Date(year, month + 1, 1);
    var prevDisabled = prevMonthDate < new Date(startDate.getFullYear(), startDate.getMonth(), 1);
    var nextDisabled = nextMonthDate > new Date(endDate.getFullYear(), endDate.getMonth(), 1);

    var titleStr = new Intl.DateTimeFormat(locale, {month: 'long', year: 'numeric'}).format(new Date(year, month, 1));

    document.getElementById(container_id).innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + titleStr + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid dsmr-picker-grid--days">' + weekdays + cells + '</div>' +
        '</div>';

    var container = document.getElementById(container_id);

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        if (which === 'start') {
            g_start_picker_month = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
        } else {
            g_end_picker_month = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
        }
        render_picker(which);
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        if (which === 'start') {
            g_start_picker_month = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
        } else {
            g_end_picker_month = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
        }
        render_picker(which);
    });
    container.querySelectorAll('.dsmr-picker-cell[data-day]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            var newDate = new Date(year, month, parseInt(this.getAttribute('data-day')));
            if (which === 'start') {
                g_start_selected = newDate;
            } else {
                g_end_selected = newDate;
            }
            set_form_value(input_id, newDate);
            render_picker(which);
        });
    });
}

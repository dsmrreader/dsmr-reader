var g_trends_start_date = null;
var g_trends_end_date = null;

let g_datepicker_view_mode = 'months';
let g_datepicker_selections = {};
let g_day_picker_month = {'start': null, 'end': null};
let g_month_picker_year = {'start': null, 'end': null};
let g_year_picker_decade_start = {'start': null, 'end': null};


$(document).ready(function () {
    $("#datepicker_trigger_days").click(function () {
        g_datepicker_view_mode = 'days';
        switch_mode();
    });

    $("#datepicker_trigger_months").click(function () {
        g_datepicker_view_mode = 'months';
        switch_mode();
    });

    $("#datepicker_trigger_years").click(function () {
        g_datepicker_view_mode = 'years';
        switch_mode();
    });

    /* Pre-select end date for both pickers so update_trends() fires on load. */
    var initialDate = new Date(DATEPICKER_END_DATE);
    g_datepicker_selections['start'] = initialDate;
    g_datepicker_selections['end'] = initialDate;
    g_trends_start_date = initialDate;
    g_trends_end_date = initialDate;

    switch_mode();
});

/**
 * Shows the appropriate pickers for the current mode.
 */
function switch_mode() {
    $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
    $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);

    ['start', 'end'].forEach(function (postfix) {
        if (g_datepicker_view_mode === 'days') {
            $('#datepicker-' + postfix + '-day').show();
            $('#datepicker-' + postfix + '-month').hide();
            $('#datepicker-' + postfix + '-year').hide();

            var sel = g_datepicker_selections[postfix] || endDate;
            g_day_picker_month[postfix] = {year: sel.getFullYear(), month: sel.getMonth()};
            render_day_picker(postfix);
        } else if (g_datepicker_view_mode === 'months') {
            $('#datepicker-' + postfix + '-day').hide();
            $('#datepicker-' + postfix + '-month').show();
            $('#datepicker-' + postfix + '-year').hide();

            if (!g_month_picker_year[postfix]) {
                g_month_picker_year[postfix] = endDate.getFullYear();
            }
            g_month_picker_year[postfix] = Math.max(startDate.getFullYear(),
                Math.min(endDate.getFullYear(), g_month_picker_year[postfix]));
            render_month_picker(postfix);
        } else {
            $('#datepicker-' + postfix + '-day').hide();
            $('#datepicker-' + postfix + '-month').hide();
            $('#datepicker-' + postfix + '-year').show();

            if (!g_year_picker_decade_start[postfix]) {
                g_year_picker_decade_start[postfix] = Math.floor(endDate.getFullYear() / 10) * 10;
            }
            render_year_picker(postfix);
        }
    });
}

/**
 * Updates selection globals and triggers trend refresh.
 */
function on_trends_selection(postfix, date) {
    g_datepicker_selections[postfix] = date;

    if (postfix === 'start') {
        g_trends_start_date = date;
    } else {
        g_trends_end_date = date;
    }

    update_trends();
}

/**
 * Renders the day-grid calendar picker for the given postfix.
 * Reads / mutates: g_day_picker_month[postfix], g_datepicker_selections[postfix].
 */
function render_day_picker(postfix) {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var year = g_day_picker_month[postfix].year;
    var month = g_day_picker_month[postfix].month;
    var locale = DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl-NL' : 'en-GB';

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
        var sel = g_datepicker_selections[postfix];
        var isActive = sel
            && sel.getFullYear() === year
            && sel.getMonth() === month
            && sel.getDate() === day;
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

    document.getElementById('datepicker-' + postfix + '-day').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + titleStr + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid dsmr-picker-grid--days">' + weekdays + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-' + postfix + '-day');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_day_picker_month[postfix] = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
        render_day_picker(postfix);
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_day_picker_month[postfix] = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
        render_day_picker(postfix);
    });
    container.querySelectorAll('.dsmr-picker-cell[data-day]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            on_trends_selection(postfix, new Date(year, month, parseInt(this.getAttribute('data-day'))));
            render_day_picker(postfix);
        });
    });
}

/**
 * Renders the month-grid picker for the given postfix.
 * Reads / mutates: g_month_picker_year[postfix], g_datepicker_selections[postfix].
 */
function render_month_picker(postfix) {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var year = g_month_picker_year[postfix];
    var locale = DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl-NL' : 'en-GB';

    var months = [];
    for (var i = 0; i < 12; i++) {
        months.push(new Intl.DateTimeFormat(locale, {month: 'short'}).format(new Date(2024, i, 1)));
    }

    var prevDisabled = (year - 1) < startDate.getFullYear();
    var nextDisabled = (year + 1) > endDate.getFullYear();

    var cells = '';
    for (var m = 0; m < 12; m++) {
        var cellDate = new Date(year, m, 1);
        var minMonth = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
        var maxMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
        var isDisabled = cellDate < minMonth || cellDate > maxMonth;
        var sel = g_datepicker_selections[postfix];
        var isActive = sel && sel.getFullYear() === year && sel.getMonth() === m;
        var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
        if (isDisabled) {
            cells += '<button class="' + cls + '" disabled>' + months[m] + '</button>';
        } else {
            cells += '<button class="' + cls + '" data-month="' + m + '">' + months[m] + '</button>';
        }
    }

    document.getElementById('datepicker-' + postfix + '-month').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + year + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-' + postfix + '-month');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_month_picker_year[postfix]--;
        render_month_picker(postfix);
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_month_picker_year[postfix]++;
        render_month_picker(postfix);
    });
    container.querySelectorAll('.dsmr-picker-cell[data-month]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            on_trends_selection(postfix, new Date(g_month_picker_year[postfix], parseInt(this.getAttribute('data-month')), 1));
            render_month_picker(postfix);
        });
    });
}

/**
 * Renders the year-grid picker for the given postfix.
 * Reads / mutates: g_year_picker_decade_start[postfix], g_datepicker_selections[postfix].
 * Shows 12 years (decadeStart−1 … decadeStart+10) like Bootstrap Datepicker.
 */
function render_year_picker(postfix) {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var ds = g_year_picker_decade_start[postfix];

    var prevDisabled = (ds - 1) < startDate.getFullYear();
    var nextDisabled = (ds + 10) > endDate.getFullYear();

    var cells = '';
    for (var y = ds - 1; y <= ds + 10; y++) {
        var isOutOfDecade = y < ds || y > ds + 9;
        var isDisabled = y < startDate.getFullYear() || y > endDate.getFullYear();
        var sel = g_datepicker_selections[postfix];
        var isActive = sel && sel.getFullYear() === y;
        var cls = 'dsmr-picker-cell'
            + (isOutOfDecade && !isDisabled ? ' muted' : '')
            + (isActive ? ' active' : '');
        if (isDisabled) {
            cells += '<button class="' + cls + '" disabled>' + y + '</button>';
        } else {
            cells += '<button class="' + cls + '" data-year="' + y + '">' + y + '</button>';
        }
    }

    document.getElementById('datepicker-' + postfix + '-year').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + ds + '\u2013' + (ds + 9) + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-' + postfix + '-year');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_year_picker_decade_start[postfix] -= 10;
        render_year_picker(postfix);
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_year_picker_decade_start[postfix] += 10;
        render_year_picker(postfix);
    });
    container.querySelectorAll('.dsmr-picker-cell[data-year]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            on_trends_selection(postfix, new Date(parseInt(this.getAttribute('data-year')), 0, 1));
            render_year_picker(postfix);
        });
    });
}

let g_datepicker_view_mode = 'months';
let g_selected_date = null;
let g_day_picker_month = null;
let g_month_picker_year = null;
let g_year_picker_decade_start = null;
let summary_xhr_request = null;
let g_graph_xhr_request = null;


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

    /* Initial mode. */
    switch_mode();
});

/**
 * Shows the appropriate picker for the current mode and triggers a view update.
 */
function switch_mode() {
    $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
    $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);

    if (g_datepicker_view_mode === 'days') {
        $('#datepicker-day').show();
        $('#datepicker-month').hide();
        $('#datepicker-year').hide();
        if (!g_selected_date) {
            g_selected_date = endDate;
        }
        g_day_picker_month = {year: g_selected_date.getFullYear(), month: g_selected_date.getMonth()};
        render_day_picker();
    } else if (g_datepicker_view_mode === 'months') {
        $('#datepicker-day').hide();
        $('#datepicker-month').show();
        $('#datepicker-year').hide();

        if (!g_selected_date) {
            g_selected_date = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
        }
        g_month_picker_year = Math.max(startDate.getFullYear(),
            Math.min(endDate.getFullYear(), g_selected_date.getFullYear()));
        render_month_picker();
    } else {
        $('#datepicker-day').hide();
        $('#datepicker-month').hide();
        $('#datepicker-year').show();

        if (!g_selected_date) {
            g_selected_date = new Date(endDate.getFullYear(), 0, 1);
        }
        g_year_picker_decade_start = Math.floor(g_selected_date.getFullYear() / 10) * 10;
        render_year_picker();
    }

    update_view(g_selected_date);
}

/**
 * Renders the day-grid calendar picker into #datepicker-day.
 * Reads / mutates: g_day_picker_month, g_selected_date.
 */
function render_day_picker() {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var year = g_day_picker_month.year;
    var month = g_day_picker_month.month;
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
        var isActive = g_selected_date
            && g_selected_date.getFullYear() === year
            && g_selected_date.getMonth() === month
            && g_selected_date.getDate() === day;
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

    document.getElementById('datepicker-day').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + titleStr + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid dsmr-picker-grid--days">' + weekdays + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-day');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_day_picker_month = {year: prevMonthDate.getFullYear(), month: prevMonthDate.getMonth()};
        render_day_picker();
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_day_picker_month = {year: nextMonthDate.getFullYear(), month: nextMonthDate.getMonth()};
        render_day_picker();
    });
    container.querySelectorAll('.dsmr-picker-cell[data-day]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            g_selected_date = new Date(year, month, parseInt(this.getAttribute('data-day')));
            update_view(g_selected_date);
            render_day_picker();
        });
    });
}

/**
 * Renders the month-grid picker into #datepicker-month.
 * Reads / mutates: g_month_picker_year, g_selected_date.
 */
function render_month_picker() {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var year = g_month_picker_year;
    var locale = DATEPICKER_LANGUAGE_CODE.startsWith('nl') ? 'nl-NL' : 'en-GB';

    var months = [];
    for (var i = 0; i < 12; i++) {
        months.push(new Intl.DateTimeFormat(locale, {month: 'short'}).format(new Date(2024, i, 1)));
    }

    var prevDisabled = year - 1 < startDate.getFullYear();
    var nextDisabled = year + 1 > endDate.getFullYear();

    var cells = '';
    for (var m = 0; m < 12; m++) {
        var cellDate = new Date(year, m, 1);
        var minMonth = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
        var maxMonth = new Date(endDate.getFullYear(), endDate.getMonth(), 1);
        var isDisabled = cellDate < minMonth || cellDate > maxMonth;
        var isActive = g_selected_date
            && g_selected_date.getFullYear() === year
            && g_selected_date.getMonth() === m;
        var cls = 'dsmr-picker-cell' + (isActive ? ' active' : '');
        if (isDisabled) {
            cells += '<button class="' + cls + '" disabled>' + months[m] + '</button>';
        } else {
            cells += '<button class="' + cls + '" data-month="' + m + '">' + months[m] + '</button>';
        }
    }

    document.getElementById('datepicker-month').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + year + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-month');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_month_picker_year--;
        render_month_picker();
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_month_picker_year++;
        render_month_picker();
    });
    container.querySelectorAll('.dsmr-picker-cell[data-month]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            g_selected_date = new Date(g_month_picker_year, parseInt(this.getAttribute('data-month')), 1);
            update_view(g_selected_date);
            render_month_picker();
        });
    });
}

/**
 * Renders the year-grid picker into #datepicker-year.
 * Reads / mutates: g_year_picker_decade_start, g_selected_date.
 * Shows 12 years (decadeStart−1 … decadeStart+10) like Bootstrap Datepicker.
 */
function render_year_picker() {
    var startDate = new Date(DATEPICKER_START_DATE);
    var endDate = new Date(DATEPICKER_END_DATE);
    var ds = g_year_picker_decade_start;

    /* Prev disabled when the previous decade contains no valid years. */
    var prevDisabled = (ds - 1) < startDate.getFullYear();
    var nextDisabled = (ds + 10) > endDate.getFullYear();

    var cells = '';
    for (var y = ds - 1; y <= ds + 10; y++) {
        var isOutOfDecade = y < ds || y > ds + 9;
        var isDisabled = y < startDate.getFullYear() || y > endDate.getFullYear();
        var isActive = g_selected_date && g_selected_date.getFullYear() === y;
        var cls = 'dsmr-picker-cell'
            + (isOutOfDecade && !isDisabled ? ' muted' : '')
            + (isActive ? ' active' : '');
        if (isDisabled) {
            cells += '<button class="' + cls + '" disabled>' + y + '</button>';
        } else {
            cells += '<button class="' + cls + '" data-year="' + y + '">' + y + '</button>';
        }
    }

    document.getElementById('datepicker-year').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + ds + '\u2013' + (ds + 9) + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker-year');

    container.querySelector('.dsmr-picker-prev').addEventListener('click', function () {
        g_year_picker_decade_start -= 10;
        render_year_picker();
    });
    container.querySelector('.dsmr-picker-next').addEventListener('click', function () {
        g_year_picker_decade_start += 10;
        render_year_picker();
    });
    container.querySelectorAll('.dsmr-picker-cell[data-year]').forEach(function (cell) {
        cell.addEventListener('click', function () {
            g_selected_date = new Date(parseInt(this.getAttribute('data-year')), 0, 1);
            update_view(g_selected_date);
            render_year_picker();
        });
    });
}

/**
 * Shortcut for updating both XHR views.
 */
function update_view(selected_date) {
    update_summary(selected_date);
    update_graphs(selected_date);
}

/**
 * Updates the upper view, which is the summary table.
 */
function update_summary(selected_date) {
    $("#summary-loader").show();
    $("#summary-holder").hide();

    /* Prevent queueing multiple updates when a user clicks multiple selections too quickly. */
    if (summary_xhr_request !== null) {
        summary_xhr_request.abort();
    }

    summary_xhr_request = $.ajax({
        url: ARCHIVE_XHR_SUMMARY_URL,
        data: {
            'date': dayjs(selected_date).format(DATEPICKER_LOCALE_FORMAT.toUpperCase()),
            'level': g_datepicker_view_mode
        },
    }).done(function (data) {
        $("#summary-holder").html(data).show();
    }).always(function () {
        $("#summary-loader").hide();
        summary_xhr_request = null;
    });
}

/**
 * Updates the lower view, which are the graphs displayed.
 */
function update_graphs(selected_date) {
    /* Prevent queueing multiple updates when a user clicks multiple selections too quickly. */
    if (g_graph_xhr_request !== null) {
        g_graph_xhr_request.abort();
    }

    if (echarts_electricity_graph !== undefined) {
        echarts_electricity_graph?.showLoading('default', LOADING_OPTIONS)
        echarts_electricity_graph?.clear();
    }

    if (echarts_electricity_returned_graph !== undefined) {
        echarts_electricity_returned_graph?.showLoading('default', LOADING_OPTIONS)
        echarts_electricity_returned_graph?.clear();
    }

    if (echarts_gas_graph !== undefined) {
        echarts_gas_graph?.showLoading('default', LOADING_OPTIONS)
        echarts_gas_graph?.clear();
    }

    g_graph_xhr_request = $.ajax({
        url: ARCHIVE_XHR_GRAPHS_URL,
        dataType: "json",
        data: {
            'date': dayjs(selected_date).format(DATEPICKER_LOCALE_FORMAT.toUpperCase()),
            'level': g_datepicker_view_mode
        }
    }).done(function (response) {
        if (response.electricity) {
            render_electricity_graph(response.electricity);
        }

        if (response.electricity_returned) {
            render_electricity_returned_graph(response.electricity_returned);
        }

        if (response.gas) {
            render_gas_graph(response.gas);
        }
    }).always(function () {
        g_graph_xhr_request = null;
        $("#chart-loader").hide();
    });
}

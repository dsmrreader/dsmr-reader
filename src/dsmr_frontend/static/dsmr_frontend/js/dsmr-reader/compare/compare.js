let g_datepicker_view_mode = 'months';
let g_datepicker_selections = {};
let g_day_pickers = {};
let g_month_picker_year = {'1': null, '2': null};
let g_year_picker_decade_start = {'1': null, '2': null};


$(document).ready(function () {
    ['1', '2'].forEach(function (postfix) {
        g_day_pickers[postfix] = flatpickr("#datepicker" + postfix + "-day", {
            inline: true,
            defaultDate: datepicker_end_date,
            minDate: datepicker_start_date,
            maxDate: datepicker_end_date,
            dateFormat: "Y-m-d",
            locale: datepicker_language_code.startsWith('nl') ? 'nl' : 'default',
            onChange: function (selectedDates) {
                if (g_datepicker_view_mode !== 'days') {
                    return;
                }
                g_datepicker_selections[postfix] = selectedDates[0];
                update_summary();
            }
        });
    });

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
 * Shows the appropriate pickers for the current mode and resets selections.
 */
function switch_mode() {
    /* Reset selections so both dates must be re-chosen in the new mode. */
    g_datepicker_selections = {};

    $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
    $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

    var startDate = new Date(datepicker_start_date);
    var endDate = new Date(datepicker_end_date);

    ['1', '2'].forEach(function (postfix) {
        if (g_datepicker_view_mode === 'days') {
            g_day_pickers[postfix].calendarContainer.style.display = '';
            $('#datepicker' + postfix + '-month').hide();
            $('#datepicker' + postfix + '-year').hide();
        } else if (g_datepicker_view_mode === 'months') {
            g_day_pickers[postfix].calendarContainer.style.display = 'none';
            $('#datepicker' + postfix + '-month').show();
            $('#datepicker' + postfix + '-year').hide();

            if (!g_month_picker_year[postfix]) {
                g_month_picker_year[postfix] = endDate.getFullYear();
            }
            g_month_picker_year[postfix] = Math.max(startDate.getFullYear(),
                Math.min(endDate.getFullYear(), g_month_picker_year[postfix]));
            render_month_picker(postfix);
        } else {
            g_day_pickers[postfix].calendarContainer.style.display = 'none';
            $('#datepicker' + postfix + '-month').hide();
            $('#datepicker' + postfix + '-year').show();

            if (!g_year_picker_decade_start[postfix]) {
                g_year_picker_decade_start[postfix] = Math.floor(endDate.getFullYear() / 10) * 10;
            }
            render_year_picker(postfix);
        }
    });
}

/**
 * Renders the month-grid picker for the given postfix.
 */
function render_month_picker(postfix) {
    var startDate = new Date(datepicker_start_date);
    var endDate = new Date(datepicker_end_date);
    var year = g_month_picker_year[postfix];
    var locale = datepicker_language_code.startsWith('nl') ? 'nl-NL' : 'en-GB';

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

    document.getElementById('datepicker' + postfix + '-month').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + year + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker' + postfix + '-month');

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
            g_datepicker_selections[postfix] = new Date(
                g_month_picker_year[postfix], parseInt(this.getAttribute('data-month')), 1
            );
            update_summary();
            render_month_picker(postfix);
        });
    });
}

/**
 * Renders the year-grid picker for the given postfix.
 * Shows 12 years (decadeStart−1 … decadeStart+10) like Bootstrap Datepicker.
 */
function render_year_picker(postfix) {
    var startDate = new Date(datepicker_start_date);
    var endDate = new Date(datepicker_end_date);
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

    document.getElementById('datepicker' + postfix + '-year').innerHTML =
        '<div class="dsmr-picker">' +
        '<div class="dsmr-picker-nav">' +
        '<button class="dsmr-picker-prev"' + (prevDisabled ? ' disabled' : '') + '>&#8249;</button>' +
        '<span class="dsmr-picker-title">' + ds + '\u2013' + (ds + 9) + '</span>' +
        '<button class="dsmr-picker-next"' + (nextDisabled ? ' disabled' : '') + '>&#8250;</button>' +
        '</div>' +
        '<div class="dsmr-picker-grid">' + cells + '</div>' +
        '</div>';

    var container = document.getElementById('datepicker' + postfix + '-year');

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
            g_datepicker_selections[postfix] = new Date(
                parseInt(this.getAttribute('data-year')), 0, 1
            );
            update_summary();
            render_year_picker(postfix);
        });
    });
}

/**
 * Updates the summary table when both pickers have a selection.
 */
function update_summary() {
    if (!g_datepicker_selections['1'] || !g_datepicker_selections['2']) {
        return;
    }

    let base_selection = dayjs(g_datepicker_selections['1']).format(datepicker_locale_format.toUpperCase());
    let comparison_selection = dayjs(g_datepicker_selections['2']).format(datepicker_locale_format.toUpperCase());

    $("#summary-holder").hide();
    $("#summary-loader").show();

    $.ajax({
        url: compare_xhr_summary_url,
        data: {
            'base_date': base_selection,
            'comparison_date': comparison_selection,
            'level': g_datepicker_view_mode
        },
    }).done(function (data) {
        $("#summary-holder").html(data).show();
    }).always(function () {
        $("#summary-loader").hide();
    });
}

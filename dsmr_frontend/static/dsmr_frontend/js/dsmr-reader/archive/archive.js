var g_datepicker_view_mode = 'months';
var summary_xhr_request = null;
var g_graph_xhr_request = null;


$(document).ready(function () {
    initialize_datepicker();

    $("#datepicker_trigger_days").click(function () {
        g_datepicker_view_mode = 'days';
        initialize_datepicker()
    });

    $("#datepicker_trigger_months").click(function () {
        g_datepicker_view_mode = 'months';
        initialize_datepicker()
    });

    $("#datepicker_trigger_years").click(function () {
        g_datepicker_view_mode = 'years';
        initialize_datepicker()
    });
});

/**
 * Resets the datepicker. Required because options cannot be changed dynamically.
 */
function initialize_datepicker() {
    $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
    $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');

    if ($('#datepicker').children().length > 0) {
        /* Remove any previous events bound below. */
        $('#datepicker').off().datepicker('destroy');
    }

    $('#datepicker').datepicker({
        startView: g_datepicker_view_mode,
        minViewMode: g_datepicker_view_mode,
        maxViewMode: 'years',
        calendarWeeks: true,
        weekStart: 1,
        todayHighlight: true,
        startDate: datepicker_start_date,
        endDate: datepicker_end_date,
        format: datepicker_locale_format,
        language: datepicker_language_code
    }).on('changeDate', function (e) {
        if (g_datepicker_view_mode != 'days') {
            return;
        }
        update_view(e.date);

    }).on('changeMonth', function (e) {
        if (g_datepicker_view_mode != 'months') {
            return;
        }
        update_view(e.date);

    }).on('changeYear', function (e) {
        if (g_datepicker_view_mode != 'years') {
            return;
        }
        update_view(e.date);

    }).datepicker('update', datepicker_end_date);

    update_view($('#datepicker').datepicker('getDate'));
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
    if (summary_xhr_request) {
        summary_xhr_request.abort();
    }

    summary_xhr_request = $.ajax({
        url: archive_xhr_summary_url,
        data: {
            'date': moment(selected_date).format(datepicker_locale_format.toUpperCase()),
            'level': g_datepicker_view_mode
        },
    }).done(function (data) {
        summary_xhr_request = null;
        $("#summary-loader").hide();
        $("#summary-holder").html(data).show();
    });
}

/**
 * Updates the lower view, which are the graphs displayed.
 */
function update_graphs(selected_date) {
    /* Prevent queueing multiple updates when a user clicks multiple selections too quickly. */
    if (g_graph_xhr_request) {
        g_graph_xhr_request.abort();
    }

    g_graph_xhr_request = $.ajax({
        url: archive_xhr_graphs_url,
        dataType: "json",
        data: {
            'date': moment(selected_date).format(datepicker_locale_format.toUpperCase()),
            'level': g_datepicker_view_mode
        },
    }).done(function (response) {
        g_graph_xhr_request = null;
        $("#chart-loader").hide();

        if (response.electricity) {
            render_electricity_graph(response.electricity);
        }

        if (response.electricity_returned) {
            render_electricity_returned_graph(response.electricity_returned);
        }

        if (response.gas) {
            render_gas_graph(response.gas);
        }
    });
}

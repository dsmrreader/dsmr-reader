var g_datepicker_view_mode = 'months';
var g_datepicker_selections = [];


$(document).ready(function(){
    initialize_datepicker('1');
    initialize_datepicker('2');
    
    $("#datepicker_trigger_days").click(function(){
        g_datepicker_view_mode = 'days';
        initialize_datepicker('1')
        initialize_datepicker('2')
    });
    
    $("#datepicker_trigger_months").click(function(){
        g_datepicker_view_mode = 'months';
        initialize_datepicker('1')
        initialize_datepicker('2')
    });
    
    $("#datepicker_trigger_years").click(function(){
        g_datepicker_view_mode = 'years';
        initialize_datepicker('1')
        initialize_datepicker('2')
    });
});

/**
 * Resets the datepicker. Required because options cannot be changed dynamically.
 */
function initialize_datepicker(id_postfix)
{
	/* Reset selection. */
	g_datepicker_selections = [];
	
    $('.datepicker-trigger').removeClass('st-green').addClass('st-gray');
    $('#datepicker_trigger_' + g_datepicker_view_mode).removeClass('st-gray').addClass('st-green');
    
    if ($('#datepicker' + id_postfix).children().length > 0) 
    {
 		/* Remove any previous events bound below. */
 		$('#datepicker' + id_postfix).off().datepicker('remove');
    }
    
    $('#datepicker' + id_postfix).datepicker({
        startView: g_datepicker_view_mode,
        minViewMode: g_datepicker_view_mode,
        maxViewMode: 'years',
        calendarWeeks: true,
        todayHighlight: true,
        startDate: datepicker_start_date,
        endDate: datepicker_end_date,
        format: datepicker_locale_format,
        language: datepicker_language_code
    }).on('changeDate', function(e) {
        if (g_datepicker_view_mode != 'days')
        {
            return;
        }
        g_datepicker_selections[id_postfix] = e.date;
        update_summary();
        
    }).on('changeMonth', function(e) {
        if (g_datepicker_view_mode != 'months')
        {
            return;
        }
        g_datepicker_selections[id_postfix] = e.date;
        update_summary();
        
    }).on('changeYear', function(e) {
        if (g_datepicker_view_mode != 'years')
        {
            return;
        }
        g_datepicker_selections[id_postfix] = e.date;
        update_summary();
        
    });
}

/**
 * Updates the the summary table.
 */
function update_summary()
{
	if (! g_datepicker_selections[1] || ! g_datepicker_selections[2]) {
		return;
	}

	var base_selection = moment(g_datepicker_selections[1]).format(datepicker_locale_format.toUpperCase());
	var comparison_selection = moment(g_datepicker_selections[2]).format(datepicker_locale_format.toUpperCase());
	
    $("#summary-holder").hide();
	$("#summary-loader").show();
	
    $.ajax({
        url: compare_xhr_summary_url,
        data: {
            'base_date': base_selection,
            'comparison_date': comparison_selection,
            'level': g_datepicker_view_mode
        },
    }).done(function(data) {
        $("#summary-loader").hide();
        $("#summary-holder").html(data).show();
    });
}

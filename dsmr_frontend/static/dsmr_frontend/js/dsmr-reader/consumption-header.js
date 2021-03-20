function update_consumption_header(update_interval)
{
    $("#header-loader").show();

    $.ajax({
        dataType: "json",
        url: xhr_consumption_header_url,
    }).done(function(response) {
        $("#latest_timestamp").html(response.timestamp);
        $("#tariff_name").html(response.tariff_name);

        if (response.currently_returned > 0) {
            response.currently_returned = '-' + response.currently_returned;
        }

        $("#latest_electricity_delivered").html(response.currently_delivered);
        $("#latest_electricity_returned").html(response.currently_returned);

        if (response.cost_per_hour)
        {
            let cost_per_hour = response.cost_per_hour;

            // Weird edge case.
            if (cost_per_hour === '-0.00' || cost_per_hour === '-0,00') {
                cost_per_hour = '0.00';
            }

            $("#cost_per_hour").html(cost_per_hour).show();
        }
    }).always(function(){
        // Done (either way) reschedule next update.
        setTimeout(
            function(){ update_consumption_header(update_interval); },
            update_interval
        );

        $("#header-loader").hide();
    });
}
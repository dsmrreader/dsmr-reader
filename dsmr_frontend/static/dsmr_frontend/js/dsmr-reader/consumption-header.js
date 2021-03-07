function update_consumption_header()
{
    $("#header-loader").show();

    $.ajax({
        dataType: "json",
        url: xhr_consumption_header_url,
    }).done(function(response) {
        $("#header-loader").hide();
        $("#latest_timestamp").html(response.timestamp);
        $("#tariff_name").html(response.tariff_name);

        if (response.currently_returned > 0) {
            $("#latest_electricity").html('').hide();
            $("#latest_electricity_returned").html('-' + response.currently_returned).show();
        } else {
            $("#latest_electricity").html(response.currently_delivered).show();
            $("#latest_electricity_returned").html('').hide();
        }

        if (response.cost_per_hour)
        {
            let cost_per_hour = response.cost_per_hour;

            // Weird edge case.
            if (cost_per_hour === '-0.00' || cost_per_hour === '-0,00') {
                cost_per_hour = '0.00';
            }

            $("#cost_per_hour").html(cost_per_hour).show();
        }
    });
}
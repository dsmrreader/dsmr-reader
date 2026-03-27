function decimal_html(value)
{
    let text = String(value);

    if (typeof DECIMAL_SIZE_FORMATTING !== 'undefined' && !DECIMAL_SIZE_FORMATTING) {
        return text;
    }

    let dot_pos = text.lastIndexOf('.');
    let comma_pos = text.lastIndexOf(',');

    if (dot_pos === -1 && comma_pos === -1) {
        return text;
    }

    let sep_pos = Math.max(dot_pos, comma_pos);
    let sep = text[sep_pos];
    let integer_part = text.slice(0, sep_pos);
    let decimal_part = text.slice(sep_pos + 1);
    return integer_part + '<span class="badge-decimal">' + sep + decimal_part + '</span>';
}

function update_consumption_header(update_interval)
{
    $("#header-loader").show();

    $.ajax({
        dataType: "json",
        url: XHR_CONSUMPTION_HEADER_URL,
    }).done(function(response) {
        $("#latest_timestamp").html(response.timestamp);
        $("#tariff_name").html(response.tariff_name);

        if (response.currently_returned > 0) {
            response.currently_returned = response.currently_returned;
        }

        $("#latest_electricity_delivered").html(decimal_html(response.currently_delivered));
        $("#latest_electricity_returned").html(decimal_html(response.currently_returned));

        if (response.cost_per_hour)
        {
            let cost_per_hour = response.cost_per_hour;

            // Weird edge case.
            if (cost_per_hour === '-0.00' || cost_per_hour === '-0,00') {
                cost_per_hour = '0.00';
            }

            $("#cost_per_hour").html(decimal_html(cost_per_hour)).show();
        }
    }).always(function(){
        // Done (either way), reschedule next update.
        setTimeout(
            function(){ update_consumption_header(update_interval); },
            update_interval
        );

        $("#header-loader").hide();
    });
}
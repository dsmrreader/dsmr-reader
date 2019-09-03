$(document).ready(function(){
    $(".help-trigger").click(function(){
    	$(this).next().show();
        $(this).remove();
        return false;
    });
	
    $("#check_for_updates").click(function(){
        check_for_updates();
        return false;
    });

    setInterval(function(){ location.reload(); }, 10000);

});

function check_for_updates()
{
	$("#check_for_updates").hide();
    $("#loader").show();

    $.ajax({
        dataType: "json",
        url: status_update_url,
    }).done(function(response) {
        $("#loader").hide();

        if (response.update_available)
        {
        	$("#update_available").show();
        }
        else
    	{
        	$("#no_update_available").show();
    	}
    });
}
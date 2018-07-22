$('a').click(function(event) {
    // When DSMR Reader is ran as a standalone iOS Web App, prevent links targetting the same window from being opened externally.
    if (navigator.standalone === true && $(this).attr('target') !== '_blank') {
        event.preventDefault();
        location.href = $(this).attr('href');
    }
});
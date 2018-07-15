$(document).ready(function(){
	var echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));
    var echarts_electricity_initial_options = {
        color: [electricity_delivered_color, electricity_returned_color],
    	tooltip : {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
                label: {
                    show: true
                }
            }
        },
        calculable : true,
        grid: {
            top: '12%',
            left: '1%',
            right: '1%',
            containLabel: true
        },
        xAxis: [
            {
                type : 'category',
                data : null
            }
        ],
        yAxis: [
            {
                type : 'value',
            }
        ],
        dataZoom: [
            {
                show: true,
                start: 0,
                end: 100
            },
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
    };
	
    /* These settings should not affect the updates and reset the zoom on each update. */
    var echarts_electricity_update_options = {
        xAxis: [
            {
                type : 'category',
                data : null
            }
        ],
        series : [
            {
            	smooth: true,
                name: 'Watt (+)',
                type: 'line',
                areaStyle: {},
                stack: 'dummy',
                data: null
            },
            {
            	smooth: true,
                name: 'Watt (-)',
                type: 'line',
                areaStyle: {},
                stack: 'dummy',
                data: null
            }
        ]
    };
	
	
	echarts_electricity_graph.showLoading();
	
	/* Init graph. */
	$.get(echarts_electricity_graph_url, function (xhr_data) {
	    echarts_electricity_graph.hideLoading();

	    /* Adjust default zooming to the number of default items we want to display. */
	    var zoom_percent = 100 - (dashboard_graph_width / xhr_data.read_at.length * 100);
	    echarts_electricity_initial_options.dataZoom[0].start = zoom_percent;
	    echarts_electricity_graph.setOption(echarts_electricity_initial_options);

	    /* Different set of options, to prevent the dataZoom being reset on each update. */
	    echarts_electricity_update_options.xAxis[0].data = xhr_data.read_at;
	    echarts_electricity_update_options.series[0].data = xhr_data.currently_delivered;
	    echarts_electricity_update_options.series[1].data = xhr_data.currently_returned;
		echarts_electricity_graph.setOption(echarts_electricity_update_options);
		
		var latest_delta_id = xhr_data.latest_delta_id;
		
		/* Update graph data from now on. */
		setInterval(function () {

			$.get(echarts_electricity_graph_url + "&latest_delta_id=" + latest_delta_id, function (xhr_data) {
				/* Ignore empty sets. */
				if (xhr_data.read_at.length == 0)
				{
					return;
				}
				
			    /* Delta update. */
				for (var i = 0 ; i < xhr_data.read_at.length ; i++)
				{
					echarts_electricity_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
					echarts_electricity_update_options.series[0].data.push(xhr_data.currently_delivered[i]);
					echarts_electricity_update_options.series[1].data.push(xhr_data.currently_returned[i]);
				}
				
				latest_delta_id = xhr_data.latest_delta_id;
				echarts_electricity_graph.setOption(echarts_electricity_update_options);
			});
		}, echarts_electricity_graph_interval * 1000);
	});
	
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_electricity_graph.resize();
	});
});
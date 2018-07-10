$(document).ready(function(){
	
	var echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));
    var echarts_electricity_options = {
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
	
		echarts_electricity_options.dataZoom[0].start = zoom_percent;
		echarts_electricity_options.xAxis[0].data = xhr_data.read_at;
		echarts_electricity_options.series[0].data = xhr_data.currently_delivered;
		echarts_electricity_options.series[1].data = xhr_data.currently_returned;

	    echarts_electricity_graph.setOption(echarts_electricity_options);
	});
	
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_electricity_graph.resize();
	});
	
	/* Update graph data. */
	setInterval(function () {
		$.get(echarts_electricity_graph_url, function (xhr_data) {
			
			echarts_electricity_options.xAxis[0].data = xhr_data.read_at;
			echarts_electricity_options.series[0].data = xhr_data.currently_delivered;
			echarts_electricity_options.series[1].data = xhr_data.currently_returned;

			echarts_electricity_graph.setOption(echarts_electricity_options);
		});
	}, echarts_electricity_graph_interval * 1000);
});
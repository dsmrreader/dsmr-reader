$(document).ready(function(){
	
	var echarts_voltage_graph = echarts.init(document.getElementById('echarts-voltage-graph'));
    var echarts_voltage_initial_options = {
        color: [
        	voltage_l1_color,
        	voltage_l2_color,
        	voltage_l3_color
        ],
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
            right: '2%',
            containLabel: true
        },
        xAxis: [
            {
                type : 'category',
                boundaryGap: false,
                data : null
            }
        ],
        yAxis: [
            {
                type : 'value'
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
    var echarts_voltage_update_options = {
        xAxis: [
            {
                type : 'category',
                boundaryGap: false,
                data : null
            }
        ],
        series : [
            {
            	smooth: true,
                name: 'Volt (L1)',
                type: 'line',
                data: null
            },
            {
            	smooth: true,
                name: 'Volt (L2)',
                type: 'line',
                data: null
            },
            {
            	smooth: true,
                name: 'Volt (L3)',
                type: 'line',
                data: null
            },
        ]
    };
	
	echarts_voltage_graph.showLoading('default', echarts_loading_options);
	
	/* Init graph. */
	$.get(echarts_voltage_graph_url, function (xhr_data) {
	    echarts_voltage_graph.hideLoading();
	    
	    /* Adjust default zooming to the number of default items we want to display. */
	    var zoom_percent = 100 - (dashboard_graph_width / xhr_data.read_at.length * 100);
	    echarts_voltage_initial_options.dataZoom[0].start = zoom_percent;
	    echarts_voltage_graph.setOption(echarts_voltage_initial_options);

	    /* Different set of options, to prevent the dataZoom being reset on each update. */
	    echarts_voltage_update_options.xAxis[0].data = xhr_data.read_at;
	    echarts_voltage_update_options.series[0].data = xhr_data.phase_voltage.l1;
	    echarts_voltage_update_options.series[1].data = xhr_data.phase_voltage.l2;
	    echarts_voltage_update_options.series[2].data = xhr_data.phase_voltage.l3;
	    echarts_voltage_graph.setOption(echarts_voltage_update_options);
	    
	    var latest_delta_id = xhr_data.latest_delta_id;

		/* Update graph data from now on. */
	    setInterval(function () {
			$.get(echarts_voltage_graph_url + "&latest_delta_id=" + latest_delta_id, function (xhr_data) {
				/* Ignore empty sets. */
				if (xhr_data.read_at.length == 0)
				{
					return;
				}

				/* Delta update. */
				for (var i = 0 ; i < xhr_data.read_at.length ; i++)
				{
					echarts_voltage_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
					echarts_voltage_update_options.series[0].data.push(xhr_data.phase_voltage.l1[i]);
					echarts_voltage_update_options.series[1].data.push(xhr_data.phase_voltage.l2[i]);
					echarts_voltage_update_options.series[2].data.push(xhr_data.phase_voltage.l3[i]);
				}
				
				latest_delta_id = xhr_data.latest_delta_id;
	    		echarts_voltage_graph.setOption(echarts_voltage_update_options);
	    	});
	    }, echarts_voltage_graph_interval * 1000);
	});
	
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_voltage_graph.resize();
	});
});

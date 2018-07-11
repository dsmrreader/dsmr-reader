$(document).ready(function(){
	
	var echarts_phases_graph = echarts.init(document.getElementById('echarts-phases-graph'));
    var echarts_phases_options = {
        color: [phase_delivered_l1_color, phase_delivered_l2_color, phase_delivered_l3_color],
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
                name: 'Watt (L1)',
                type: 'line',
                areaStyle: {},
                stack: 'dummy',
                data: null
            },
            {
            	smooth: true,
                name: 'Watt (L2)',
                type: 'line',
                areaStyle: {},
                stack: 'dummy',
                data: null
            },
            {
            	smooth: true,
                name: 'Watt (L3)',
                type: 'line',
                areaStyle: {},
                stack: 'dummy',
                data: null
            }
        ]
    };
	
	echarts_phases_graph.showLoading();
	
	/* Init graph. */
	$.get(echarts_phases_graph_url, function (xhr_data) {
	    echarts_phases_graph.hideLoading();
	    
	    /* Adjust default zooming to the number of default items we want to display. */
	    var zoom_percent = 100 - (dashboard_graph_width / xhr_data.read_at.length * 100);
	
	    echarts_phases_options.dataZoom[0].start = zoom_percent;
	    echarts_phases_options.xAxis[0].data = xhr_data.read_at;
	    echarts_phases_options.series[0].data = xhr_data.phases.l1;
	    echarts_phases_options.series[1].data = xhr_data.phases.l2;
	    echarts_phases_options.series[2].data = xhr_data.phases.l3;

	    echarts_phases_graph.setOption(echarts_phases_options);
	});
	
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_phases_graph.resize();
	});
	
	/* Update graph data. */
	setInterval(function () {
		$.get(echarts_phases_graph_url, function (xhr_data) {
			
			echarts_phases_options.xAxis[0].data = xhr_data.read_at;
		    echarts_phases_options.series[0].data = xhr_data.phases.l1;
		    echarts_phases_options.series[1].data = xhr_data.phases.l2;
		    echarts_phases_options.series[2].data = xhr_data.phases.l3;

		    echarts_phases_graph.setOption(echarts_phases_options);
		});
	}, echarts_phases_graph_interval * 1000);
});
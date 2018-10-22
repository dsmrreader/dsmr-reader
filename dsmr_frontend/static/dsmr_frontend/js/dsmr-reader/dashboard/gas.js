$(document).ready(function(){
	
	var echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));
	echarts_gas_graph.showLoading('default', echarts_loading_options);
	
	/* Init graph. */
	$.get(echarts_gas_graph_url, function (xhr_data) {
	    echarts_gas_graph.hideLoading();

	    /* Adjust default zooming to the number of default items we want to display. */
	    var zoom_percent = 100 - (dashboard_graph_width / xhr_data.read_at.length * 100);
	
	    var option = {
	        color: [gas_delivered_color],
	        tooltip : {
	            trigger: 'axis',
	            formatter: "{c} {a}",
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
	                data : xhr_data.read_at
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
	                start: zoom_percent,
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
	                name: 'm³',
	                type: 'line',
	                areaStyle: {},
	                data: xhr_data.currently_delivered,
	                smooth: true
	            }
	        ]
	    };
	    echarts_gas_graph.setOption(option);
	});
	
	/* Responsiveness. */
	$(window).resize(function() {
    	echarts_gas_graph.resize();
    });
});
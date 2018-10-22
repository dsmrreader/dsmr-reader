var echarts_electricity_returned_graph = echarts.init(document.getElementById('echarts-electricity-returned-graph'));


$(document).ready(function(){
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_electricity_returned_graph.resize();
	});
});
	

function render_electricity_returned_graph(xhr_data)
{
    var echarts_options = {
	    title: {
	        text: text_electricity_returned_header,
	        left: 'center'
	    },
        color: [
        	electricity_returned_color,
        	electricity_returned_alternate_color,
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
            right: '1%',
            containLabel: true
        },
        xAxis: [
            {
                type : 'category',
                data : xhr_data.x
            }
        ],
        yAxis: [
            {
                type : 'value'
            }
        ],
        series: null
    };
    
    if (xhr_data.electricity1_returned && xhr_data.electricity2_returned)
	{
    	echarts_options.series = [
            {
            	smooth: true,
                name: text_electricity1_returned,
                type: 'line',
                areaStyle: {},
                data: xhr_data.electricity1_returned
            },
            {
            	smooth: true,
                name: text_electricity2_returned,
                type: 'line',
                areaStyle: {},
                data: xhr_data.electricity2_returned
            }
        ]
	}
    else if (xhr_data.electricity_returned_merged)
	{
    	echarts_options.series = [
            {
            	smooth: true,
                name: text_electricity_merged_returned,
                type: 'line',
                areaStyle: {},
                data: xhr_data.electricity_returned_merged
            }
        ]
	}
	
	echarts_electricity_returned_graph.setOption(echarts_options);
}

var echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));


$(document).ready(function(){
	/* Responsiveness. */
	$(window).resize(function() {
		echarts_gas_graph.resize();
	});
});
	

function render_gas_graph(xhr_data)
{
    var echarts_options = {
	    title: {
	        text: text_gas_header,
	        left: 'center'
	    },
        color: [
        	gas_delivered_color
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
                boundaryGap: gas_graph_style == 'bar',
                data : xhr_data.x
            }
        ],
        yAxis: [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name: text_gas,
                type: gas_graph_style,
                smooth: true,
                areaStyle: {},
                data: xhr_data.gas
            }
        ]
    };
	
	echarts_gas_graph.setOption(echarts_options);
}

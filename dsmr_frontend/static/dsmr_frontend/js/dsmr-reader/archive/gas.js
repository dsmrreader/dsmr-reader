let echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));


$(window).resize(function () {
    echarts_gas_graph?.resize();
});


function render_gas_graph(xhr_data) {
    let echarts_options = {
        toolbox: TOOLBOX_OPTIONS,
        title: {
            text: TEXT_GAS_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center'
        },
        color: [
            GAS_DELIVERED_COLOR
        ],
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
                label: {
                    show: true
                }
            }
        },
        calculable: true,
        grid: {
            top: '12%',
            left: '1%',
            right: '2%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: GAS_GRAPH_STYLE === 'bar',
                data: xhr_data.x
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: TEXT_GAS,
                type: GAS_GRAPH_STYLE,
                smooth: true,
                areaStyle: {},
                data: xhr_data.gas
            }
        ]
    };

    echarts_gas_graph.hideLoading()
    echarts_gas_graph.setOption(echarts_options);
}

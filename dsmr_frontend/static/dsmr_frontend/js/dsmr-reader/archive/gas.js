echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));


$(window).resize(function () {
    echarts_gas_graph?.resize();
});


function render_gas_graph(xhr_data) {
    let animationDelay = function (idx) {
        return idx * 10;
    };
    let echarts_options = {
        title: {
            text: TEXT_GAS_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center'
        },
        color: [
            GAS_DELIVERED_COLOR
        ],
        tooltip: TOOLTIP_OPTIONS,
        calculable: true,
        grid: GRID_OPTIONS,
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
                animationDelay: animationDelay,
                data: xhr_data.gas
            }
        ],
        animationEasing: 'elasticOut',
        media: [
            {
              option: {
                    toolbox: TOOLBOX_OPTIONS
                },
            },
            {
                query: { maxWidth: 500},
                option: {
                    toolbox: {show: false}
                }
            }
        ]
    };

    echarts_gas_graph.hideLoading()
    echarts_gas_graph.setOption(echarts_options);
}

$(document).ready(function () {
    echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));
    echarts_gas_graph.showLoading('default', LOADING_OPTIONS);

    /* Init graph. */
    $.get(GAS_GRAPH_URL, function (xhr_data) {
        echarts_gas_graph.hideLoading();

        let option = {
            color: [
                GAS_DELIVERED_COLOR
            ],
            title: {
                text: TEXT_GAS_HEADER,
                textStyle: TITLE_TEXTSTYLE_OPTIONS,
                left: 'center',
            },
            tooltip: TOOLTIP_OPTIONS,
            calculable: true,
            grid: GRID_OPTIONS,
            xAxis: [
                {
                    type: 'category',
                    boundaryGap: GAS_GRAPH_STYLE === 'bar',
                    data: xhr_data.read_at,
                    axisLabel: {
                        color: TEXTSTYLE_COLOR
                    }
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    axisLabel: {
                        color: TEXTSTYLE_COLOR,
                        formatter: '{value} m³'
                    }
                }
            ],
            dataZoom: [
                {
                    show: true,
                    // Do not change initial zoom when using a non DSMR v5 meter.
                    // Because it will cause DSMR v4 meter users to only display 2 of 24 hours by default.
                    start: TELEGRAM_DSMR_VERSION === '50' ? LIVE_GRAPHS_INITIAL_ZOOM : 0,
                    end: 100,
                    textStyle: {
                        color: TEXTSTYLE_COLOR
                    }
                },
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                }
            ],
            series: [
                {
                    name: 'm³',
                    type: GAS_GRAPH_STYLE,
                    areaStyle: {},
                    emphasis: EMPHASIS_STYLE_OPTIONS,
                    data: xhr_data.currently_delivered,
                    smooth: true
                }
            ],
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
        echarts_gas_graph.setOption(option);
    });
});

$(window).resize(function () {
    echarts_gas_graph?.resize();
});
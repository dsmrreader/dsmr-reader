$(document).ready(function () {
    echarts_electricity_peaks_graph = echarts.init(document.getElementById('echarts-electricity-peaks-graph'));
    echarts_electricity_peaks_graph.showLoading('default', LOADING_OPTIONS);

    /* Init graph. */
    $.get(ELECTRICITY_PEAKS_GRAPH_URL, function (xhr_data) {
        echarts_electricity_peaks_graph.hideLoading();

        let option = {
            color: [
                ELECTRICITY_PEAKS_COLOR
            ],
            title: {
                text: TEXT_ELECTRICITY_PEAKS_HEADER,
                textStyle: TITLE_TEXTSTYLE_OPTIONS,
                left: 'center',
            },
            tooltip: TOOLTIP_OPTIONS,
            calculable: true,
            grid: GRID_OPTIONS,
            xAxis: [
                {
                    type: 'category',
                    boundaryGap: false,
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
                        formatter: '{value} ' + TEXT_KW15M
                    }
                }
            ],
            dataZoom: [
                {
                    show: true,
                    start: LIVE_GRAPHS_INITIAL_ZOOM,
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
                    name: TEXT_KW15M,
                    type: 'line',
                    areaStyle: {},
                    emphasis: EMPHASIS_STYLE_OPTIONS,
                    data: xhr_data.average_delivered,
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
        echarts_electricity_peaks_graph.setOption(option);
    });
});

$(window).resize(function () {
    echarts_electricity_peaks_graph?.resize();
});
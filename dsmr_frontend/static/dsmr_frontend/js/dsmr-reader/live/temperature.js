$(document).ready(function () {
    echarts_temperature_graph = echarts.init(document.getElementById('echarts-temperature-graph'));
    echarts_temperature_graph.showLoading('default', LOADING_OPTIONS);

    /* Init graph. */
    $.get(TEMPERATURE_GRAPH_URL, function (xhr_data) {
        echarts_temperature_graph.hideLoading();

        let option = {
            color: [
                TEMPERATURE_COLOR
            ],
            title: {
                text: TEXT_TEMPERATURE_HEADER,
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
                    data: xhr_data.read_at
                }
            ],
            yAxis: [
                {
                    type: 'value'
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
            series: [
                {
                    name: '°C',
                    type: 'line',
                    areaStyle: {},
                    data: xhr_data.degrees_celcius,
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
        echarts_temperature_graph.setOption(option);
    });
});

$(window).resize(function () {
    echarts_temperature_graph?.resize();
});
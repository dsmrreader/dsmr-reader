let echarts_avg_electricity_graph = null;
let echarts_avg_electricity_returned_graph = null;
let echarts_avg_gas_graph = null;

function update_trends_averages(start_date, end_date) {
    let echarts_options = {
        title: {
            text: 'null',
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
        tooltip: TOOLTIP_OPTIONS,
        xAxis: [
            {
                type: 'category',
                boundaryGap: ELECTRICITY_GRAPH_STYLE === 'bar',
                data: null,
                axisLabel: {
                    color: TEXTSTYLE_COLOR,
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                axisLabel: {
                    color: TEXTSTYLE_COLOR
                }
            }
        ],
        series: null,
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

    echarts_avg_electricity_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_electricity_graph?.clear();
    echarts_avg_electricity_returned_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_electricity_returned_graph?.clear();
    echarts_avg_gas_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_gas_graph?.clear();

    $.ajax({
        url: AVG_CONSUMPTION_URL,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).fail(function (xhr_data) {
        echarts_avg_electricity_graph?.showLoading('default', {text: '❌ ' + xhr_data.responseText});
        echarts_avg_electricity_returned_graph?.showLoading('default', {text: '❌ ' + xhr_data.responseText});
        echarts_avg_gas_graph?.showLoading('default', {text: '❌ ' + xhr_data.responseText});
    }).done(function (xhr_data) {
        echarts_options.xAxis[0].data = xhr_data.hour_start;
        echarts_options.color = [ELECTRICITY_DELIVERED_COLOR];
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY_CONSUMED_TOOLTIP,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                showBackground: true,
                backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                emphasis: EMPHASIS_STYLE_OPTIONS,
                smooth: true,
                areaStyle: {},
                data: xhr_data.avg_electricity
            }
        ]

        echarts_options.title.text = TEXT_ELECTRICITY_CONSUMED_HEADER;
        echarts_avg_electricity_graph?.setOption(echarts_options);
        echarts_avg_electricity_graph?.hideLoading();

        if (xhr_data.avg_electricity_returned.length > 0) {
            echarts_options.color = [ELECTRICITY_RETURNED_COLOR];
            echarts_options.series = [
                {
                    name: TEXT_ELECTRICITY_RETURNED_TOOLTIP,
                    type: ELECTRICITY_GRAPH_STYLE,
                    stack: STACK_ELECTRICITY_GRAPHS,
                    animationDelay: ANIMATION_DELAY_OPTIONS,
                    showBackground: true,
                    backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                    emphasis: EMPHASIS_STYLE_OPTIONS,
                    smooth: true,
                    areaStyle: {},
                    data: xhr_data.avg_electricity_returned
                }
            ]
            echarts_options.title.text = TEXT_ELECTRICITY_RETURNED_HEADER;
            echarts_avg_electricity_returned_graph?.setOption(echarts_options);
            echarts_avg_electricity_returned_graph?.hideLoading();
        }

        if (xhr_data.avg_gas.length > 0) {
            echarts_options.color = [GAS_DELIVERED_COLOR];
            echarts_options.series = [
                {
                    name: TEXT_GAS_CONSUMED_TOOLTIP,
                    type: ELECTRICITY_GRAPH_STYLE,
                    animationDelay: ANIMATION_DELAY_OPTIONS,
                    showBackground: true,
                    backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                    emphasis: EMPHASIS_STYLE_OPTIONS,
                    smooth: true,
                    areaStyle: {},
                    data: xhr_data.avg_gas
                }
            ]
            echarts_options.title.text = TEXT_GAS_CONSUMED_HEADER;
            echarts_avg_gas_graph?.setOption(echarts_options);
            echarts_avg_gas_graph?.hideLoading();
        }
    });
}

$(window).resize(function () {
    echarts_avg_electricity_graph?.resize();
    echarts_avg_electricity_returned_graph?.resize();
    echarts_avg_gas_graph?.resize();
});

$(document).ready(function () {
    if ($('#echarts-avg-electricity-graph').length > 0) {
        echarts_avg_electricity_graph = echarts.init(document.getElementById('echarts-avg-electricity-graph'));
    }

    if ($('#echarts-avg-electricity-returned-graph').length > 0) {
        echarts_avg_electricity_returned_graph = echarts.init(document.getElementById('echarts-avg-electricity-returned-graph'));
    }

    if ($('#echarts-avg-gas-graph').length > 0) {
        echarts_avg_gas_graph = echarts.init(document.getElementById('echarts-avg-gas-graph'));
    }

    update_trends();
});

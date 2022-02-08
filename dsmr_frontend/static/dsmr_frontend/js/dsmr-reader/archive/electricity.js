echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));


$(window).resize(function () {
    echarts_electricity_graph?.resize();
});


function render_electricity_graph(xhr_data) {
    let echarts_options = {
        title: {
            text: TEXT_ELECTRICITY_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
        color: [
            ELECTRICITY_DELIVERED_ALTERNATE_COLOR,
            ELECTRICITY_DELIVERED_COLOR
        ],
        tooltip: TOOLTIP_OPTIONS,
        calculable: true,
        grid: GRID_OPTIONS,
        xAxis: [
            {
                type: 'category',
                boundaryGap: ELECTRICITY_GRAPH_STYLE === 'bar',
                data: xhr_data.x,
                axisLabel: {
                    color: TEXTSTYLE_COLOR
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

    if (xhr_data.electricity1 && xhr_data.electricity2) {
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY1_DELIVERED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                smooth: true,
                areaStyle: {},
                data: xhr_data.electricity1
            },
            {
                name: TEXT_ELECTRICITY2_DELIVERED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                smooth: true,
                areaStyle: {},
                data: xhr_data.electricity2
            }
        ]
    } else if (xhr_data.electricity_merged) {
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY_MERGED_DELIVERED,
                type: ELECTRICITY_GRAPH_STYLE,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                smooth: true,
                areaStyle: {},
                data: xhr_data.electricity_merged
            }
        ]
    }

    echarts_electricity_graph.hideLoading();
    echarts_electricity_graph.setOption(echarts_options);
}

echarts_electricity_returned_graph = echarts.init(document.getElementById('echarts-electricity-returned-graph'));


$(window).resize(function () {
    echarts_electricity_returned_graph?.resize();
});


function render_electricity_returned_graph(xhr_data) {
    let echarts_options = {
        title: {
            text: TEXT_ELECTRICITY_RETURNED_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center'
        },
        color: [
            ELECTRICITY_RETURNED_ALTERNATE_COLOR,
            ELECTRICITY_RETURNED_COLOR
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

    if (xhr_data.electricity1_returned && xhr_data.electricity2_returned) {
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY1_RETURNED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                showBackground: true,
                backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                smooth: true,
                areaStyle: {},
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: xhr_data.electricity1_returned
            },
            {
                name: TEXT_ELECTRICITY2_RETURNED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                showBackground: true,
                backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                smooth: true,
                areaStyle: {},
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: xhr_data.electricity2_returned
            }
        ]
    } else if (xhr_data.electricity_returned_merged) {
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY_MERGED_RETURNED,
                type: ELECTRICITY_GRAPH_STYLE,
                animationDelay: ANIMATION_DELAY_OPTIONS,
                showBackground: true,
                backgroundStyle: BACKGROUND_STYLE_OPTIONS,
                smooth: true,
                areaStyle: {},
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: xhr_data.electricity_returned_merged
            }
        ]
    }

    echarts_electricity_returned_graph?.hideLoading()
    echarts_electricity_returned_graph?.setOption(echarts_options);
}

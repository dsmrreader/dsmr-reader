let echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));


$(window).resize(function () {
    echarts_electricity_graph?.resize();
});


function render_electricity_graph(xhr_data) {
    let echarts_options = {
        toolbox: TOOLBOX_OPTIONS,
        title: {
            text: TEXT_ELECTRICITY_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
        color: [
            ELECTRICITY_DELIVERED_ALTERNATE_COLOR,
            ELECTRICITY_DELIVERED_COLOR
        ],
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
                label: {
                    normal: {
                        show: true,
                        position: 'top',
                        formatter: function (params) {
                            let val = 0;
                            this.option.series.forEach(s => {
                                val += s.data[params.dataIndex];
                            });
                            return val;
                        }
                    }
                },
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
                boundaryGap: ELECTRICITY_GRAPH_STYLE === 'bar',
                data: xhr_data.x
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: null
    };

    if (xhr_data.electricity1 && xhr_data.electricity2) {
        echarts_options.series = [
            {
                name: TEXT_ELECTRICITY1_DELIVERED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
                smooth: true,
                areaStyle: {},
                data: xhr_data.electricity1
            },
            {
                name: TEXT_ELECTRICITY2_DELIVERED,
                type: ELECTRICITY_GRAPH_STYLE,
                stack: STACK_ELECTRICITY_GRAPHS,
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
                smooth: true,
                areaStyle: {},
                data: xhr_data.electricity_merged
            }
        ]
    }

    echarts_electricity_graph.hideLoading();
    echarts_electricity_graph.setOption(echarts_options);
}

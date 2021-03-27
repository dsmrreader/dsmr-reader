$(document).ready(function () {
    echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));

    let x_axis = [
        {
            type: 'category',
            boundaryGap: false,
            data: []
        },
        {
            // We need this axis for rendering the return graph but hide it, since it's redunant.
            show: false,
            gridIndex: 1,
            boundaryGap: false,
            data: []
        }
    ];
    let echarts_electricity_initial_options = {
        color: [
            ELECTRICITY_DELIVERED_COLOR,
            ELECTRICITY_RETURNED_COLOR
        ],
        title: {
            text: TEXT_ELECTRICITY_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
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
        grid: [{
            left: 50,
            right: 50,
            height: '35%'
        }, {
            left: 50,
            right: 50,
            height: '35%',
            top: '50%'
        }],
        axisPointer: {
            link: {xAxisIndex: 'all'}
        },
        xAxis: x_axis,
        yAxis: [
            {
                type: 'value'
            },
            {
                gridIndex: 1,
                type: 'value',
                inverse: true
            }
        ],
        dataZoom: [
            {
                xAxisIndex: [0, 1],
                show: true,
                start: LIVE_GRAPHS_INITIAL_ZOOM,
                end: 100
            },
            {
                xAxisIndex: [0, 1],
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
        media: [
            {
              option: {
                    toolbox: TOOLBOX_OPTIONS,
                    grid: [{}, {
                        top: '50%'
                    }],
                },
            },
            {
                query: { maxWidth: 768},
                option: {
                    toolbox: {show: false},
                    grid: [{}, {
                        top: '55%'
                    }],
                }
            }
        ],
    };

    /* These settings should not affect the updates and reset the zoom on each update. */
    let echarts_electricity_update_options = {
        xAxis: x_axis,
        series: [
            {
                label: {
                    formatter: '{b}: {c}'
                },
                name: TEXT_DELIVERED,
                type: 'line',
                smooth: true,
                areaStyle: {},
                data: []
            },
            {
                xAxisIndex: 1,
                yAxisIndex: 1,
                name: TEXT_RETURNED,
                type: 'line',
                smooth: true,
                areaStyle: {},
                data: []
            }
        ],
    };

    echarts_electricity_graph.showLoading('default', LOADING_OPTIONS);

    $.get(ELECTRICITY_GRAPH_URL, function (xhr_data) {
        if (! CAPABILITY_ELECTRICITY_RETURNED) {
            delete echarts_electricity_initial_options.xAxis[1];
            delete echarts_electricity_initial_options.yAxis[1];
            delete echarts_electricity_initial_options.dataZoom[0].xAxisIndex;
            delete echarts_electricity_initial_options.dataZoom[1].xAxisIndex;
            delete echarts_electricity_initial_options.grid[0].height;
            delete echarts_electricity_initial_options.grid[1];
            echarts_electricity_initial_options.grid[0].top = '12%';

            delete echarts_electricity_update_options.xAxis[1];
            delete echarts_electricity_update_options.series[1];
        }

        echarts_electricity_graph.hideLoading();
        echarts_electricity_graph.setOption(echarts_electricity_initial_options);

        echarts_electricity_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_electricity_update_options.series[0].data = xhr_data.currently_delivered;

        if (CAPABILITY_ELECTRICITY_RETURNED) {
            echarts_electricity_update_options.xAxis[1].data = xhr_data.read_at;
            echarts_electricity_update_options.series[1].data = xhr_data.currently_returned;
        }

        echarts_electricity_graph.setOption(echarts_electricity_update_options);

        // Schedule updates
        let latest_delta_id = xhr_data.latest_delta_id;
        let pending_xhr_request = null;

        setInterval(function(){
            // Do not send new XHR request update if the previous one is still pending.
            if (pending_xhr_request !== null) {
                return;
            }

            pending_xhr_request = $.ajax({
                dataType: "json",
                url: ELECTRICITY_GRAPH_URL + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                echarts_electricity_update_options.xAxis[0].data = echarts_electricity_update_options.xAxis[0].data.concat(xhr_data.read_at)
                echarts_electricity_update_options.series[0].data = echarts_electricity_update_options.series[0].data.concat(xhr_data.currently_delivered);

                if (CAPABILITY_ELECTRICITY_RETURNED) {
                    echarts_electricity_update_options.xAxis[1].data = echarts_electricity_update_options.xAxis[1].data.concat(xhr_data.read_at)
                    echarts_electricity_update_options.series[1].data = echarts_electricity_update_options.series[1].data.concat(xhr_data.currently_returned);
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_electricity_graph.setOption(echarts_electricity_update_options);
            }).always(function(){
                // Allow new updates
                pending_xhr_request = null;
            });
        }, ELECTRICITY_GRAPH_INTERVAL * 1000);
    });
});

$(window).resize(function () {
    echarts_electricity_graph?.resize();
});
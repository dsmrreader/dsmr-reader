$(document).ready(function () {
    echarts_phases_graph = echarts.init(document.getElementById('echarts-phases-graph'));

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
    let echarts_phases_initial_options = {
        color: [
            PHASE_DELIVERED_L1_COLOR,
            PHASE_DELIVERED_L2_COLOR,
            PHASE_DELIVERED_L3_COLOR,
            PHASE_RETURNED_L1_COLOR,
            PHASE_RETURNED_L2_COLOR,
            PHASE_RETURNED_L3_COLOR
        ],
        title: {
            text: TEXT_PHASES_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
        tooltip: TOOLTIP_OPTIONS,
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
        ]
    };

    /* These settings should not affect the updates and reset the zoom on each update. */
    let echarts_phases_update_options = {
        xAxis: x_axis,
        series: [
            {
                yAxisIndex: 0,
                name: 'L1+',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: []
            },
            {
                yAxisIndex: 0,
                name: 'L2+',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: []
            },
            {
                yAxisIndex: 0,
                name: 'L3+',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: []
            },
            {
                xAxisIndex: 1,
                yAxisIndex: 1,
                name: 'L1-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: []
            },
            {
                xAxisIndex: 1,
                yAxisIndex: 1,
                name: 'L2-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: []
            },
            {
                xAxisIndex: 1,
                yAxisIndex: 1,
                name: 'L3-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: []
            }
        ]
    };

    echarts_phases_graph.showLoading('default', LOADING_OPTIONS);

    $.get(PHASES_GRAPH_URL, function (xhr_data) {
        if (! CAPABILITY_ELECTRICITY_RETURNED) {
            delete echarts_phases_initial_options.xAxis[1];
            delete echarts_phases_initial_options.yAxis[1];
            delete echarts_phases_initial_options.dataZoom[0].xAxisIndex;
            delete echarts_phases_initial_options.dataZoom[1].xAxisIndex;
            delete echarts_phases_initial_options.grid[0].height;
            delete echarts_phases_initial_options.grid[1];
            echarts_phases_initial_options.grid[0].top = '12%';

            delete echarts_phases_update_options.xAxis[1];
            delete echarts_phases_update_options.series[3];
            delete echarts_phases_update_options.series[4];
            delete echarts_phases_update_options.series[5];
        }

        echarts_phases_graph.hideLoading();
        echarts_phases_graph.setOption(echarts_phases_initial_options);

        echarts_phases_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_phases_update_options.series[0].data = xhr_data.phases_delivered.l1;
        echarts_phases_update_options.series[1].data = xhr_data.phases_delivered.l2;
        echarts_phases_update_options.series[2].data = xhr_data.phases_delivered.l3;

        if (CAPABILITY_ELECTRICITY_RETURNED) {
            echarts_phases_update_options.xAxis[1].data = xhr_data.read_at;
            echarts_phases_update_options.series[3].data = xhr_data.phases_returned.l1;
            echarts_phases_update_options.series[4].data = xhr_data.phases_returned.l2;
            echarts_phases_update_options.series[5].data = xhr_data.phases_returned.l3;
        }

        echarts_phases_graph.setOption(echarts_phases_update_options);

        let latest_delta_id = xhr_data.latest_delta_id;
        let pending_xhr_request = null;

        setInterval(function(){
            // Do not send new XHR request update if the previous one is still pending.
            if (pending_xhr_request !== null) {
                return;
            }

            pending_xhr_request = $.ajax({
                dataType: "json",
                url: PHASES_GRAPH_URL + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                echarts_phases_update_options.xAxis[0].data = echarts_phases_update_options.xAxis[0].data.concat(xhr_data.read_at);
                echarts_phases_update_options.series[0].data = echarts_phases_update_options.series[0].data.concat(xhr_data.phases_delivered.l1);
                echarts_phases_update_options.series[1].data = echarts_phases_update_options.series[1].data.concat(xhr_data.phases_delivered.l2);
                echarts_phases_update_options.series[2].data = echarts_phases_update_options.series[2].data.concat(xhr_data.phases_delivered.l3);

                if (CAPABILITY_ELECTRICITY_RETURNED) {
                    echarts_phases_update_options.xAxis[1].data = echarts_phases_update_options.xAxis[1].data.concat(xhr_data.read_at);
                    echarts_phases_update_options.series[3].data = echarts_phases_update_options.series[3].data.concat(xhr_data.phases_returned.l1);
                    echarts_phases_update_options.series[4].data = echarts_phases_update_options.series[4].data.concat(xhr_data.phases_returned.l2);
                    echarts_phases_update_options.series[5].data = echarts_phases_update_options.series[5].data.concat(xhr_data.phases_returned.l3);
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_phases_graph.setOption(echarts_phases_update_options);
            }).always(function(){
                // Allow new updates
                pending_xhr_request = null;
            });
        }, PHASES_GRAPH_INTERVAL * 1000);
    });
});

$(window).resize(function () {
    echarts_phases_graph?.resize();
});
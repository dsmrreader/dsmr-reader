$(document).ready(function () {
    echarts_phases_graph = echarts.init(document.getElementById('echarts-phases-graph'));

    let x_axis = [
        {
            type: 'category',
            boundaryGap: false,
            data: null
        },
        {
            type: 'category',
            boundaryGap: false,
            data: null,
            inverse: true,
            // Hide when not needed.
            show: CAPABILITY_ELECTRICITY_RETURNED
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
        grid: {
            top: '12%',
            left: '1%',
            right: '2%',
            containLabel: true
        },
        xAxis: x_axis,
        yAxis: [
            {
                type: 'value'
            },
            {
                type: 'value',
                inverse: true
            }
        ],
        dataZoom: [
            {
                show: true,
                start: LIVE_GRAPHS_INITIAL_ZOOM,
                end: 100
            },
            {
                type: 'inside',
                start: 0,
                end: 100
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
                data: null
            },
            {
                yAxisIndex: 0,
                name: 'L2+',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: null
            },
            {
                yAxisIndex: 0,
                name: 'L3+',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: null
            },
            {
                yAxisIndex: 1,
                name: 'L1-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            },
            {
                yAxisIndex: 1,
                name: 'L2-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            },
            {
                yAxisIndex: 1,
                name: 'L3-',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            }
        ]
    };

    echarts_phases_graph.showLoading('default', LOADING_OPTIONS);

    /* Init graph. */
    $.get(PHASES_GRAPH_URL, function (xhr_data) {
        echarts_phases_graph.hideLoading();
        echarts_phases_graph.setOption(echarts_phases_initial_options);

        /* Different set of options, to prevent the dataZoom being reset on each update. */
        echarts_phases_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_phases_update_options.xAxis[1].data = xhr_data.read_at;
        echarts_phases_update_options.series[0].data = xhr_data.phases_delivered.l1;
        echarts_phases_update_options.series[1].data = xhr_data.phases_delivered.l2;
        echarts_phases_update_options.series[2].data = xhr_data.phases_delivered.l3;
        echarts_phases_update_options.series[3].data = xhr_data.phases_returned.l1;
        echarts_phases_update_options.series[4].data = xhr_data.phases_returned.l2;
        echarts_phases_update_options.series[5].data = xhr_data.phases_returned.l3;
        echarts_phases_graph.setOption(echarts_phases_update_options);


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
                url: PHASES_GRAPH_URL + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                /* Ignore empty sets. */
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                /* Delta update. */
                for (let i = 0; i < xhr_data.read_at.length; i++) {
                    echarts_phases_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
                    echarts_phases_update_options.xAxis[1].data.push(xhr_data.read_at[i]);
                    echarts_phases_update_options.series[0].data.push(xhr_data.phases_delivered.l1[i]);
                    echarts_phases_update_options.series[1].data.push(xhr_data.phases_delivered.l2[i]);
                    echarts_phases_update_options.series[2].data.push(xhr_data.phases_delivered.l3[i]);
                    echarts_phases_update_options.series[3].data.push(xhr_data.phases_returned.l1[i]);
                    echarts_phases_update_options.series[4].data.push(xhr_data.phases_returned.l2[i]);
                    echarts_phases_update_options.series[5].data.push(xhr_data.phases_returned.l3[i]);
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
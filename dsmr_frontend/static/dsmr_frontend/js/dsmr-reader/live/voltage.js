$(document).ready(function () {
    echarts_voltage_graph = echarts.init(document.getElementById('echarts-voltage-graph'));

    let echarts_voltage_initial_options = {
        color: [
            VOLTAGE_L1_COLOR,
            VOLTAGE_L2_COLOR,
            VOLTAGE_L3_COLOR
        ],
        title: {
            text: TEXT_VOLTAGE_HEADER,
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
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: []
            }
        ],
        yAxis: [
            {
                type: 'value',
                min: 'dataMin',
                max: 'dataMax'
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
    let echarts_voltage_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: []
            }
        ],
        series: []
    };

    echarts_voltage_graph.showLoading('default', LOADING_OPTIONS);

    $.get(VOLTAGE_GRAPH_URL, function (xhr_data) {
        echarts_voltage_graph.hideLoading();

        /* Dynamic phases. */
        if (CAPABILITY_MULTI_PHASE) {
            echarts_voltage_update_options.series = [
                {
                    name: 'L1',
                    type: 'line',
                    data: []
                },
                {
                    name: 'L2',
                    type: 'line',
                    data: []
                },
                {
                    name: 'L3',
                    type: 'line',
                    data: []
                },
            ];
        } else {
            echarts_voltage_update_options.series = [
                {
                    name: 'Volt',
                    type: 'line',
                    data: []
                }
            ];
        }

        echarts_voltage_graph.setOption(echarts_voltage_initial_options);

        echarts_voltage_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_voltage_update_options.series[0].data = xhr_data.phase_voltage.l1;

        if (CAPABILITY_MULTI_PHASE) {
            echarts_voltage_update_options.series[1].data = xhr_data.phase_voltage.l2;
            echarts_voltage_update_options.series[2].data = xhr_data.phase_voltage.l3;
        }

        echarts_voltage_graph.setOption(echarts_voltage_update_options);

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
                url: VOLTAGE_GRAPH_URL + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                echarts_voltage_update_options.xAxis[0].data = echarts_voltage_update_options.xAxis[0].data.concat(xhr_data.read_at);
                echarts_voltage_update_options.series[0].data = echarts_voltage_update_options.series[0].data.concat(xhr_data.phase_voltage.l1);

                if (CAPABILITY_MULTI_PHASE) {
                    echarts_voltage_update_options.series[1].data = echarts_voltage_update_options.series[1].data.concat(xhr_data.phase_voltage.l2);
                    echarts_voltage_update_options.series[2].data = echarts_voltage_update_options.series[2].data.concat(xhr_data.phase_voltage.l3);
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_voltage_graph.setOption(echarts_voltage_update_options);
            }).always(function(){
                // Allow new updates
                pending_xhr_request = null;
            });
        }, VOLTAGE_GRAPH_INTERVAL * 1000);
    });
});

$(window).resize(function () {
    echarts_voltage_graph?.resize();
});
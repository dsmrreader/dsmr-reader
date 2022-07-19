$(document).ready(function () {
    echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));

    // Keep track of initial values, to only show the actual kWh diff instead of the meter totals
    let first_total_delivered = 0;
    let first_total_returned = 0;

    let echarts_electricity_initial_options = {
        color: [
            ELECTRICITY_DELIVERED_COLOR,
            ELECTRICITY_DELIVERED_ALTERNATE_COLOR,
            ELECTRICITY_RETURNED_COLOR,
            ELECTRICITY_RETURNED_ALTERNATE_COLOR
        ],
        title: {
            text: TEXT_ELECTRICITY_HEADER,
            textStyle: TITLE_TEXTSTYLE_OPTIONS,
            left: 'center',
        },
        tooltip: TOOLTIP_OPTIONS,
        calculable: true,
        grid: GRID_OPTIONS,
        axisPointer: {
            link: {xAxisIndex: 'all'}
        },
        legend: {
            top: '85%',
            data: [TEXT_DELIVERED, TEXT_RETURNED, TEXT_TOTAL_DELIVERED, TEXT_TOTAL_RETURNED]
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: [],
                axisLabel: {
                    color: TEXTSTYLE_COLOR
                }
            }
        ],
        yAxis: [
            {
                position: 'left',
                alignTicks: true,
                type: 'value',
                axisLabel: {
                    color: TEXTSTYLE_COLOR,
                    formatter: '{value} W'
                },
                axisLine: {
                    show: true
                },
            },
            {
                position: 'right',
                alignTicks: true,
                type: 'value',
                axisLabel: {
                    color: TEXTSTYLE_COLOR,
                    formatter: '{value} kWh'
                },
                axisLine: {
                    show: true
                },
                minInterval: 0.001
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
        media: [
            {
              option: {
                    toolbox: TOOLBOX_OPTIONS,
                    legend: {show: true},
                    grid: [{}, {
                        top: '50%'
                    }],
                },
            },
            {
                query: { maxWidth: 768},
                option: {
                    toolbox: {show: false},
                    legend: {show: false},
                    grid: [{}, {
                        top: '55%'
                    }],
                }
            }
        ],
    };

    /* These settings should not affect the updates and reset the zoom on each update. */
    let echarts_electricity_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: true,
                data: null
            }
        ],
        series: [
            {
                yAxisIndex: 0,
                name: TEXT_DELIVERED,
                type: 'line',
                smooth: true,
                areaStyle: {},
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: []
            },
            {
                yAxisIndex: 1,
                z: 1,
                name: TEXT_TOTAL_DELIVERED,
                type: 'line',
                smooth: true,
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: []
            },
            {
                yAxisIndex: 0,
                name: TEXT_RETURNED,
                type: 'line',
                smooth: true,
                emphasis: EMPHASIS_STYLE_OPTIONS,
                areaStyle: {},
                data: []
            },
            {
                yAxisIndex: 1,
                z: 1,
                name: TEXT_TOTAL_RETURNED,
                type: 'line',
                smooth: true,
                emphasis: EMPHASIS_STYLE_OPTIONS,
                data: []
            }
        ],
    };

    echarts_electricity_graph.showLoading('default', LOADING_OPTIONS);

    $.get(ELECTRICITY_GRAPH_URL, function (xhr_data) {
        if (! CAPABILITY_ELECTRICITY_RETURNED) {
            delete echarts_electricity_update_options.series[2];  // W
            delete echarts_electricity_update_options.series[3];  // kWh
        }

        echarts_electricity_graph.hideLoading();
        echarts_electricity_graph.setOption(echarts_electricity_initial_options);

        echarts_electricity_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_electricity_update_options.series[0].data = xhr_data.currently_delivered;

        first_total_delivered = xhr_data.total_delivered[0] ?? 0;

        // Show total X diff from the first data point
        xhr_data.total_delivered = xhr_data.total_delivered.map(
            x => (x - first_total_delivered).toFixed(3)
        );
        echarts_electricity_update_options.series[1].data = xhr_data.total_delivered;

        if (CAPABILITY_ELECTRICITY_RETURNED) {
            echarts_electricity_update_options.series[2].data = xhr_data.currently_returned;

            first_total_returned = xhr_data.total_returned[0] ?? 0;

            // Show total X diff from the first data point
            xhr_data.total_returned = xhr_data.total_returned.map(
                x => (x - first_total_returned).toFixed(3)
            );
            echarts_electricity_update_options.series[3].data = xhr_data.total_returned;
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

                xhr_data.total_delivered = xhr_data.total_delivered.map(
                    x => (x - first_total_delivered).toFixed(3)
                );
                echarts_electricity_update_options.series[1].data = echarts_electricity_update_options.series[1].data.concat(xhr_data.total_delivered);

                if (CAPABILITY_ELECTRICITY_RETURNED) {
                    echarts_electricity_update_options.series[2].data = echarts_electricity_update_options.series[2].data.concat(xhr_data.currently_returned);

                    xhr_data.total_returned = xhr_data.total_returned.map(
                        x => (x - first_total_returned).toFixed(3)
                    );
                    echarts_electricity_update_options.series[3].data = echarts_electricity_update_options.series[3].data.concat(xhr_data.total_returned);
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
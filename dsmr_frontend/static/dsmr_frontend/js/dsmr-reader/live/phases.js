$(document).ready(function () {

    let echarts_phases_graph = echarts.init(document.getElementById('echarts-phases-graph'));
    let echarts_phases_initial_options = {
        color: [
            phase_delivered_l1_color,
            phase_delivered_l2_color,
            phase_delivered_l3_color,
            phase_returned_l1_color,
            phase_returned_l2_color,
            phase_returned_l3_color
        ],
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
                data: null
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
                start: live_graphs_initial_zoom,
                end: 100
            },
            {
                type: 'inside',
                start: 0,
                end: 100
            }
        ],
    };

    /* These settings should not affect the updates and reset the zoom on each update. */
    let echarts_phases_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: null
            }
        ],
        series: [
            {
                name: 'Watt (L1)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: null
            },
            {
                name: 'Watt (L2)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: null
            },
            {
                name: 'Watt (L3)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'delivered',
                data: null
            },
            {
                name: 'Watt (L1)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            },
            {
                name: 'Watt (L2)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            },
            {
                name: 'Watt (L3)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                stack: 'returned',
                data: null
            }
        ]
    };

    echarts_phases_graph.showLoading('default', echarts_loading_options);

    /* Init graph. */
    $.get(echarts_phases_graph_url, function (xhr_data) {
        echarts_phases_graph.hideLoading();
        echarts_phases_graph.setOption(echarts_phases_initial_options);

        /* Different set of options, to prevent the dataZoom being reset on each update. */
        echarts_phases_update_options.xAxis[0].data = xhr_data.read_at;
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
                url: echarts_phases_graph_url + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                /* Ignore empty sets. */
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                /* Delta update. */
                for (let i = 0; i < xhr_data.read_at.length; i++) {
                    echarts_phases_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
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
        }, echarts_phases_graph_interval * 1000);
    });

    /* Responsiveness. */
    $(window).resize(function () {
        echarts_phases_graph.resize();
    });
});

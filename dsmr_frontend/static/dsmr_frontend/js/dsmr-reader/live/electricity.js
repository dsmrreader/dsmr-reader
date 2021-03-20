$(document).ready(function () {
    let echarts_electricity_graph = echarts.init(document.getElementById('echarts-electricity-graph'));
    let echarts_electricity_initial_options = {
        color: [
            electricity_delivered_color,
            electricity_returned_color
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
        ]
    };

    /* These settings should not affect the updates and reset the zoom on each update. */
    let echarts_electricity_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: false,
                data: null
            }
        ],
        series: [
            {
                name: 'Watt (+)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                data: null
            },
            {
                name: 'Watt (-)',
                type: 'line',
                smooth: true,
                areaStyle: {},
                data: null
            }
        ]
    };

    echarts_electricity_graph.showLoading('default', echarts_loading_options);

    /* Init graph. */
    $.get(echarts_electricity_graph_url, function (xhr_data) {
        echarts_electricity_graph.hideLoading();
        echarts_electricity_graph.setOption(echarts_electricity_initial_options);

        /* Different set of options, to prevent the dataZoom being reset on each update. */
        echarts_electricity_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_electricity_update_options.series[0].data = xhr_data.currently_delivered;
        echarts_electricity_update_options.series[1].data = xhr_data.currently_returned;
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
                url: echarts_electricity_graph_url + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                /* Ignore empty sets. */
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                /* Delta update. */
                for (let i = 0; i < xhr_data.read_at.length; i++) {
                    echarts_electricity_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
                    echarts_electricity_update_options.series[0].data.push(xhr_data.currently_delivered[i]);
                    echarts_electricity_update_options.series[1].data.push(xhr_data.currently_returned[i]);
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_electricity_graph.setOption(echarts_electricity_update_options);
            }).always(function(){
                // Allow new updates
                pending_xhr_request = null;
            });
        }, echarts_electricity_graph_interval * 1000);
    });

    /* Responsiveness. */
    $(window).resize(function () {
        echarts_electricity_graph.resize();
    });
});

$(document).ready(function () {
    var echarts_power_current_graph = echarts.init(document.getElementById('echarts-power-current-graph'));
    var echarts_power_current_initial_options = {
        color: [
            power_current_l1_color,
            power_current_l2_color,
            power_current_l3_color
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
                type: 'value',
                min: 'dataMin',
                max: 'dataMax'
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
    var echarts_power_current_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: true,
                data: null
            }
        ],
        series: null
    };

    echarts_power_current_graph.showLoading('default', echarts_loading_options);

    /* Init graph. */
    $.get(echarts_power_current_graph_url, function (xhr_data) {
        echarts_power_current_graph.hideLoading();

        /* Dynamic phases. */
        if (is_multi_phase) {
            echarts_power_current_update_options.series = [
                {
                    name: 'Ampere (L1)',
                    type: 'bar',
                    stack: true,
                    data: null
                },
                {
                    name: 'Ampere (L2)',
                    type: 'bar',
                    stack: true,
                    data: null
                },
                {
                    name: 'Ampere (L3)',
                    type: 'bar',
                    stack: true,
                    data: null
                },
            ];
        } else {
            echarts_power_current_update_options.series = [
                {
                    name: 'Ampere',
                    type: 'bar',
                    data: null
                }
            ];
        }

        echarts_power_current_graph.setOption(echarts_power_current_initial_options);

        /* Different set of options, to prevent the dataZoom being reset on each update. */
        echarts_power_current_update_options.xAxis[0].data = xhr_data.read_at;
        echarts_power_current_update_options.series[0].data = xhr_data.phase_power_current.l1;

        if (is_multi_phase) {
            echarts_power_current_update_options.series[1].data = xhr_data.phase_power_current.l2;
            echarts_power_current_update_options.series[2].data = xhr_data.phase_power_current.l3;
        }

        echarts_power_current_graph.setOption(echarts_power_current_update_options);

        var latest_delta_id = xhr_data.latest_delta_id;

        /* Update graph data from now on. */
        setInterval(function () {
            $.get(echarts_power_current_graph_url + "&latest_delta_id=" + latest_delta_id, function (xhr_data) {
                /* Ignore empty sets. */
                if (xhr_data.read_at.length == 0) {
                    return;
                }

                /* Delta update. */
                for (var i = 0; i < xhr_data.read_at.length; i++) {
                    echarts_power_current_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
                    echarts_power_current_update_options.series[0].data.push(xhr_data.phase_power_current.l1[i]);

                    if (is_multi_phase) {
                        echarts_power_current_update_options.series[1].data.push(xhr_data.phase_power_current.l2[i]);
                        echarts_power_current_update_options.series[2].data.push(xhr_data.phase_power_current.l3[i]);
                    }
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_power_current_graph.setOption(echarts_power_current_update_options);
            });
        }, echarts_power_current_graph_interval * 1000);
    });

    /* Responsiveness. */
    $(window).resize(function () {
        echarts_power_current_graph.resize();
    });
});

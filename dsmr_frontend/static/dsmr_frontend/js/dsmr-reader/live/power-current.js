$(document).ready(function () {
    let echarts_power_current_graph = echarts.init(document.getElementById('echarts-power-current-graph'));
    let echarts_power_current_initial_options = {
        toolbox: TOOLBOX_OPTIONS,
        color: [
            POWER_CURRENT_L1_COLOR,
            POWER_CURRENT_L2_COLOR,
            POWER_CURRENT_L3_COLOR
        ],
        title: {
            text: TEXT_POWER_CURRENT_HEADER,
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
                start: LIVE_GRAPHS_INITIAL_ZOOM,
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
    let echarts_power_current_update_options = {
        xAxis: [
            {
                type: 'category',
                boundaryGap: true,
                data: null
            }
        ],
        series: null
    };

    echarts_power_current_graph.showLoading('default', ECHARTS_LOADING_OPTIONS);

    /* Init graph. */
    $.get(ECHARTS_POWER_CURRENT_GRAPH_URL, function (xhr_data) {
        echarts_power_current_graph.hideLoading();

        /* Dynamic phases. */
        if (IS_MULTI_PHASE) {
            echarts_power_current_update_options.series = [
                {
                    name: 'L1',
                    type: 'bar',
                    stack: true,
                    data: null
                },
                {
                    name: 'L2',
                    type: 'bar',
                    stack: true,
                    data: null
                },
                {
                    name: 'L3',
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

        if (IS_MULTI_PHASE) {
            echarts_power_current_update_options.series[1].data = xhr_data.phase_power_current.l2;
            echarts_power_current_update_options.series[2].data = xhr_data.phase_power_current.l3;
        }

        echarts_power_current_graph.setOption(echarts_power_current_update_options);


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
                url: ECHARTS_POWER_CURRENT_GRAPH_URL + "&latest_delta_id=" + latest_delta_id,
            }).done(function(xhr_data) {
                /* Ignore empty sets. */
                if (xhr_data.read_at.length === 0) {
                    return;
                }

                /* Delta update. */
                for (let i = 0; i < xhr_data.read_at.length; i++) {
                    echarts_power_current_update_options.xAxis[0].data.push(xhr_data.read_at[i]);
                    echarts_power_current_update_options.series[0].data.push(xhr_data.phase_power_current.l1[i]);

                    if (IS_MULTI_PHASE) {
                        echarts_power_current_update_options.series[1].data.push(xhr_data.phase_power_current.l2[i]);
                        echarts_power_current_update_options.series[2].data.push(xhr_data.phase_power_current.l3[i]);
                    }
                }

                latest_delta_id = xhr_data.latest_delta_id;
                echarts_power_current_graph.setOption(echarts_power_current_update_options);
            }).always(function(){
                // Allow new updates
                pending_xhr_request = null;
            });
        }, ECHARTS_POWER_CURRENT_GRAPH_INTERVAL * 1000);
    });
});

$(window).resize(function () {
    echarts_power_current_graph?.resize();
});
$(document).ready(function () {

    var echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));
    echarts_gas_graph.showLoading('default', echarts_loading_options);

    /* Init graph. */
    $.get(echarts_gas_graph_url, function (xhr_data) {
        echarts_gas_graph.hideLoading();

        var option = {
            color: [
                gas_delivered_color
            ],
            tooltip: {
                trigger: 'axis',
                formatter: "{c} {a}",
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
                    boundaryGap: gas_graph_style == 'bar',
                    data: xhr_data.read_at
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
                    // Do not change initial zoom when using a non DSMR v5 meter.
                    // Because it will cause DSMR v4 meter users to only display 2 of 24 hours by default.
                    start: telegram_dsmr_version == '50' ? live_graphs_initial_zoom : 0,
                    end: 100
                },
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                }
            ],
            series: [
                {
                    name: 'm³',
                    type: gas_graph_style,
                    areaStyle: {},
                    data: xhr_data.currently_delivered,
                    smooth: true
                }
            ]
        };
        echarts_gas_graph.setOption(option);
    });

    /* Responsiveness. */
    $(window).resize(function () {
        echarts_gas_graph.resize();
    });
});

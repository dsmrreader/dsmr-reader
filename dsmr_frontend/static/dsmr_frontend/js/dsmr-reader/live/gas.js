$(document).ready(function () {

    let echarts_gas_graph = echarts.init(document.getElementById('echarts-gas-graph'));
    echarts_gas_graph.showLoading('default', ECHARTS_LOADING_OPTIONS);

    /* Init graph. */
    $.get(ECHARTS_GAS_GRAPH_URL, function (xhr_data) {
        echarts_gas_graph.hideLoading();

        let option = {
            toolbox: TOOLBOX_OPTIONS,
            color: [
                GAS_DELIVERED_COLOR
            ],
            title: {
                text: TEXT_GAS_HEADER,
                textStyle: TITLE_TEXTSTYLE,
                left: 'center',
            },
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
                    boundaryGap: GAS_GRAPH_STYLE === 'bar',
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
                    start: TELEGRAM_DSMR_VERSION === '50' ? LIVE_GRAPHS_INITIAL_ZOOM : 0,
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
                    type: GAS_GRAPH_STYLE,
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

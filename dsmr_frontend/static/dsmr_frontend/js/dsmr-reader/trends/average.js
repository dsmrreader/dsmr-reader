$(document).ready(function () {

    var echarts_avg_electricity_graph = null;
    var echarts_avg_electricity_returned_graph = null;
    var echarts_avg_gas_graph = null;

    if ($('#echarts-avg-electricity-graph').length > 0) {
        echarts_avg_electricity_graph = echarts.init(document.getElementById('echarts-avg-electricity-graph'));
    }

    if ($('#echarts-avg-electricity-returned-graph').length > 0) {
        echarts_avg_electricity_returned_graph = echarts.init(document.getElementById('echarts-avg-electricity-returned-graph'));
    }

    if ($('#echarts-avg-gas-graph').length > 0) {
        echarts_avg_gas_graph = echarts.init(document.getElementById('echarts-avg-gas-graph'));
    }

    var echarts_options = {
        calculable: true,
        tooltip: {
            trigger: 'item',
            formatter: "{b} ({d}%)"
        },
        series: [
            {
                name: '%',
                type: 'pie',
                radius: [25, 125],
                center: ['50%', '50%'],
                roseType: 'area',
                data: null
            }
        ]
    };

    /* Init graphs. */
    $.get(echarts_avg_consumption_url, function (xhr_data) {
        if (echarts_avg_electricity_graph) {
            echarts_options.series[0].data = xhr_data.electricity;
            echarts_avg_electricity_graph.setOption(echarts_options);
        }

        if (echarts_avg_electricity_returned_graph && xhr_data.electricity_returned.length > 0) {
            echarts_options.series[0].data = xhr_data.electricity_returned;
            echarts_avg_electricity_returned_graph.setOption(echarts_options);
        }

        if (echarts_avg_gas_graph && xhr_data.gas.length > 0) {
            echarts_options.series[0].data = xhr_data.gas;
            echarts_avg_gas_graph.setOption(echarts_options);
        }
    });

    /* Responsiveness. */
    $(window).resize(function () {
        if (echarts_avg_electricity_graph) {
            echarts_avg_electricity_graph.resize();
        }

        if (echarts_avg_electricity_returned_graph) {
            echarts_avg_electricity_returned_graph.resize();
        }

        if (echarts_avg_gas_graph) {
            echarts_avg_gas_graph.resize();
        }
    });
});
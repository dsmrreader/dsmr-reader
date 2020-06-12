$(document).ready(function () {

    var echarts_electricity_by_tariff_week_graph = echarts.init(document.getElementById('echarts-electricity-by-tariff-week-graph'));
    var echarts_electricity_by_tariff_month_graph = echarts.init(document.getElementById('echarts-electricity-by-tariff-month-graph'));

    var echarts_options = {
        color: [
            electricity_delivered_alternate_color,
            electricity_delivered_color
        ],
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
                data: null
            }
        ]
    };


    echarts_electricity_by_tariff_week_graph.showLoading('default', echarts_loading_options);
    echarts_electricity_by_tariff_month_graph.showLoading('default', echarts_loading_options);

    /* Init graphs. */
    $.get(echarts_by_tariff_url, function (xhr_data) {
        echarts_electricity_by_tariff_week_graph.hideLoading();
        echarts_electricity_by_tariff_month_graph.hideLoading();

        echarts_options.series[0].data = xhr_data.week;
        echarts_electricity_by_tariff_week_graph.setOption(echarts_options);

        echarts_options.series[0].data = xhr_data.month;
        echarts_electricity_by_tariff_month_graph.setOption(echarts_options);
    });

    /* Responsiveness. */
    $(window).resize(function () {
        echarts_electricity_by_tariff_week_graph.resize();
        echarts_electricity_by_tariff_month_graph.resize();
    });
});
let echarts_electricity_by_tariff_graph = echarts.init(document.getElementById('echarts-electricity-by-tariff-graph'));

function update_trends_tariffs(start_date, end_date) {
    let echarts_options = {
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
                radius: ['10%', '60%'],
                label: {
                    formatter: '{b}\n{d}%'
                },
                data: null
            }
        ]
    };

    echarts_electricity_by_tariff_graph.showLoading('default', echarts_loading_options);

    $.ajax({
        url: echarts_by_tariff_url,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).done(function (xhr_result) {
        echarts_options.series[0].data = xhr_result.data;
        echarts_electricity_by_tariff_graph.setOption(echarts_options);
    }).always(function(){
        echarts_electricity_by_tariff_graph.hideLoading();
    });
}

$(document).ready(function () {
    $(window).resize(function () {
        echarts_electricity_by_tariff_graph?.resize();
    });
});

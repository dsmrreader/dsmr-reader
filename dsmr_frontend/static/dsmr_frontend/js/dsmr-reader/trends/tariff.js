let echarts_electricity_by_tariff_graph = echarts.init(document.getElementById('echarts-electricity-by-tariff-graph'));

function update_trends_tariffs(start_date, end_date) {
    let echarts_options = {
        baseOption: {
            color: [
                ELECTRICITY_DELIVERED_ALTERNATE_COLOR,
                ELECTRICITY_DELIVERED_COLOR
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
                    label: {
                        formatter: '{b}\n{d}%'
                    },
                    data: null
                }
            ]
        },
        media: [
            {
              option: {
                    series: [
                        {
                            radius: ['10%', '90%'],
                            width: '100%',
                            label: {
                                alignTo: 'labelLine',
                                edgeDistance: '5%'
                            }
                        }
                    ],
                },
            },
            {
                query: { maxWidth: 500},
                option: {
                    series: [
                        {
                            radius: ['10%', '25%'],
                            label: {
                                alignTo: 'edge',
                                position: 'outside',
                                edgeDistance: 0
                            }
                        }
                    ]
                }
            }
        ]
    };

    echarts_electricity_by_tariff_graph.showLoading('default', ECHARTS_LOADING_OPTIONS);

    $.ajax({
        url: ECHARTS_BY_TARIFF_URL,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).done(function (xhr_result) {
        echarts_options.baseOption.series[0].data = xhr_result.data;
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

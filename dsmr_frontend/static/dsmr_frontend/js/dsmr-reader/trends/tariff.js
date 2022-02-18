let echarts_electricity_by_tariff_graph = echarts.init(document.getElementById('echarts-electricity-by-tariff-graph'));

function update_trends_tariffs(start_date, end_date) {
    let echarts_options = {
        baseOption: {
            title: {
                text: TEXT_TITLE_TARIFF_RATIO,
                textStyle: TITLE_TEXTSTYLE_OPTIONS,
                left: 'center',
            },
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
                            radius: ['10%', '70%'],
                            width: '100%',
                            label: {
                                alignTo: 'edge',
                                position: 'outside',
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
                                edgeDistance: 0
                            }
                        }
                    ]
                }
            }
        ]
    };

    echarts_electricity_by_tariff_graph.showLoading('default', LOADING_OPTIONS);
    echarts_electricity_by_tariff_graph?.clear();

    $.ajax({
        url: BY_TARIFF_URL,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).fail(function (xhr_data) {
        echarts_electricity_by_tariff_graph?.showLoading('default', {text: '❌ ' + xhr_data.responseText});
    }).done(function (xhr_result) {
        let data = xhr_result.data;
        data.forEach(function (item) {
            item['label'] = {
                color: PIE_TEXTSTYLE_COLOR
             };
        });

        echarts_options.baseOption.series[0].data = data;
        echarts_electricity_by_tariff_graph.setOption(echarts_options);
        echarts_electricity_by_tariff_graph.hideLoading();
    });
}

$(window).resize(function () {
    echarts_electricity_by_tariff_graph?.resize();
});

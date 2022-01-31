let echarts_avg_electricity_graph = null;
let echarts_avg_electricity_returned_graph = null;
let echarts_avg_gas_graph = null;

function update_trends_averages(start_date, end_date) {
    let echarts_options = {
        baseOption: {
            title: {
                text: null,  // Set below
                textStyle: TITLE_TEXTSTYLE_OPTIONS,
                left: 'center'
            },
            calculable: true,
            tooltip: {
                trigger: 'item',
                formatter: '{b}\n({d}%)'
            },
            series: [
                {
                    name: '%',
                    type: 'pie',
                    roseType: 'radius',
                    label: {
                        formatter: '{d}% {S|{b}}',
                        rich: {
                            S: {
                                fontSize: 8,
                                color: 'grey'
                            },
                        }
                    },
                    labelLine: {
                        length2: 0
                    },
                    data: null
                }
            ],
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

    echarts_avg_electricity_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_electricity_graph?.clear();
    echarts_avg_electricity_returned_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_electricity_returned_graph?.clear();
    echarts_avg_gas_graph?.showLoading('default', LOADING_OPTIONS);
    echarts_avg_gas_graph?.clear();

    $.ajax({
        url: AVG_CONSUMPTION_URL,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).done(function (xhr_data) {
        let dataElectricity = xhr_data.electricity;
        dataElectricity.forEach(function (item) {
            item['label'] = {
                color: PIE_TEXTSTYLE_COLOR
             };
        });

        echarts_options.baseOption.series[0].data = dataElectricity;
        echarts_options.baseOption.title.text = TEXT_TITLE_ELECTRICITY;
        echarts_avg_electricity_graph?.setOption(echarts_options);
        echarts_avg_electricity_graph?.hideLoading();

        if (xhr_data.electricity_returned.length > 0) {
            let dataElectricityReturned = xhr_data.electricity_returned;
            dataElectricityReturned.forEach(function (item) {
                item['label'] = {
                    color: PIE_TEXTSTYLE_COLOR
                 };
            });

            echarts_options.baseOption.series[0].data = dataElectricityReturned;
            echarts_options.baseOption.title.text = TEXT_TITLE_ELECTRICITY_RETURNED;
            echarts_avg_electricity_returned_graph?.setOption(echarts_options);
            echarts_avg_electricity_returned_graph?.hideLoading();
        }

        if (xhr_data.gas.length > 0) {
            let dataGas = xhr_data.gas;
            dataGas.forEach(function (item) {
                item['label'] = {
                    color: PIE_TEXTSTYLE_COLOR
                 };
            });

            echarts_options.baseOption.series[0].data = dataGas;
            echarts_options.baseOption.title.text = TEXT_TITLE_GAS;
            echarts_avg_gas_graph?.setOption(echarts_options);
            echarts_avg_gas_graph?.hideLoading();
        }
    });
}

$(window).resize(function () {
    echarts_avg_electricity_graph?.resize();
    echarts_avg_electricity_returned_graph?.resize();
    echarts_avg_gas_graph?.resize();
});

$(document).ready(function () {
    if ($('#echarts-avg-electricity-graph').length > 0) {
        echarts_avg_electricity_graph = echarts.init(document.getElementById('echarts-avg-electricity-graph'));
    }

    if ($('#echarts-avg-electricity-returned-graph').length > 0) {
        echarts_avg_electricity_returned_graph = echarts.init(document.getElementById('echarts-avg-electricity-returned-graph'));
    }

    if ($('#echarts-avg-gas-graph').length > 0) {
        echarts_avg_gas_graph = echarts.init(document.getElementById('echarts-avg-gas-graph'));
    }

    update_trends();
});

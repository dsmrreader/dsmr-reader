let echarts_avg_electricity_graph = null;
let echarts_avg_electricity_returned_graph = null;
let echarts_avg_gas_graph = null;

function update_trends_averages(start_date, end_date) {
    let echarts_options = {
        baseOption: {
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

    $.ajax({
        url: ECHARTS_AVG_CONSUMPTION_URL,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).done(function (xhr_data) {
        echarts_options.baseOption.series[0].data = xhr_data.electricity;
        echarts_avg_electricity_graph?.setOption(echarts_options);

        if (xhr_data.electricity_returned.length > 0) {
            echarts_options.baseOption.series[0].data = xhr_data.electricity_returned;
            echarts_avg_electricity_returned_graph?.setOption(echarts_options);
        }

        if (xhr_data.gas.length > 0) {
            echarts_options.baseOption.series[0].data = xhr_data.gas;
             echarts_avg_gas_graph?.setOption(echarts_options);
        }
    });
}


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

    $(window).resize(function () {
        echarts_avg_electricity_graph?.resize();
        echarts_avg_electricity_returned_graph?.resize();
        echarts_avg_gas_graph?.resize();
    });
});

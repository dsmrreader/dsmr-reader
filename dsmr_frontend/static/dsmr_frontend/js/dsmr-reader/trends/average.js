let echarts_avg_electricity_graph = null;
let echarts_avg_electricity_returned_graph = null;
let echarts_avg_gas_graph = null;

function update_trends_averages(start_date, end_date) {
    let echarts_options = {
        calculable: true,
        tooltip: {
            trigger: 'item',
            formatter: '{b}\n({d}%)'
        },
        series: [
            {
                name: '%',
                type: 'pie',
                radius: ['1%', '75%'],
                center: ['50%', '50%'],
                width: '100%',
                roseType: 'radius',
                label: {
                    // alignTo: 'labelLine',
                    formatter: '{d}%\n{S|{b}}',
                    rich: {
                        S: {
                            fontSize: 8,
                            color: 'grey'
                        },
                    }
                },
                labelLine: {
                    length: 5,
                    length2: 5
                },
                data: null
            }
        ]
    };

    $.ajax({
        url: echarts_avg_consumption_url,
        data: {
            'start_date': start_date,
            'end_date': end_date
        },
    }).done(function (xhr_data) {
        echarts_options.series[0].data = xhr_data.electricity;
        echarts_avg_electricity_graph?.setOption(echarts_options);

        if (xhr_data.electricity_returned.length > 0) {
            echarts_options.series[0].data = xhr_data.electricity_returned;
            echarts_avg_electricity_returned_graph?.setOption(echarts_options);
        }

        if (xhr_data.gas.length > 0) {
            echarts_options.series[0].data = xhr_data.gas;
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

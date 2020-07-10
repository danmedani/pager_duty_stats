'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import StackedColumn from './stackedColumn';
import SearchFilter from './searchFilter';

const e = React.createElement;

var blankChart = {
  series: [],
  options: {
    chart: {
      type: 'bar',
      height: 350,
      stacked: true,
      toolbar: {
        show: true
      },
      zoom: {
        enabled: true
      }
    },
    responsive: [{
      breakpoint: 480,
      options: {
        legend: {
          position: 'bottom',
          offsetX: -10,
          offsetY: 0
        }
      }
    }],
    plotOptions: {
      bar: {
        horizontal: false,
      },
    },
    xaxis: {
      type: 'datetime',
      categories: []
    },
    legend: {
      position: 'right',
      offsetY: 40
    },
    fill: {
      opacity: 1
    }
  }
}

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      chartData: blankChart
    };

    this.updateChartData = this.updateChartData.bind(this);
  }

  updateChartData(chartDataFromSearch) {
    var chartData = JSON.parse(JSON.stringify(blankChart));
    chartData.series = chartDataFromSearch.series;
    chartData.options.xaxis.categories = chartDataFromSearch.xaxis;
    this.setState({chartData: chartData});
  }

  render() {
    return (
        <div>
            <div>
                <SearchFilter updateChartDataCallback={this.updateChartData} />
            </div>
            <div>
                <StackedColumn chartData={this.state.chartData} />
            </div>
        </div>
    );
  }
}

const domContainer = document.querySelector('#chart_container');
ReactDOM.render(e(ChartPage), domContainer);

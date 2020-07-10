import React from 'react';
import ReactApexChart from 'react-apexcharts'

class StackedColumn extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      series: this.props.chartData.series,
      options: this.props.chartData.options
    };
  }

  render() {
    return (
      <div id="chart">
        <ReactApexChart options={this.props.chartData.options} series={this.props.chartData.series} type="bar" />
      </div>
    );
  }
}

export default StackedColumn;

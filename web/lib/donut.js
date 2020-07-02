var _jsxFileName = "/Users/dmedani/codes/pager_duty_stats/web/src/donut.js";
import React, { Component } from 'react';
import Chart from 'react-apexcharts';

class Donut extends Component {
  constructor(props) {
    super(props);
    this.state = {
      options: {},
      series: [44, 55, 41, 17, 15],
      labels: ['A', 'B', 'C', 'D', 'E']
    };
  }

  render() {
    return /*#__PURE__*/React.createElement("div", {
      className: "donut",
      __self: this,
      __source: {
        fileName: _jsxFileName,
        lineNumber: 18,
        columnNumber: 7
      }
    }, /*#__PURE__*/React.createElement(Chart, {
      options: this.state.options,
      series: this.state.series,
      type: "donut",
      width: "380",
      __self: this,
      __source: {
        fileName: _jsxFileName,
        lineNumber: 19,
        columnNumber: 9
      }
    }));
  }

}

export default Donut;
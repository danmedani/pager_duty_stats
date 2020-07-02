'use strict';

var _jsxFileName = "/Users/dmedani/codes/pager_duty_stats/web/src/chart.js";
import Donut from './modules/donut';
const e = React.createElement;

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      liked: false
    };
  }

  render() {
    return /*#__PURE__*/React.createElement(Donut, {
      __self: this,
      __source: {
        fileName: _jsxFileName,
        lineNumber: 14,
        columnNumber: 12
      }
    });
  }

}

const domContainer = document.querySelector('#chart_container');
ReactDOM.render(e(ChartPage), domContainer);
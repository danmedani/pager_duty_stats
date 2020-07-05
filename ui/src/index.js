'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import Donut from './donut';

const e = React.createElement;

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    return <Donut />;
  }
}

const domContainer = document.querySelector('#chart_container');
ReactDOM.render(e(ChartPage), domContainer);


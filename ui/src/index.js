'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import StackedColumn from './stackedColumn';
import SearchFilter from './searchFilter';

const e = React.createElement;

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { liked: false };
  }

  render() {
    return (
        <div>
            <div>
                <SearchFilter />
            </div>
            <div>
                <StackedColumn />
            </div>
        </div>
    );
  }
}

const domContainer = document.querySelector('#chart_container');
ReactDOM.render(e(ChartPage), domContainer);

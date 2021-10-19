'use strict';

require("regenerator-runtime/runtime");

import React from 'react';
import { isOauthTokenValid, getServices, getTeams } from '../logic/api';

import ReactDOM from 'react-dom';
import StackedColumn from '../components/stackedColumn';
import SearchFilter from '../components/searchFilter';
import { CircularProgress, Button } from '@material-ui/core';
import { blankChart } from '../logic/models'

const e = React.createElement;

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      chartData: blankChart,
      searchButtonDisabled: false,
      services: [],
      teams: [],
      searched: false
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.beginSearch = this.beginSearch.bind(this);
    this.endSearch = this.endSearch.bind(this);
    this.updateChartData = this.updateChartData.bind(this);
    this.logOut = this.logOut.bind(this);
  }

  async componentDidMount() {
    const existingToken = localStorage.getItem("pager-duty-token");
    if ((!existingToken) || ! await isOauthTokenValid(existingToken)) {
      window.location.href = '/';
    } else {
      getTeams(existingToken).then(
        (result) => {this.setState({teams: result})}
      );
      getServices(existingToken).then(
        (result) => {this.setState({services: result})}
      );
    }
  }

  getChartTitle(chartType) {
    return 'Incident Counts';
  }

  updateChartData(chartDataFromSearch, chartType) {
    var chartData = JSON.parse(JSON.stringify(blankChart));
    chartData.series = chartDataFromSearch.series;
    chartData.options.xaxis.categories = chartDataFromSearch.xaxis;
    chartData.options.title.text = this.getChartTitle(chartType);
    this.setState({
      chartData: chartData,
      searched: true
    });
  }

  logOut() {
    localStorage.removeItem('pager-duty-token');
    window.location.href = '/';
  }

  beginSearch() {
    this.setState({searchButtonDisabled: true});
  }

  endSearch() {
    this.setState({searchButtonDisabled: false});
  }

  checkKey() {
    if (this.state.pdApiKey == '') {
      this.setState(
        {
          apiKeyError: error,
          checkKeyButtonDisabled: false
        }
      )
      return
    }
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  render() {
    return (
        <div>
          <div>
            <SearchFilter 
              updateChartDataCallback={this.updateChartData}
              beginSearchCallback={this.beginSearch}
              endSearchCallback={this.endSearch} 
              searchButtonDisabled={this.state.searchButtonDisabled} 
              pdApiKey={this.state.pdApiKey}
              teams={this.state.teams}
              services={this.state.services}
            />
          </div>
          <div>
            {this.state.searchButtonDisabled
              ?
              <div className="graph-area">
                <CircularProgress />
              </div>
              :
              this.state.searched
                ?
                <StackedColumn 
                  chartData={this.state.chartData}
                  beginSearchCallback={this.beginSearch}
                  endSearchCallback={this.endSearch}
                  searchButtonDisabled={this.state.searchButtonDisabled} 
                />
                :
                <div className="graph-area">
                  Patiently awaiting your search...
                </div>
            }
          </div>
          <div id="logout">
            <Button variant="contained" color="secondary" onClick={() => this.logOut()}>
              Log Out
            </Button>
          </div>
        </div>
    );
  }
}

const domContainer = document.querySelector('#main_container');
ReactDOM.render(e(ChartPage), domContainer);

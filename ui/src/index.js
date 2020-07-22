'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import StackedColumn from './stackedColumn';
import SearchFilter from './searchFilter';
import { Button, TextField, CircularProgress } from '@material-ui/core';
import { blankChart } from './util/models'

const e = React.createElement;

const chartTitleMap = {
    'SERVICE_NAME': 'by Service Name',
    'TIME_OF_DAY': 'by Time of Day',
    'CUSTOM_INCIDENT_TYPE': 'by Type',
}

class ChartPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      apiKeyError: '',
      chartData: blankChart,
      searchButtonDisabled: false,
      checkKeyButtonDisabled: false,
      gotLegitApiKey: false,
      pdApiKey: '',
      services: [],
      teams: []
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.beginSearch = this.beginSearch.bind(this);
    this.endSearch = this.endSearch.bind(this);
    this.updateChartData = this.updateChartData.bind(this);

    var existingApiKey = localStorage.getItem('pd_api_key') || '';
    if (existingApiKey !== '') {
        this.state.pdApiKey = existingApiKey;
    }
  }

  getChartTitle(chartType) {
    return 'Incident Counts, ' + chartTitleMap[chartType];
  }

  updateChartData(chartDataFromSearch, chartType) {
    var chartData = JSON.parse(JSON.stringify(blankChart));
    chartData.series = chartDataFromSearch.series;
    chartData.options.xaxis.categories = chartDataFromSearch.xaxis;
    chartData.options.title.text = this.getChartTitle(chartType);
    this.setState({chartData: chartData});
  }

  beginSearch() {
    this.setState({searchButtonDisabled: true});
  }

  endSearch() {
    this.setState({searchButtonDisabled: false});
  }

  checkKey() {
    this.setState(
      {
        checkKeyButtonDisabled: true,
        apiKeyError: null
      }
    )
    fetch(
      '/api/teams?pd_api_key=' + this.state.pdApiKey
      )
      .then(res => res.json())
      .then(
        (result) => {
          this.setState(
            {
              teams: result,
              gotLegitApiKey: true
            }
          )
          
          // looks like the api key worked out. let's go grab the services (this can take a while)
          // Let's save the api key to local storage...
          localStorage.setItem('pd_api_key', this.state.pdApiKey);
          fetch(
            '/api/services?pd_api_key=' + this.state.pdApiKey
            )
            .then(res => res.json())
            .then(
              (result) => {
                this.setState(
                  {
                    services: result,
                    checkKeyButtonDisabled: false,
                    apiKeyError: null
                  }
                )
              },
              // Note: it's important to handle errors here
              // instead of a catch() block so that we don't swallow
              // exceptions from actual bugs in components.
              (error) => {
                
              }
            )
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState(
            {
              pdApiKey: '',
              apiKeyError: error,
              checkKeyButtonDisabled: false
            }
          )
        }
      )
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
          {!this.state.gotLegitApiKey 
            ?
            <div id="pdApiKey">
              <div>
                <p className="title">
                  Enter PagerDuty API Key
                </p>
              </div>
              <div>
                <TextField 
                  id="outlined-basic" 
                  label="Pager Duty Api Key" 
                  variant="outlined" 
                  name="pdApiKey"
                  type="password"
                  value={this.state.pdApiKey} 
                  onChange={this.handleInputChange} 
                />
              </div>
              <div>
                {this.state.apiKeyError &&
                  <p className="errorMsg">
                    API Key Not Accepted
                  </p>
                }
                </div>
              <div>
              <Button variant="contained" color="primary" onClick={() => this.checkKey()} disabled={this.state.checkKeyButtonDisabled}>
                Go
              </Button>
              </div>
            </div>
            :
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
                  <div id="circularProgress">
                    <CircularProgress />
                  </div>
                  :
                  <StackedColumn 
                    chartData={this.state.chartData}
                    beginSearchCallback={this.beginSearch}
                    endSearchCallback={this.endSearch}
                    searchButtonDisabled={this.state.searchButtonDisabled} 
                  />
                }
              </div>
            </div>
          }
        </div>
    );
  }
}

const domContainer = document.querySelector('#main_container');
ReactDOM.render(e(ChartPage), domContainer);

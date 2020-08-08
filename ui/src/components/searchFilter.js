import React from 'react';
import { Button, FormControlLabel, Radio, RadioGroup, TextField, ThemeProvider, createMuiTheme, CircularProgress } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';


const theme = createMuiTheme({
  typography: {
    fontSize: 12,
    fontFamily: [
      '-apple-system'
    ].join(','),
  },
});


class SearchFilter extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      groupingWindow: 'day',
      chartType: 'SERVICE_NAME',
      filterType: 'team',
      loadingData: false,
      startDate: '2020-05-01',
      endDate: '',
      services: [],
      teams: [],
      searchError: ''
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.onServicesChange = this.onServicesChange.bind(this);
    this.onTeamsChange = this.onTeamsChange.bind(this);
    this.handleFilterTypeChange = this.handleFilterTypeChange.bind(this);
  }

  onServicesChange(event, values) {
    this.setState({
      services: values
    });
  }

  onTeamsChange(event, values) {
    this.setState({
      teams: values
    });
  }

  handleFilterTypeChange(event) {
    this.setState({
      teams: [],
      services: [],
    });
    this.handleInputChange(event);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  fetchData() {
    this.setState({
      loadingData: true,
      searchError: ''
    });

    var data = {
      'start_date': this.state.startDate,
      'end_date': this.state.endDate,
      'grouping_window': this.state.groupingWindow,
      'chart_type': this.state.chartType,
      'pd_api_key': this.props.pdApiKey,
    };
    if (this.state.filterType == 'service') {
        data.service_ids = this.state.services.map(service => service.id).join(',');
    } else if (this.state.teams.length > 0) {
        data.team_ids = this.state.teams.map(team => team.id).join(',');
    }
    if (this.state.teams.length + this.state.services.length == 0) {
        this.setState({
            loadingData: false,
            searchError: 'Please enter at least one service or team to search'
        })
        return
    }
    this.props.beginSearchCallback();
    fetch(
      '/api/chart',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        }
      )
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            loadingData: false,
            items: result.items
          });
          this.props.updateChartDataCallback(result, this.state.chartType);
          this.props.endSearchCallback();
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            loadingData: false,
            searchError: error
          });
          this.props.endSearchCallback();
        }
      )
  }

  render() {
    return (
      <div id="search-filter-container">
        <div id="search-filter">
          <ThemeProvider theme={theme}>
            <div >
              <RadioGroup aria-label="Filter Type" name="filterType" value={this.state.filterType} onChange={this.handleFilterTypeChange}>
                <FormControlLabel value="service" control={<Radio />} label="By Service" />
                <FormControlLabel value="team" control={<Radio />} label="By Team" />
              </RadioGroup>
              {this.state.filterType == 'service'
                ?
                this.props.services.length > 0
                  ?
                  <Autocomplete
                    multiple
                    id="services-selector"
                    options={this.props.services}
                    getOptionLabel={(service) => service.name}
                    style={{ width: 300 }}
                    renderInput={(params) => (
                      <TextField {...params} label="Select Service(s)" variant="outlined" />
                    )}
                    disabled={!this.props.services}
                    onChange={this.onServicesChange}
                    value={this.state.services}
                  />
                  :
                  <div>
                    <p>
                      Fetching services...
                    </p>
                    <CircularProgress />
                  </div>
                :
                this.props.teams.length > 0
                  ?
                  <Autocomplete
                    multiple
                    id="team-selector"
                    options={this.props.teams}
                    getOptionLabel={(team) => team.name}
                    style={{ width: 300 }}
                    renderInput={(params) => (
                      <TextField {...params} label="Select Team(s)" variant="outlined" />
                    )}
                    disabled={!this.props.teams}
                    onChange={this.onTeamsChange}
                    value={this.state.teams}
                  />
                  :
                  <div>
                    <p>
                      Fetching teams...
                    </p>
                    <CircularProgress />
                  </div>
              }
            </div>
            <TextField
              id="date"
              label="Start Date"
              type="date"
              name="startDate"
              value={this.state.startDate}
              onChange={this.handleInputChange}
              InputLabelProps={{
                  shrink: true,
              }}
            />
            <TextField
              id="date"
              label="End Date"
              type="date"
              name="endDate"
              onChange={this.handleInputChange}
              InputLabelProps={{
                  shrink: true,
              }}
            />
            <RadioGroup aria-label="Grouping Window" name="groupingWindow" value={this.state.groupingWindow} onChange={this.handleInputChange}>
              <FormControlLabel value="day" control={<Radio />} label="Day" />
              <FormControlLabel value="week" control={<Radio />} label="Week" />
            </RadioGroup>
            <RadioGroup aria-label="Chart Type" name="chartType" value={this.state.chartType} onChange={this.handleInputChange}>
              <FormControlLabel value="SERVICE_NAME" control={<Radio />} label="By Service Name" />
              <FormControlLabel value="TIME_OF_DAY" control={<Radio />} label="By Time of Day" />
              <FormControlLabel value="CUSTOM_INCIDENT_TYPE" control={<Radio />} label="By Type" />
            </RadioGroup>
            <Button type="submit" variant="contained" color="primary" onClick={() => this.fetchData()} disabled={this.props.searchButtonDisabled}>
              Search
            </Button>
          </ThemeProvider>
        </div>
        <div className="error-msg">
          {this.state.searchError && 
            <p>
              {this.state.searchError}
            </p>
          }
        </div>
      </div>
    );
  }
}

export default SearchFilter;

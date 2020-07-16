import React from 'react';
import { Button, FormControlLabel, Radio, RadioGroup, TextField } from '@material-ui/core';
import Autocomplete from '@material-ui/lab/Autocomplete';


class SearchFilter extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      groupingWindow: 'day',
      chartType: 'serviceName',
      loadingData: false,
      startDate: '2020-05-01',
      endDate: null,
      serviceIds: 'P289YKV,PJQKKBU',
      pdApiKey: '',
      teams: [],
      services: []
    };

    setTimeout(() => {
      fetch(
        '/api/teams?pd_api_key=???'
        )
        .then(res => res.json())
        .then(
          (result) => {
            this.setState(
              {
                teams: result
              }
            )
          },
          // Note: it's important to handle errors here
          // instead of a catch() block so that we don't swallow
          // exceptions from actual bugs in components.
          (error) => {
            this.setState({
              loadingData: false,
              error
            });
          }
        )
    }, 1)

    setTimeout(() => {
      fetch(
        '/api/services?pd_api_key=???'
        )
        .then(res => res.json())
        .then(
          (result) => {
            this.setState(
              {
                services: result
              }
            )
          },
          // Note: it's important to handle errors here
          // instead of a catch() block so that we don't swallow
          // exceptions from actual bugs in components.
          (error) => {
            this.setState({
              loadingData: false,
              error
            });
          }
        )
    }, 1)

    this.handleInputChange = this.handleInputChange.bind(this);
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
      loadingData: true
    });

    var data = {
      'service_ids': this.state.serviceIds,
      'start_date': this.state.startDate,
      'end_date': this.state.endDate,
      'grouping_window': this.state.groupingWindow,
      'chart_type': this.state.chartType,
      'pd_api_key': this.state.pdApiKey,
    };
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
          this.props.updateChartDataCallback(result);
          this.props.endSearchCallback();
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            loadingData: false,
            error
          });
          this.props.endSearchCallback();
        }
      )
  }

  render() {
    return (
      <div id="searchFilter">
        <Autocomplete
          multiple
          id="team-selector"
          options={this.state.teams}
          getOptionLabel={(team) => team.name}
          style={{ width: 300 }}
          renderInput={(params) => (
            <TextField {...params} label="Select Team" variant="outlined" />
          )}
        />
        <Autocomplete
          multiple
          id="team-selector"
          options={this.state.services}
          getOptionLabel={(service) => service.name}
          style={{ width: 300 }}
          renderInput={(params) => (
            <TextField {...params} label="Select Service" variant="outlined" />
          )}
        />
        <TextField 
          id="outlined-basic" 
          label="Service IDs" 
          variant="outlined" 
          name="serviceIds"
          value={this.state.serviceIds} 
          onChange={this.handleInputChange} 
        />
        <TextField 
          id="outlined-basic" 
          label="Api Key" 
          variant="outlined" 
          name="pdApiKey"
          value={this.state.pdApiKey} 
          onChange={this.handleInputChange} 
        />
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
          <FormControlLabel value="serviceName" control={<Radio />} label="By Service Name" />
          <FormControlLabel value="timeOfDay" control={<Radio />} label="By Time of Day" />
          <FormControlLabel value="type" control={<Radio />} label="By Type" />
        </RadioGroup>
        <Button variant="contained" color="primary" onClick={() => this.fetchData()} disabled={this.props.searchButtonDisabled}>
          Search
        </Button>
      </div>
    );
  }
}

export default SearchFilter;

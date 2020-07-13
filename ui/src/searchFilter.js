import React from 'react';
import { Button, FormControlLabel, Radio, RadioGroup, TextField } from '@material-ui/core';

class SearchFilter extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      groupingWindow: 'day',
      loadingData: false,
      startDate: '2020-05-01',
      endDate: null,
      serviceIds: 'P289YKV,PJQKKBU',
      pdApiKey: ''
    };

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
      'pd_api_key': this.state.pdApiKey,
    };
    this.props.beginSearchCallback();
    fetch(
      'http://pagerdutystats-env.eba-pf8bvutt.us-east-2.elasticbeanstalk.com/api/chart',
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
        <Button variant="contained" color="primary" onClick={() => this.fetchData()} disabled={this.props.searchButtonDisabled}>
          Search
        </Button>
      </div>
    );
  }
}

export default SearchFilter;

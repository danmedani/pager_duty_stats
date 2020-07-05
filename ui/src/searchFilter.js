import React from 'react';
import { Button, FormControlLabel, Radio, RadioGroup, TextField } from '@material-ui/core';

class SearchFilter extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      groupingWindow: 'day',
      loadingData: false,
      startDate: '2020-01-01',
      endDate: null,
      serviceIds: 'asd'
    };
  }

  handleGroupChange(event) {
    this.setState({groupingWindow: event.target.value});
  }

  // handleGroupChange(event) {
  //   this.setState({groupingWindow: event.target.value});
  // }

  fetchData() {
    this.setState({
      loadingData: true
    });

    var data = {
      'service_ids': this.state.serviceIds,
      'start_date': this.state.startDate,
      'end_date': this.state.endDate,
      'grouping_window': this.state.groupingWindow
    };
    fetch(
      'http://127.0.0.1:3031/api/chart',
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
  }

  render() {
    return (
      <div id="searchFilter">
        <TextField id="outlined-basic" label="Service IDs" variant="outlined" value={this.state.serviceIds} />
        <TextField
          id="date"
          label="Start Date"
          type="date"
          // defaultValue="2020-01-01"
          value={this.state.startDate}
          InputLabelProps={{
              shrink: true,
          }}
        />
        <TextField
          id="date"
          label="End Date"
          type="date"
          defaultValue="2021-01-01"
          InputLabelProps={{
              shrink: true,
          }}
        />
        <RadioGroup aria-label="Grouping Window" name="groupingWindow" value={this.state.groupingWindow} onChange={(event) => this.handleGroupChange(event)}>
          <FormControlLabel value="day" control={<Radio />} label="Day" />
          <FormControlLabel value="week" control={<Radio />} label="Week" />
        </RadioGroup>
        <Button variant="contained" color="primary" onClick={() => this.fetchData()}>
          Search
        </Button>
      </div>
    );
  }
}

export default SearchFilter;

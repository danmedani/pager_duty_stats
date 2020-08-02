'use strict';

import React from 'react';
import OauthPopup from 'react-oauth-popup';
import isPagerDutyApiTokenValid from './api'
import ReactDOM from 'react-dom';
import { CircularProgress, Button } from '@material-ui/core';

const e = React.createElement;

const onCode = (code, params) => {
  console.log("wooooo a code", code);
  console.log("alright! the URLSearchParams interface from the popup url", params);
}
const onClose = () => {
  console.log("closed!");
}

class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      apiKeyError: '',
      pagerDutyToken: '',
      oauth_url: ''
    };

    var pagerDutyToken = localStorage.getItem('pager_duty_token') || '';
    if (pagerDutyToken !== '' && isPagerDutyApiTokenValid(pagerDutyToken)) {
      this.state.pagerDutyToken = pagerDutyToken;
      localStorage.setItem('pager_duty_token', pagerDutyToken);
    } else {
      
    }
  }

  render() {
    return (
        <div>
          {!this.state.pagerDutyToken 
            ?
            <div id="home-button">
              <OauthPopup
                url={this.state.oauth_url}
                onCode={onCode}
                onClose={onClose}
              >
                <Button variant="contained" color="primary">
                  Pager Duty Oauth 
                </Button>
              </OauthPopup>
            </div>
            :
            <CircularProgress />
          }
        </div>
    );
  }
}

const domContainer = document.querySelector('#main_container');
ReactDOM.render(e(HomePage), domContainer);

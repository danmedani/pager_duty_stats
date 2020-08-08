'use strict';

require("regenerator-runtime/runtime");

import React from 'react';
import OauthPopup from 'react-oauth-popup';
// import { generateCodePackagePromise } from '../logic/crypto';
import { auth } from '../logic/crypto';
import ReactDOM from 'react-dom';
import { CircularProgress, Button } from '@material-ui/core';
// import { isPagerDutyApiTokenValid } from '../logic/api';

const CLIENT_ID = '8f009107530c47f2bab6dc74dbe52f17630276894645e8d1c7b1de22c00a57ca'
const REDIRECT_URL = window.location.href

const e = React.createElement;


const onCode = (code, params) => {
  console.log("wooooo a code", code);
  console.log('oauth_code_verifer', sessionStorage.getItem('code_verifier'));
  console.log('REDIRECT_URL', REDIRECT_URL); 

  // this.state.authing = true;
  var token_url = 'https://app.pagerduty.com/oauth/token?grant_type=authorization_code&client_id='+
    CLIENT_ID+'&redirect_uri='+REDIRECT_URL+'&code='+code+'&code_verifier='+sessionStorage.getItem('code_verifier');
  console.log("token_url ", token_url);
  fetch(
    token_url,
    {
      method: 'POST'
    }
  ).then(res => res.json())
  .then(
    (result) => {
      localStorage.setItem("pager-duty-token", result.access_token);
    },
    (error) => {
      console.log('error!!! ' + error);
    }
  )

}
const onClose = () => {
  console.log("closed!");
}

class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      apiKeyError: '',
      oauth_url: '',
      authing: false
    };

    // const urlParams = new URLSearchParams(window.location.search);
    // if (urlParams.get('code')) {
    //   console.log('ayoooooo');
    // }

  }

  async componentDidMount() {
    var authUrl = await auth();
    this.setState({ oauth_url: authUrl });
  }

  render() {
    return (
        <div>
          {this.state.oauth_url && !this.state.authing
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

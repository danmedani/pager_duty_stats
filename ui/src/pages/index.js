'use strict';

require("regenerator-runtime/runtime");

import React from 'react';
import OauthPopup from 'react-oauth-popup';
// import { generateCodePackagePromise } from '../logic/crypto';
import { auth } from '../logic/crypto';
import ReactDOM from 'react-dom';
import { CircularProgress, Button } from '@material-ui/core';
import { isOauthTokenValid } from '../logic/api';

const CLIENT_ID = '8f009107530c47f2bab6dc74dbe52f17630276894645e8d1c7b1de22c00a57ca'
const REDIRECT_URL = window.location.href

const e = React.createElement;


// const onCode = (code, params) => {
//   var token_url = 'https://app.pagerduty.com/oauth/token?grant_type=authorization_code&client_id='+
//     CLIENT_ID+'&redirect_uri='+REDIRECT_URL+'&code='+code+'&code_verifier='+sessionStorage.getItem('code_verifier');
//   fetch(
//     token_url,
//     {
//       method: 'POST'
//     }
//   ).then(res => res.json())
//   .then(
//     (result) => {
//       var valid = await isOauthTokenValid(result.access_token);
//       if (valid) {
//         localStorage.setItem("pager-duty-token", result.access_token);
//         window.location.href = '/stats';
//       }
//     },
//     (error) => {
//       console.log('error!!! ' + error);
//     }
//   )

// }
const onClose = () => {
  console.log("closed!");
}

class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      oauth_url: '',
      oauth_problem: false
    };

    this.onCode = this.onCode.bind(this);
  }

  async onCode(code, params) {
    var token_url = 'https://app.pagerduty.com/oauth/token?grant_type=authorization_code&client_id='+
    CLIENT_ID+'&redirect_uri='+REDIRECT_URL+'&code='+code+'&code_verifier='+sessionStorage.getItem('code_verifier');

    try {
      var tokenData = await fetch(token_url, {method: 'POST'});
      var valid = await isOauthTokenValid(tokenData.access_token);
      if (valid) {
        localStorage.setItem("pager-duty-token", tokenData.access_token);
        window.location.href = '/stats';
      } else {
        console.log('not vlid');
        this.setState({ oauth_problem: true });
      }
    } catch(e) {
      console.log('exception!', e);
      this.setState({ oauth_problem: true });
    }
  }

  async componentDidMount() {
    var existingToken = localStorage.getItem("pager-duty-token") || '';
    if (existingToken !== '' && await isOauthTokenValid(existingToken)) {
        window.location.href = '/stats';
    } else {
      var authUrl = await auth();
      this.setState({ oauth_url: authUrl });
    }
  }

  render() {
    return (
        <div>
          {this.state.oauth_problem
            ?
            <div id="home-button">
              <p>
                There was some kind of problem with OAuth, sorry.
              </p>
            </div>
            :
            this.state.oauth_url && !this.state.oauth_problem
              ?
              <div id="home-button">
                <OauthPopup
                  url={this.state.oauth_url}
                  onCode={this.onCode}
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

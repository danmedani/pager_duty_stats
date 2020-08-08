import { handleErrors } from './errors';

async function isPagerDutyApiTokenValid(pagerDutyApiToken) {
  fetch('/api/auth?pd_api_key=' + pagerDutyApiToken)
    .then(handleErrors)
    .then(result => result.json())
    .then(
      (result) => {
        if (result.status === 'valid') {
          return true;
        }
      },
      (error) => {
        return false;
      }
    )
}

export { isPagerDutyApiTokenValid };

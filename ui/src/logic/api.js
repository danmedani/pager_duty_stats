async function isOauthTokenValid(bearerToken) {
  try {
    await fetch('/api/auth', {
      headers: {
        'Authorization': bearerToken
      }
    })
  } catch(e) {
    return false;
  }
  return true;
}

async function getTeams(bearerToken) {
  return fetch('/api/teams', {
    headers: {
      'Authorization': bearerToken
    }
  }).then(res => res.json())
}

async function getServices(bearerToken) {
  return fetch('/api/services', {
    headers: {
      'Authorization': bearerToken
    }
  }).then(res => res.json())
}

async function getChart(data, bearerToken) {
  return fetch('/api/chart', {
    headers: {
      'Authorization': bearerToken,
      'Content-Type': 'application/json'
    },
    method: 'POST',
    body: JSON.stringify(data)
  }).then(res => res.json())
}

export { isOauthTokenValid, getServices, getTeams, getChart };


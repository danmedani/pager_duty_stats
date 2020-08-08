async function isOauthTokenValid(bearerToken) {
  console.log('hi');
  try {
    await fetch('/api/auth', {
      headers: {
        'Authorization': 'Bearer ' + bearerToken,
        'Accept': 'application/vnd.pagerduty+json;version=2'
      }
    })
  } catch(e) {
    return false;
  }
  return true;
}

export { isOauthTokenValid };

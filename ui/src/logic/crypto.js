/**
 * Mostly taken from https://github.com/PagerDuty-Samples/pagerduty-bulk-user-mgr-sample/blob/master/js/auth.js, with small tweaks.
 */

const CLIENT_ID = '8f009107530c47f2bab6dc74dbe52f17630276894645e8d1c7b1de22c00a57ca'
const REDIRECT_URL = window.location.href

function gen128x8bitNonce() {
  const array = new Uint8Array(128); //( generate 1024bits 8*128
  window.crypto.getRandomValues(array);
  return array;
};
// hash verifier
async function digestVerifier(vString) {
  const encoder = new TextEncoder();
  const verifier = encoder.encode(vString);
  const hash = await crypto.subtle.digest('SHA-256', verifier);
  return hash;
}

function base64Unicode(buffer) {
  /*\
  |*|
  |*|  Base64 / binary data / UTF-8 strings utilities (#1)
  |*|
  |*|  https://developer.mozilla.org/en-US/docs/Web/API/WindowBase64/Base64_encoding_and_decoding
  |*|
  |*|  Author: madmurphy
  |*|
  \*/
  const uint6ToB64 = function(nUint6) {

      return nUint6 < 26 ?
          nUint6 + 65 :
          nUint6 < 52 ?
          nUint6 + 71 :
          nUint6 < 62 ?
          nUint6 - 4 :
          nUint6 === 62 ?
          43 :
          nUint6 === 63 ?
          47 :
          65;

  }
  const base64EncArr = function(aBytes) {

      let eqLen = (3 - (aBytes.length % 3)) % 3,
          sB64Enc = "";

      for (let nMod3, nLen = aBytes.length, nUint24 = 0, nIdx = 0; nIdx < nLen; nIdx++) {
          nMod3 = nIdx % 3;
          /* Uncomment the following line in order to split the output in lines 76-character long: */
          /*
          if (nIdx > 0 && (nIdx * 4 / 3) % 76 === 0) { sB64Enc += "\r\n"; }
          */
          nUint24 |= aBytes[nIdx] << (16 >>> nMod3 & 24);
          if (nMod3 === 2 || aBytes.length - nIdx === 1) {
              sB64Enc += String.fromCharCode(uint6ToB64(nUint24 >>> 18 & 63), uint6ToB64(nUint24 >>> 12 & 63), uint6ToB64(nUint24 >>> 6 & 63), uint6ToB64(nUint24 & 63));
              nUint24 = 0;
          }
      }

      return eqLen === 0 ?
          sB64Enc :
          sB64Enc.substring(0, sB64Enc.length - eqLen) + (eqLen === 1 ? "=" : "==");
  };
  let encodedArr =  base64EncArr(new Uint8Array(buffer));
  // manually finishing up the url encoding fo the encodedArr
  encodedArr = encodedArr.replace(/\+/g, '-')
              .replace(/\//g, '_')
              .replace(/=/g, '');
  return encodedArr;
}

async function auth() {
  // generate code verifier
  const generatedCode = gen128x8bitNonce();
  // base64 encode code_verifier
  const codeVerifier = base64Unicode(generatedCode.buffer);        
  // save code_verifier
  sessionStorage.setItem('code_verifier', codeVerifier);
  // generate the challenge from the code verifier
  const challengeBuffer =  await digestVerifier(codeVerifier);
  // base64 encode the challenge
  const challenge = base64Unicode(challengeBuffer);        
  // build authUrl
  const authUrl = `https://app.pagerduty.com/oauth/authorize?` +
                      `client_id=${CLIENT_ID}&` +
                      `redirect_uri=${REDIRECT_URL}&` + 
                      `response_type=code&` +
                      `code_challenge=${encodeURI(challenge)}&` + 
                      `code_challenge_method=S256`;

  // document.getElementById("pd-auth-button").href = authUrl;
  return authUrl;
}

export { auth };
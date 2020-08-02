/*
 * Copied from https://developer.pagerduty.com/docs/app-integration-development/oauth-2-pkce/
 */
function generateCodePackagePromise() {
    var base64Url = function(buffer) {
          /*
          |*|
          |*|  Base64 / binary data / UTF-8 strings utilities (#1)
          |*|  Based on Code From:
          |*|  https://developer.mozilla.org/en-US/docs/Web/API/WindowBase64/Base64_encoding_and_decoding
          |*|
          |*|  Author: madmurphy
          |*|
          */

        var uint6ToB64 = function(nUint6) {

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

        var base64EncArr = function(aBytes) {

            var eqLen = (3 - (aBytes.length % 3)) % 3,
                sB64Enc = "";

            for (var nMod3, nLen = aBytes.length, nUint24 = 0, nIdx = 0; nIdx < nLen; nIdx++) {
                nMod3 = nIdx % 3;
                /* Uncomment the following line in order to split the output in lines 76-character long: */
                /*
                  if (nIdx > 0 && (nIdx * 4 / 3) % 76 === 0) { sB64Enc += "r"; }
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


        var base64 = base64EncArr(new Uint8Array(buffer));
        var base64url_no_padding = base64.replace(/+/g, '-')
              .replace(///g, '_')
              .replace(/=/g, '');

        return base64url_no_padding;
    }
    var gen128x8bitNonce = function() {
        var array = new Uint8Array(128); //( generate 1024bits 8*128
        window.crypto.getRandomValues(array);
        return array;
    };

    var code_verifier = gen128x8bitNonce();

    /*
       Note : We consider the code_verifier used for the purpose
       of generating a hash to be in the base64_url_no_padding format
       Since any random sequence of 1024bits can be mapped into a base64
       encoding and the standard recommends the code_verifier be specified
       in terms of the characters that base64_url_no_padding is made up
       of - the most effective way to create a code_verifier is by not
       generating a random sequence of the base64 characters but simply
       generate a 1024bit number sequence and convert it to base64 string.
    */
    var base64_verifier = base64Url(code_verifier.buffer);
    var encoder = new TextEncoder();
    var base64_arraybuffer = encoder.encode(base64_verifier);

    return crypto.subtle.digest("SHA-256", base64_arraybuffer).then(function(code_challenge){

        return {
            code_verifer: base64_verifier,
            code_challenge: base64Url(code_challenge),
            code_challenge_method: "S256"
        }
    });
  }
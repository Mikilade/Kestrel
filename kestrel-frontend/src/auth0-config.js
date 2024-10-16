const domain = process.env.REACT_APP_AUTH0_DOMAIN;
const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;
const audience = process.env.REACT_APP_AUTH0_AUDIENCE;

if (!domain || !clientId) {
  throw new Error('Missing Auth0 configuration. Check your .env file.');
}

export const auth0Config = {
  domain,
  clientId,
  audience, // This is optional, so we don't check for its presence
  redirectUri: window.location.origin,
};
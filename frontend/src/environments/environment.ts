export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'coffee-shop-app.eu', // the auth0 domain prefix
    audience: 'http://coffee-shop-app', // the audience set for the auth0 app
    clientId: 'B49syElrpSchGc3hz7vjfb0bdptUVLsm', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:8100', // the base url of the running ionic application. 
  }
};

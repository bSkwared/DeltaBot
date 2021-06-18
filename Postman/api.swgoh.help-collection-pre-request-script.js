const obj = {
    "username": pm.environment.get("USERNAME"),
    "password": pm.environment.get("PASSWORD"),
    "grant_type": "password",
    "client_id": "foo",
    "client_secret": "bar"
};

const payload = Object.keys(obj).reduce((acc, cur) => {
    return `${acc}${cur}=${obj[cur]}&`;
}, '');
pm.environment.set('auth_payload', payload);

const postRequest = {
    url: 'https://api.swgoh.help/auth/signin',
    method: 'POST',
    header: {
        "content-type": "application/x-www-form-urlencoded"
        },
    body: {
      mode: 'raw',
        raw: pm.environment.get("auth_payload")
    }
  }; 
  pm.sendRequest(postRequest, (error, response) => {
      console.log(error ? error : response.json());
      var response_json = response.json();
      pm.environment.set("token", response_json.access_token);
});

# Basic setup for Postman application

## Getting the Postman application

Postman is a collaboration platform for API development. Postman's features simplify each step of building an API and
streamline collaboration so you can create better APIs—faster. For our use case we will use it to become familiar with
the api.swgoh.help API.

It can be downloaded [here](https://www.postman.com/downloads/)

### How to use these files

This folder contains two JSON files that can be imported into the Postman application.

The first file is [swgoh_api-postman_environment_template.json](swgoh_api-postman_environment_template.json). This file should be imported into Postman first since
it creates a separate environment for requests to the api.swgoh.help API. Before importing the file you should edit it
for your specific api.swgoh.help username and password.

```		
                {
			"key": "USERNAME",
			"value": "API_USERNAME_GOES_HERE",
			"enabled": true
		},
		{
			"key": "PASSWORD",
			"value": "API_PASSWORD_GOES_HERE",
			"enabled": true
		}
```

The second file is [api.swgoh.help.postman_collection.json](api.swgoh.help.postman_collection.json). This file should be imported into the new environment
created by the import above. This Postman Collection file contains a few simple example requests to help get you started
working with the api.swgoh.help API.

Once the Postman environment and collection have been imported, the contents of the 
[api.swgoh.help-collection-pre-request-script.js](api.swgoh.help-collection-pre-request-script.js) file should be placed in the Postman collection Pre-request script field.
This step is essential as it contains the login code needed to access the API and store the session information in the 
Postman environment global variables that are used by the queries in the collection.

For more information about importing configuration into the Postman application, please see their online
documentation [here](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/)
.

The imported Postman Collection provides an example of how to:

- get a list of all the available characters and ships a player could possibly obtain
- get the complete guild membership of a list of player allycodes
- get the complete player data for a list of allycodes

**CAUTION**: the api.swgoh.help API has rate limits and can become overloaded during heavy use. It is best to limit the
number of allycodes sent in a single list to 20 or less.
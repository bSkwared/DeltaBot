# api_swgoh_help
Python wrapper for the API at https://api.swgoh.help/

This implementation is based upon the work done by platzman (python module) and 
shittybill (node.js interface)

## Description

This wrapper attempts to provide an easy to use interface for the Star Wars Galaxy 
of Heros game data API available at https://api.swgoh.help/. In order to use the API
you must first register for an account at https://api.swgoh.help/signup

The 'settings' class is used to store all of the API specific values that may need
to be changed during runtime or require unique values per instance. The most basic
of these values are the required 'username' and 'password' entries. The 'settings'
class instance is then passed to the api_swgoh_help client instance.

The primary method provided by the api_swgoh_help class is fetchAPI(). This method
takes two parameters. The first parameter is the endpoint URL to call, for example 
'/swgoh/data'. The second parameter is a standard python dictionary containing the
parameters needed for the desired endpoint. The dictionary is converted to a JSON 
string to send in the body of the HTTP POST sent to the API. The fetchAPI() method
automatically manages the Authorization token issued by the API upon successful
login during the initial request.

There are also wrapper methods for each of the published API endpoints. Each of 
the helper methods call the primary fetchAPI() method while also providing some
common defaults to make usage easier. The helper methods are:

- fetchZetas()
- fetchSquads()
- fetchBattles()
- fetchEvents()
- fetchData()
- fetchPlayers()
- fetchGuilds()
- fetchUnits()
- fetchRoster()

Each helper method, with the exception of fetchZetas() and fetchSquads(), takes a single
parameter. Typically, the parameter is a python dictionary containing the API parameters
needed for the specific endpoint called. In some cases where no parameter is supplied
a generic default is constructed. Certain helper methods also accept integer or list
input. For example, if you call the fetchPlayers() method with an integer parameter,
it is assumed to be an allycode. The necessary dictionary is constructed around that
allycode and then submitted to the API.

## Usage

```
from api_swgoh_help import api_swgoh_help, settings
creds = settings('your_username','your_password')
client = api_swgoh_help(creds)

allycodes = [1234567879,987654321]

players = client.fetchPlayers(allycodes)

for player in players:
    print("Name: {0} ({1}) level: {2} - Guild: {3}".format(player['name'], player['allyCode'], player['level'], player['guildName']))
```

## Example Code

The [get-guild-allycodes.py](examples/get-guild-allycodes.py) file will collect a list of
guild member allycodes. Update the script with an API username, password and the allycode of
a guild member before executing.

The [swgoh-sample.py](examples/swgoh-example.py) file is a collection of example code to illustrate
usage of various API endpoints. It is not intended to be run as is. 

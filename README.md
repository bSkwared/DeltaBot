<<<<<<< HEAD
<<<<<<< HEAD
# api_swgoh_help
<<<<<<< HEAD
Python code for the API at https://api.swgoh.help/
Api is developed pretty fast so follow it's documentation for changes, I would be able to update this code only irregularly.
=======
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
>>>>>>> 9a89f07 (Parse mods into db as well)

## Usage

          creds = settings('your_username','your_password')
          client = SWGOHhelp(creds)

#careful, allycode is integer, not string
          
          allycode = 997393984

          player = client.get_data('player',allycode)
          print(player)

          guild = client.get_data('guild',allycode)
          print(guild)

          units = client.get_data('units',allycode)
          print(units)

          battles = client.get_data('battles',allycode)
          print(battles)

<<<<<<< HEAD
#data is different - there the second value is not allycode but chosen collection name:
          
          data = client.get_data('data','abilityList')
          print(data)

#currently valid collections:
          
          abilityList
          battleEnvironmentsList
          battleTargetingRuleList
          categoryList
          challengeList
          challengeStyleList
          effectList
          environmentCollectionList
          equipmentList
          eventSamplingList
          guildExchangeItemList
          guildRaidList
          helpEntryList
          materialList
          playerTitleList
          powerUpBundleList
          raidConfigList
          recipeList
          requirementList
          skillList
          starterGuildList
          statModList
          statModSetList
          statProgressionList
          tableList
          targetingSetList
          territoryBattleDefinitionList
          territoryWarDefinitionList
          unitsList
          unlockAnnouncementDefinitionList
          warDefinitionList
          xpTableList

# Available Language Clients

* JavaScript: https://github.com/r3volved/api-swgoh-help
* Java: https://github.com/j0rdanit0/api-swgoh-help
=======
The [swgoh-sample.py](examples/swgoh-example.py) file is a collection of example code to illustrate
usage of various API endpoints. It is not intended to be run as is.
=======
# Delta Bot
>>>>>>> 11cad47 (Delete Postman directory and move all files to a tmp folder to cleanup later)


blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
ls: dev.db: No such file or directory
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ python3.11 test_db.py guild_player_stats.json
2022-12-18 23:48:26.681067+00:00
creating new guild
Finished all players in 0:00:31.445122
Averaged 0:00:00.655107 per player
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
-rw-r--r--  1 blasky  staff  5025792 Dec 18 15:48 dev.db
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ python3.11 test_db.py guild_player_stats_12_18_22.json
2022-12-18 23:49:07.197324+00:00
foundu guild in db
Finished all players in 0:00:22.986805
Averaged 0:00:00.478892 per player
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
-rw-r--r--  1 blasky  staff  5144576 Dec 18 15:49 dev.db
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$
>>>>>>> f3baf64 (Pulled new data, reverted the file to be just logging player data)
=======
# DeltaBot



>>>>>>> ae5e816 (Move python code into deltabot package)

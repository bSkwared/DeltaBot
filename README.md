# api_swgoh_help
Python code for the API at https://api.swgoh.help/
Api is developed pretty fast so follow it's documentation for changes, I would be able to update this code only irregularly.

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


blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
ls: dev.db: No such file or directory
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ vi ally_passwd.txt
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ python3.11 ./test_db.py
2022-12-18 13:17:28.051820+00:00
creating new guild
Finished all players in 0:00:10.635984
Averaged 0:00:00.221583 per player
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
-rw-r--r--  1 blasky  staff  2797568 Dec 18 05:17 dev.db
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ vi ./test_db.py
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ python3.11 ./test_db.py
2022-12-18 13:17:58.234526+00:00
foundu guild in db
Finished all players in 0:00:05.091645
Averaged 0:00:00.106076 per player
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$ ls -l dev.db
-rw-r--r--  1 blasky  staff  2846720 Dec 18 05:18 dev.db
(venv)
blasky at blasky--MacBookPro18 in ~/swgoh/api_swgoh_help (master●●)
$
>>>>>>> f3baf64 (Pulled new data, reverted the file to be just logging player data)

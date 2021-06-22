#!/usr/bin/env python3

import json

from api_swgoh_help import api_swgoh_help, settings

# Initialize data structures
toons = {}
skills = {}
abilities = {}
gear = {}

# Change the settings below
creds = settings('JohnDoe', 'password')
client = api_swgoh_help(creds)

allycodes = [123456789]

# Build local list of obtainable characters
payload = {}
payload['collection'] = "unitsList"
payload['language'] = "eng_us"
payload['enums'] = True
payload['match'] = {"rarity": 7,
                    "obtainable": True,
                    "obtainableTime": 0
                    }
payload['project'] = {"baseId": 1,
                      "nameKey": 1,
                      "descKey": 1,
                      "forceAlignment": 1,
                      "categoryIdList": 1,
                      "combatType": 1
                      }
units = client.fetchData(payload)

for unit in units:
    toons[unit['baseId']] = unit

# Build local skills list
payload = {}
payload['collection'] = "skillList"
payload['language'] = "eng_us"
payload['enums'] = True
payload['project'] = { "id": 1,
                       "abilityReference": 1,
                       "isZeta": 1
                       }
items = client.fetchData(payload)

for skill in items:
    skills[skill['id']] = skill

# Build local abilities list
# skills[id]['abilityReference'] -> abilities[id]
payload = {}
payload['collection'] = "abilityList"
payload['language'] = "eng_us"
payload['enums'] = True
payload['project'] = { "id": 1,
                       "type": 1,
                       "nameKey": 1
                       }
items = client.fetchData(payload)
for ability in items:
    abilities[ability['id']] = ability['nameKey']

# Build local gear list
payload = {}
payload['collection'] = "equipmentList"
payload['language'] = "eng_us"
payload['enums'] = True
payload['project'] = {"id": 1,
                      "nameKey": 1
                      }
items = client.fetchData(payload)
for item in items:
    gear[item['id']] = item['nameKey']

payload = {}
payload['allycodes'] = allycodes
payload['language'] = "eng_us"
payload['enums'] = True
# Remove the project payload element to retrieve the player's entire roster
payload['project'] = { "name": 1 }

# Fetch player information (one or more allycodes in a list)
players = client.fetchPlayers(allycodes)

# Fetch a list of guild member allycodes
allycodes = [123456789, 987654321]
guild_allycodes = client.fetchGuilds(allycodes)

# Fetch a list of ranked zeta recommendations
zetas = client.fetchZetas()

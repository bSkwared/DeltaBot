
import datetime
import config
import os

import json
from swgoh_comlink import SwgohComlink
import requests
import urllib.request





date_name = datetime.datetime.now().strftime("%Y_%m_%d.py")
data_file = os.path.join(config.DAILY_DATA_DIR, date_name)
print(date_name)
print(data_file)



def get_guild_data(gID):
    for _ in range(3):
        guild = comlink.get_guild(gID)
        if isinstance(guild, dict) and 'member' in guild:
            return guild

    return {}

def get_player_data(pID=None, allycode=None):
    for _ in range(3):
        if pID:
            player = comlink.get_player(player_id=pID)
        else:
            assert allycode
            player = comlink.get_player(allycode)
        if isinstance(player, dict) and 'rosterUnit' in player:
            return player
    assert False, f'Unable to load player data for {pID}'

comlink = SwgohComlink(url='http://localhost:3200')
player_data = get_player_data(allycode=config.allycode)
guild_id = player_data['guildId']


speed_stat_id = 5




raw_guild_data = get_guild_data(guild_id)
rote_stars = -1
for event in raw_guild_data['profile']['guildEventTracker']:
    if event['definitionId'] == 't05D':
        rote_stars = int(event['completedStars'])
        break

data = {
    'date': f'{datetime.datetime.now()}',
    'guild_name': raw_guild_data['profile']['name'],
    'rote_stars': rote_stars,
    'guild_members': {
    }

}

players = {}
for p in raw_guild_data['member']:
    raw_player_data = get_player_data(p['playerId'])
    player_data = {
        'name': raw_player_data['name'],
        'char_gp': -1,
        'ship_gp': -1,
    }

    stats = raw_player_data['profileStat']
    for stat in stats:
        if stat['nameKey'] == 'STAT_CHARACTER_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['char_gp'] = int(stat['value'])
        if stat['nameKey'] == 'STAT_SHIP_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['ship_gp'] = int(stat['value'])

    data['guild_members'][raw_player_data['allyCode']] = player_data

with open(data_file, 'w') as fp:
    json.dump(data, fp, indent=2)


'''
(Pdb) players['DKbtMTD4TJm-QQS3Pvkq0w'].keys()
dict_keys(['rosterUnit', 'profileStat', 'pvpProfile', 'unlockedPlayerTitle', 'unlockedPlayerPortrait', 'seasonStatus', 'datacron', 'name', 'level', 'allyCode', 'playerId', 'guildId', 'guildName', 'guildLogoBackground', 'guildBannerColor', 'guildBannerLogo', 'selectedPlayerTitle', 'guildTypeId', 'localTimeZoneOffsetMinutes', 'lastActivityTime', 'selectedPlayerPortrait', 'lifetimeSeasonScore', 'playerRating'])
'''












import sys
sys.exit(0)








'''
* INDIVIDUAL *
Char GP
Ship GP
all roster number of mods with each speed
GAC rank

GP of top 100 characters (sorted by GP)
number of mods with each speed on top 100 characters

raid damage
list of GLs


* GUILD *
allycodes of all members
tw scores
raid total damage




version 1.1 additions
IND
all toons and gear/relic level





version 1.0
IND
ship GP
char GP

GUILD
tb stars
allycodes of all members


'''



'''
    (Pdb) player.keys()
dict_keys(['rosterUnit', 'profileStat', 'pvpProfile', 'unlockedPlayerTitle', 'unlockedPlayerPortrait', 'seasonStatus', 'datacron', 'name', 'level', 'allyCode', 'playerId', 'guildId', 'guildName', 'guildLogoBackground', 'guildBannerColor', 'guildBannerLogo', 'selectedPlayerTitle', 'guildTypeId', 'localTimeZoneOffsetMinutes', 'lastActivityTime', 'selectedPlayerPortrait', 'lifetimeSeasonScore', 'playerRating'])

'''
'''
speed_list = []
for toon in player_data['rosterUnit']:
    for mod in toon['equippedStatMod']:
        for secondary in mod['secondaryStat']:
            if secondary['stat']['unitStatId'] != 5:
                continue
            speed_list.append(int(secondary['stat']['statValueDecimal'])/10000)


char_gp = None
for stat in player_data['profileStat']:
    if stat['nameKey'] == 'STAT_CHARACTER_GALACTIC_POWER_ACQUIRED_NAME':
        char_gp = int(stat['value'])

print(len(speed_list))
print(modscore(speed_list, char_gp))
oo

def modscore(speed_list, char_gp):
    total = 0
    for speed in speed_list:
        if speed <= 10:
            continue

        total += -6.3058820272303500e+000 * (speed**0) \
               +  1.3035991984201347e+000 * (speed**1) \
               + -9.6654093848707642e-002 * (speed**2) \
               +  2.7728738967038821e-003 * (speed**3)


'''

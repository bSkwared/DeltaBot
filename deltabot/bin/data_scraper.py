
import datetime
import config
import os

import json
from swgoh_comlink import SwgohComlink
import requests
import urllib.request





date_name = datetime.datetime.now().strftime("%Y_%m_%d.py")
data_file = os.path.join(config.DAILY_DATA_DIR, date_name)

yesterday_name = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y_%m_%d.py")
yesterday_file = os.path.join(config.DAILY_DATA_DIR, yesterday_name)

print(date_name)
print(data_file)
print(yesterday_file)
unit_to_idx = {}
unit_file = os.path.join(config.DAILY_DATA_DIR, 'unit_to_idx.py')

yesterday_tickets = {}
try:
    with open(yesterday_file, 'r') as fp:
        yesterday_data = json.load(fp)
except:
    pass

for ac, player in yesterday_data['guild_members'].items():
    try:
        yesterday_tickets[ac] = {'today_tickets': player['today_tickets'], 'total_tickets': player['total_tickets']}
    except:
        pass

try:
    with open(unit_file, 'r') as fp:
        unit_to_idx = json.load(fp)
except:
    pass

idx_to_unit = {}
for unit, idx in unit_to_idx.items():
    idx_to_unit[idx] = unit

next_idx = (max(idx_to_unit.keys()) + 1) if idx_to_unit else 0



def get_guild_data(gID):
    for _ in range(3):
        guild = comlink.get_guild(gID, include_recent_guild_activity_info=True)
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
    },
    'krayt_damage': -1,
    'endor_damage': -1,
}

pid_raid_damage = {}
cur_raid_id = None
assert len(raw_guild_data['recentRaidResult']) <= 1
for raid in raw_guild_data['recentRaidResult']:
    if raid['raidId'] == 'kraytdragon':
        cur_raid_id = 'krayt_damage'
    elif 'endor' in raid['raidId']:
        cur_raid_id = 'endor_damage'

    if cur_raid_id in data:
        data[cur_raid_id] = int(raid['guildRewardScore'])
        for member in raid['raidMember']:
            pid_raid_damage[member['playerId']] = int(member['memberProgress'])


players = {}
for p in raw_guild_data['member']:
    raw_player_data = get_player_data(p['playerId'])
    past_tickets = yesterday_tickets.get(raw_player_data['allyCode'], {})
    player_data = {
        'name': raw_player_data['name'],
        'char_gp': -1,
        'ship_gp': -1,
        'toon_stars': [],
        'toon_gears': [],
        'speed_mods': [0] * 40,
        'yesterday_tickets': past_tickets.get('today_tickets', -1),
        'yesterday_total_tickets': past_tickets.get('total', -1),
        'total_tickets': -1,
        'today_tickets': -1,
        'krayt_damage': -1,
        'endor_damage': -1,
    }
    for contribution in p['memberContribution']:
        if contribution['type'] == 2:
            player_data['today_tickets'] = int(contribution['currentValue'])
            player_data['total_tickets'] = int(contribution['lifetimeValue'])

    if cur_raid_id in player_data:
        player_data[cur_raid_id] = pid_raid_damage.get(p['playerId'], -1)

    guild = raw_guild_data
    #comlink.get_guild(guild_id, True)
    # guild['recentRaidResult'][0]['raidMember'][1]

    stats = raw_player_data['profileStat']
    for stat in stats:
        if stat['nameKey'] == 'STAT_CHARACTER_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['char_gp'] = int(stat['value'])
        if stat['nameKey'] == 'STAT_SHIP_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['ship_gp'] = int(stat['value'])

    data['guild_members'][raw_player_data['allyCode']] = player_data

    for unit in raw_player_data['rosterUnit']:
        unit_id, _ = unit['definitionId'].split(':')
        if unit_id not in unit_to_idx:
            unit_to_idx[unit_id] = next_idx
            idx_to_unit[next_idx] = unit_id
            next_idx += 1

        # When a new character is added increase this players arrays to be
        # long enough to contain those new characters
        for field in ('toon_stars', 'toon_gears'):
            if len(player_data[field]) < next_idx:
                player_data[field].extend([0] * (next_idx - len(player_data[field])))

        idx = unit_to_idx[unit_id]
        player_data['toon_stars'][idx] = unit['currentRarity']

        # ships have ['relic'] == None, but ['currentTier'] == 1
        total_gear_level = unit.get('currentTier', 0)
        if isinstance(unit['relic'], dict):
            total_gear_level += unit['relic'].get('currentTier', 0)
        player_data['toon_gears'][idx] = total_gear_level

        for mod in unit['equippedStatMod']:
            has_speed = False
            for secondary in mod['secondaryStat']:
                if secondary['stat']['unitStatId'] != 5:
                    continue
                has_speed = True
                player_data['speed_mods'][int(secondary['stat']['statValueDecimal'])//10000] += 1
            if not has_speed and mod['primaryStat']['stat']['unitStatId'] != 5:
                player_data['speed_mods'][0] += 1
        

with open(data_file, 'w') as fp:
    json.dump(data, fp, indent=2)

with open(unit_file, 'w') as fp:
    json.dump(unit_to_idx, fp, indent=2)

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

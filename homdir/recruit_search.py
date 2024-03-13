
import re
import sys
import datetime
import os

import json
from swgoh_comlink import SwgohComlink


GL_FILEPATH = '/tmp/recruit_GLs.json'
seen_allies = {}
with open('seen_allies.json', 'r') as fp:
    seen_allies = json.loads(fp.read())


allycode = re.compile(r'(\d{9})')
ally_url = re.compile(r'https://swgoh.gg/p/(\d{9})/')
guild_url = re.compile(r'https://swgoh.gg/g/([A-Za-z0-9_-]*)/')

if len(sys.argv) != 2:
    print(f'Invalid args, expected just one allycode: {sys.argv}')
    sys.exit(1)

comlink = SwgohComlink(url='http://localhost:3200')

guild_id = ''
if allycode.match(sys.argv[1]) or ally_url.match(sys.argv[1]):
    acmatch = allycode.match(sys.argv[1])
    aumatch = ally_url.match(sys.argv[1])
    if acmatch:
        ac = acmatch.group(1)
    else:
        assert aumatch
        ac = aumatch.group(1)
    print(f'fetching allycode="{ac}"')
    player_data = comlink.get_player(ac)
    if not isinstance(player_data, dict):
        print(f'player_data {type(player_data)} is not a dict')
    if player_data.get('code'):
        print(player_data)
        print('rip')
        sys.exit(1)


    guild_id = player_data['guildId']
elif guild_url.match(sys.argv[1]):
    guild_id = guild_url.match(sys.argv[1]).group(1)
    print(f'guild_id: {guild_id}')
else:
    assert False, f'invalid argument {sys.argv[1]}'

assert guild_id, f'Unable to determine guild id'






galactic_legends = dict()
try:
    with open(GL_FILEPATH, 'r') as fp:
        galactic_legends = json.loads(fp.read())
    if not isinstance(galactic_legends, dict) or len(galactic_legends.keys()) < 8:
        print(f'loaded non-dict, or too small {galactic_legends}')
        raise Exception('bad GL saved data')

except:
    journey_guides = set()
    units = comlink.get_game_data(include_pve_units=False, request_segment=4)
    layouts = units['unitGuideLayout']
    for layout in layouts:
        for layoutTier in layout['layoutTier']:
            for line in layoutTier['layoutLine']:
                for unit in line['unitGuideId']:
                    print(unit)
                    if layout['id'] == 'GALACTIC_LEGENDS':
                        galactic_legends[unit] = True
    with open(GL_FILEPATH, 'w') as fp:
        fp.write(json.dumps(galactic_legends, indent=2))
GI = 'GRANDINQUISITOR'
REVA = 'THIRDSISTER'
gl_ships = {'CAPITALLEVIATHAN', 'CAPITALEXECUTOR', 'CAPITALPROFUNDITY'}


#guild_id = player_data['guildId']
guild = comlink.get_guild(guild_id, True)
# guild['recentRaidResult'][0]['raidMember'][1]

rote_stars = 0
for event in guild['profile']['guildEventTracker']:
    if event['definitionId'] == 't05D':
        rote_stars = int(event['completedStars'])
        break

guild_damage = 0
for raid in guild['recentRaidResult']:
    if raid['raidId'] != 'speederbike':
        continue
    try:
        guild_damage = int(raid['guildRewardScore']) // 1_000_000
    except:
        pass


print(f'**** {guild["profile"]["name"]}')
print(f'ROTE: {rote_stars}')
print(f'SBR: {guild_damage}M')

for p in guild['member']:
    '''
    (Pdb) guild['member'][0]['leagueId']
    'KYBER'
    (Pdb) guild['member'][0]['memberLevel']
    2
    (Pdb) guild['member'][0]['lastActivityTime']sys.exit(0)
    '''
    raw_player_data = comlink.get_player(player_id=p['playerId'])
    '''
    noon_time = (24 + 12 -5  - (raw_player_data["localTimeZoneOffsetMinutes"] // 60))
    while noon_time >= 24:
        noon_time -= 24
    last_energy = noon_time + 9
    while last_energy >= 24:
        last_energy -= 24
    print(f'{raw_player_data["name"]}: {noon_time}, {last_energy}')
    continue
    '''

    stats = raw_player_data['profileStat']
    gp = 0
    for stat in stats:
        if stat['nameKey'] == 'STAT_CHARACTER_GALACTIC_POWER_ACQUIRED_NAME':
            gp += int(stat['value'])
        if stat['nameKey'] == 'STAT_SHIP_GALACTIC_POWER_ACQUIRED_NAME':
            gp += int(stat['value'])

    fleet_rank = None
    for arena in raw_player_data['pvpProfile']:
        if arena['tab'] == 2:
            fleet_rank = arena['rank']
    GLs = []
    GLSHIPS = []
    has_gi = False
    has_reva = False
    gi_relic = 0
    for unit in raw_player_data['rosterUnit']:
        unit_id, _ = unit['definitionId'].split(':')
        if unit_id in galactic_legends:
            GLs.append(unit_id)
        if unit_id in gl_ships:
            GLSHIPS.append(unit_id)


        if unit_id == REVA:
            has_reva = True
        if unit_id == GI:
            has_gi = True
            if isinstance(unit['relic'], dict):
               gi_relic = unit['relic'].get('currentTier', 0) - 2

    if len(GLs) >= 3 and len(GLSHIPS) >= 1 and has_gi and not has_reva and gp > 8_000_000 and p['leagueId'] not in ('CARBONITE', 'BRONZIUM', 'CHROMIUM'):
        gp_str = str(round(gp, -4))[:-4]
        already_seen = raw_player_data['allyCode'] in seen_allies
        seen_allies[raw_player_data['allyCode']] = True
        gp_str = f'{gp_str[:-2]}.{gp_str[-2:]}'
        is_officer_or_leader = p['memberLevel'] in (3, 4)
        last_activity = datetime.datetime.fromtimestamp(int(p['lastActivityTime'])/1000)
        LAST_ACT = f'\n INACTIVE: {last_activity}' if int(p['lastActivityTime']) < 1697200000000 else ''
        seen_before = '\nSEEN BEFORE *******' if already_seen else ''
        ui_ac = f"{raw_player_data['allyCode'][:3]}-{raw_player_data['allyCode'][3:6]}-{raw_player_data['allyCode'][6:]}"
        ui_officer = '\nOFFICER ****' if is_officer_or_leader else ''
        print(f'''
=== {ui_ac}  |  {raw_player_data['name']} ==={LAST_ACT}{seen_before}{ui_officer}
{p["leagueId"]}, fleet: {fleet_rank}
gp: {gp_str}M
GLs: {' '.join(GLs)}
GL ships: {' '.join(GLSHIPS)}
gi_relic: {gi_relic} ''')



with open('seen_allies.json', 'w') as fp:
    fp.write(json.dumps(seen_allies, indent=2))
print('\n\n')

sys.exit(0)



speed_stat_id = 5





'''
players = {}
for p in raw_guild_data['member']:
    raw_player_data = get_player_data(p['playerId'])
    player_data = {
        'name': raw_player_data['name'],
        'char_gp': -1,
        'ship_gp': -1,
        'toon_stars': [],
        'toon_gears': [],
        'speed_mods': [0] * 40,
    }

    stats = raw_player_data['profileStat']
    for stat in stats:
        if stat['nameKey'] == 'STAT_CHARACTER_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['char_gp'] = int(stat['value'])
        if stat['nameKey'] == 'STAT_SHIP_GALACTIC_POWER_ACQUIRED_NAME':
            player_data['ship_gp'] = int(stat['value'])

    data['guild_members'][raw_player_data['allyCode']] = player_data

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

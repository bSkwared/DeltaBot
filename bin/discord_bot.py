import datetime
from loguru import logger as guru_log
import os
import asyncio
import config.config as config
import disnake
import json
from swgoh_comlink import SwgohComlink
import config.auth

import logging

logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='/tmp/disnake.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

guru_log.add("/tmp/deltabot.log", backtrace=True, diagnose=True)


BYPASS_GEAR_LEVEL = False
comlink = SwgohComlink(url='http://localhost:3200')
player_data = comlink.get_player(917787877)
player_data['name']
guild_id = player_data['guildId']
DELTABOT_TEST = 1062981461227077694
DELTABOT_PROD = 1063654416529494016
BS_TEST = 1062980772736286740
cur_chan = BS_TEST
cur_chan = DELTABOT_PROD
GLOBAL_PATH = '/home/server/source/DeltaBot/tmp/delta.json'
TMP_GLOBAL_PATH = f'{GLOBAL_PATH}.tmp'

GLOBAL = {'guild': [], 'players': {}, 'last_players': {}, 'unit_id_to_name' : {}, 'updates': {}, 'cur_seq': 0}
def log(msg):
    guru_log.info(f'{datetime.datetime.now()}: {msg}')

log(os.environ.get('BETTER_EXCEPTIONS'))

try:
    with open(GLOBAL_PATH, 'r') as fp:
        file_global = json.loads(fp.read())
    ng = {k: file_global.get(k, type(GLOBAL[k])()) for k in GLOBAL.keys()}
    GLOBAL = ng
except:
    log(f'Unable to load config from {GLOBAL_PATH}')

def update_unit_id_to_name():
    name_key_to_string = {}
    localization = comlink.get_localization(id=comlink.localization_version,
                                            unzip=True)['Loc_ENG_US.txt']
    for line in localization.splitlines():
        if line.strip().startswith('#'):
            continue
        else:
            k, v = line.split('|')
            name_key_to_string[k] = v

    

    id_to_name = {}
    units = comlink.get_game_data(include_pve_units=False)['units']
    for unit in units:
        unit_id, _ = unit['id'].split(':')
        id_to_name[unit_id] = name_key_to_string[unit['nameKey']]
        
    name_key_to_string = []

    GLOBAL['unit_id_to_name'] = id_to_name

def get_guild_data(gID):
    for _ in range(3):
        guild = comlink.get_guild(gID)
        if isinstance(guild, dict):
            return guild

    return {}

def update_guild():
    guild = get_guild_data(guild_id)
    if guild:
        GLOBAL['guild'] = guild

def get_player_data(pID):
    player = comlink.get_player(player_id=pID)
    roster = []
    if 'rosterUnit' not in player:
        try:
            log(f'blake keys: {player.keys()}')
        except:
            log(f'blake player: {player}')
    for c in player['rosterUnit']:
        toon = {k: c[k] for k in ('id', 'relic', 'definitionId', 'currentRarity', 'currentTier')}
        roster.append(toon)

    return {
            'name': player['name'],
            'rosterUnit': roster,
            'playerId': player['playerId']
    }

def update_players():
    players = {}
    for p in GLOBAL['guild']['member']:
        for _ in range(3):
            try:
                players[p['playerId']] = get_player_data(p['playerId'])
                break
            except Exception as e:
                log(f'blake breaking {e}')
                pass

    #GLOBAL['players'] = {p['playerId']: comlink.get_player(player_id=p['playerId']) for p in GLOBAL['guild']['member']}
    GLOBAL['players'] = players


class MyClient(disnake.Client):
    async def on_ready(self):
        log(f'Logged on as {self.user}!')
        channel = self.get_channel(cur_chan)
        if not isinstance(channel, disnake.TextChannel):
            raise ValueError("Invalid channel")
        #await channel.send("Bot starting")

        try:
            loop = asyncio.get_event_loop()

            last_players = {}
            players = {}
            GLOBAL['cur_seq'] = 0
            last_updated_names = -100
            GLOBAL['player_updates'] = {}
            # pID: {
            #     'last_updated': cur_seq,
            #     'toons': {
            #         'Toon name': {
            #             'initial_stars': 4,
            #             'initial_gear': 3,
            #             'initial_relic': 8,
            #         },
            #     },
            # }
            while True:
                GLOBAL['cur_seq'] += 1
                log('Poll for new update to guild and players')
                await loop.run_in_executor(None, update_guild)
                await loop.run_in_executor(None, update_players)
                #guild = comlink.get_guild(guild_id)
                #players = {p['playerId']: comlink.get_player(player_id=p['playerId']) for p in guild['member']}

                for npID, np in GLOBAL['players'].items():
                    lp = GLOBAL['last_players'].get(npID)
                    if lp == None:
                        # Don't print diff for new players
                        continue

                    msg = []
                    lp_roster = {c['id']: c for c in lp['rosterUnit']}
                    for c in np['rosterUnit']:
                        lc = lp_roster.get(c['id'])
                        d_split = c["definitionId"].split(":")[0]
                        if d_split not in GLOBAL['unit_id_to_name'] and last_updated_names + 100 < GLOBAL['cur_seq']:
                            log(f'Updating names since {d_split} not found in mapping')
                            last_updated_names = GLOBAL['cur_seq']
                            await loop.run_in_executor(None, update_unit_id_to_name)
                        unit_name = GLOBAL['unit_id_to_name'].get(d_split, d_split)

                        if (not lc 
                            or c['currentRarity'] != lc['currentRarity']
                            or c['currentTier'] != lc['currentTier']
                            or (c.get('relic') and lc.get('relic')
                                and lc['relic']['currentTier'] != c['relic']['currentTier'])):

                            update = GLOBAL['player_updates'].get(npID, {})
                            update['last_updated'] = GLOBAL['cur_seq']
                            toons = update.get('toons', {})
                            unit = toons.get(unit_name, {})
                            unit['initial_stars'] = min(lc['currentRarity'] if lc else 0,
                                                        unit.get('initial_stars', 999))
                            unit['initial_gear'] = min(lc['currentTier'] if lc else 0,
                                                       unit.get('initial_gear', 999))
                            try:
                                unit['initial_relic'] = min(max(0, lc['relic']['currentTier'] - 2
                                                               if (lc and lc.get('relic'))
                                                               else 0),
                                                            unit.get('initial_relic', 999))
                            except Exception as e:
                                guru_log.debug(e)
                                guru_log.debug(lc)
                                raise e
                            unit['latest_stars'] = c['currentRarity'] if c else 0
                            unit['latest_gear'] = c['currentTier'] if c else 0
                            unit['latest_relic'] = max(0, c['relic']['currentTier'] - 2
                                                           if (c and c.get('relic'))
                                                           else 0)
                            toons[unit_name] = unit
                            update['toons'] = toons
                            GLOBAL['player_updates'][npID] = update



                deleted_keys = []
                for pID, update in GLOBAL['player_updates'].items():
                    if update['last_updated'] + 3 > GLOBAL['cur_seq']:
                        continue

                    deleted_keys.append(pID)
                    pmsg = []
                    for name, stats in update['toons'].items():
                        msg = []
                        if stats['initial_stars'] == 0:
                            msg.append(f'Unlocked {name} at {stats["latest_stars"]} stars')
                            if stats['latest_gear'] > 1:
                                msg.append(f'Gear level: {stats["latest_gear"]}')
                            if stats['latest_relic'] > 1:
                                msg.append(f'Relic level: {stats["latest_relic"]}')
                            pmsg.append('\n'.join(msg))
                        else:
                            if stats['initial_stars'] != stats['latest_stars'] and stats['latest_stars'] == 7:
                                msg.append(f'Stars: {stats["initial_stars"]} -> {stats["latest_stars"]}')
                            if stats['initial_gear'] != stats['latest_gear'] and stats['latest_gear'] >= 12:
                                msg.append(f'Gear: {stats["initial_gear"]} -> {stats["latest_gear"]}')
                            if stats['initial_relic'] != stats['latest_relic']:
                                msg.append(f'Relic: {stats["initial_relic"]} -> {stats["latest_relic"]}')
                            if msg:
                                msg = [name] + msg
                                pmsg.append('\n'.join(msg))

                    if pmsg:
                        pmsg = '\n\n'.join(pmsg)
                        player_name = GLOBAL["players"].get(pID, {}).get("name", "UNKNOWN")
                        update_msg = f'**{player_name}**\n{pmsg}'
                        log(f'Attempting to send udate message {update_msg}')
                        embed = disnake.Embed(description=pmsg, colour=0x801010)
                        embed.set_author(name=player_name)
                        await channel.send(embed=embed)

                for k in deleted_keys:
                    del GLOBAL['player_updates'][k]

                GLOBAL['last_players'].update(GLOBAL['players'])
                try:
                    with open(TMP_GLOBAL_PATH, 'w') as fp:
                        fp.write(json.dumps(GLOBAL, indent=2))
                        fp.flush()
                        os.fsync(fp.fileno())
                    os.replace(TMP_GLOBAL_PATH, GLOBAL_PATH)
                except:
                    log(f'Failed to update {GLOBAL_PATH}')
                log('Begin sleeping for 30s')
                await asyncio.sleep(30)
        finally:
            pass
            #await channel.send("Bot stopping")


    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

client = MyClient()
client.run(config.auth.discord_token)


import datetime
import os
import asyncio
import config
import disnake
import stackprinter
import json
from swgoh_comlink import SwgohComlink
import requests
import urllib.request
import utils
import bin.Image_generator as gen

import logging

disnake_logger = logging.getLogger('disnake')
disnake_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=os.path.join(config.TMP_DIR,
                                                    'disnake.log'),
                              encoding='utf-8',
                              mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
disnake_logger.addHandler(handler)

GL_REQS = {}

SLEEP_S = 30
SEQ_DELAY = 3
comlink = SwgohComlink(url='http://localhost:3200')
player_data = comlink.get_player(config.allycode)
player_data['name']
guild_id = player_data['guildId']
cur_chan = config.accomplishments_channel_id
cur_thrd = config.accomplishments_thread_id
GLOBAL_PATH = f'{config.TMP_DIR}/delta.json'
TMP_GLOBAL_PATH = f'{GLOBAL_PATH}.tmp'

GLOBAL = {'guild': [], 'players': {}, 'last_players': {}, 'unit_id_to_name' : {}, 'player_updates': {}, 'cur_seq': 0, 'unit_id_to_alignment': {}}
def log(msg):
    utils.logger.info(msg)

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
    id_to_alignment = {}
    units = comlink.get_game_data(include_pve_units=False)['units']
    for unit in units:
        unit_id, _ = unit['id'].split(':')
        id_to_name[unit_id] = name_key_to_string[unit['nameKey']]
        id_to_alignment[unit_id] = unit['forceAlignment']
        
    name_key_to_string = []

    GLOBAL['unit_id_to_name'] = id_to_name
    GLOBAL['unit_id_to_alignment'] = id_to_alignment





def get_guild_data(gID):
    for _ in range(3):
        guild = comlink.get_guild(gID)
        if isinstance(guild, dict) and 'member' in guild:
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
        thread = channel.get_thread(cur_thrd)
        await thread.send("Bot starting")

        try:
            loop = asyncio.get_event_loop()

            last_players = {}
            players = {}
            last_updated_names = -100
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
                        if (d_split not in GLOBAL['unit_id_to_name'] or d_split not in GLOBAL['unit_id_to_alignment']) and last_updated_names + 100 < GLOBAL['cur_seq']:
                            log(f'Updating names since {d_split} not found in mapping')
                            last_updated_names = GLOBAL['cur_seq']
                            await loop.run_in_executor(None, update_unit_id_to_name)
                        unit_name = GLOBAL['unit_id_to_name'].get(d_split, d_split)
                        unit_alignment = GLOBAL['unit_id_to_alignment'].get(d_split, 1)

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
                                raise e
                            unit['latest_stars'] = c['currentRarity'] if c else 0
                            unit['latest_gear'] = c['currentTier'] if c else 0
                            unit['latest_relic'] = max(0, c['relic']['currentTier'] - 2
                                                           if (c and c.get('relic'))
                                                           else 0)
                            unit['alignment'] = unit_alignment
                            toons[unit_name] = unit
                            update['toons'] = toons
                            GLOBAL['player_updates'][npID] = update



                deleted_keys = []
                for pID, update in GLOBAL['player_updates'].items():
                    # if update['last_updated'] + SEQ_DELAY > GLOBAL['cur_seq']:
                    #     continue

                    player_name = GLOBAL["players"].get(pID, {}).get("name", "UNKNOWN")
                    for name, stats in update['toons'].items():
                        hit_min = False
                        msg = []
                        if stats['initial_stars'] == 0:
                            hit_min = stats["latest_stars"] == 7
                            msg.append(f'Unlocked at {stats["latest_stars"]} stars')
                            hit_min |= stats['latest_gear'] >= 12
                            if stats['latest_relic'] > 1:
                                msg.append(f'Relic: {stats["latest_relic"]}')
                            elif stats['latest_gear'] > 1:
                                msg.append(f'Gear: {stats["latest_gear"]}')
                        else:
                            gear_init = stats['initial_gear']
                            gear_final = stats['latest_gear']
                            relic_init = stats['initial_relic']
                            relic_final = stats['latest_relic']
                            init_gear_relic = ''
                            final_gear_relic = ''

                            if stats['initial_stars'] != stats['latest_stars']:
                                msg.append(f'Stars: {stats["initial_stars"]} -> {stats["latest_stars"]}')

                            if gear_init != gear_final:
                                init_gear_relic = f'G{gear_init}'
                                final_gear_relic = f'G{gear_final}'
                                if name in GL_REQS:
                                    hit_min |= gear_init < 12 and gear_final >= 12

                            if relic_init != relic_final:
                                if not init_gear_relic:
                                    if relic_init == 0:
                                        init_gear_relic = f'G{gear_init}'
                                    else:
                                        init_gear_relic = f'R{relic_init}'
                                final_gear_relic = f'R{relic_final}'

                                hit_min |= relic_final >= 7
                                for r_level in (1, 3, 5):
                                    hit_min |= relic_init < r_level and relic_final >= r_level
                            if init_gear_relic and final_gear_relic:
                                msg.append(f'{init_gear_relic} -> {final_gear_relic}')

                        if msg:
                            embed = disnake.Embed(title=player_name, colour=0x801010)
                            embed.add_field(name=name, value='\n'.join(msg), inline=False)
                            unit_img_path = utils.get_unit_img_path(name)
                            if not os.path.exists(unit_img_path):
                                utils.update_unit_images(name)
                            gen_path = gen.main(unit_img_path=unit_img_path, relic_final=final_gear_relic)
                            if os.path.exists(gen_path):
                                embed.set_thumbnail(file=disnake.File(gen_path))
                            log(f'Attempting to send udate message for {player_name}')
                            if hit_min:
                                await channel.send(embed=embed)
                            else:
                                await thread.send(embed=embed)

                    deleted_keys.append(pID)

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
                log(f'Begin sleeping for {SLEEP_S}s')
                # await asyncio.sleep(SLEEP_S)
                for _ in range(3):
                    try:
                        requests.get(config.healthcheck_url, timeout=10)
                        break
                    except requests.RequestException as e:
                        log(f'Failed to ping watchdog: {e}')

        finally:
            stackprinter.show()
            os._exit(1)
            pass
            #await channel.send("Bot stopping")


    async def on_message(self, message):
        log(f'Message from {message.author}: {message.content}')

client = MyClient()
client.run(config.discord_token)


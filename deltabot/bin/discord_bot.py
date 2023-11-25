import datetime
import os
import asyncio
import config
import disnake
import stackprinter
import json
import re
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



SLEEP_S = 0
SEQ_DELAY = 3
comlink = SwgohComlink(url='http://localhost:3200')
player_data = comlink.get_player(config.allycode)
player_data['name']
guild_id = player_data['guildId']
cur_chan = config.accomplishments_channel_id
cur_thrd = config.accomplishments_thread_id
relic_thrd = config.relics_thread_id
off_chan = config.officers_channel_id
GLOBAL_PATH = f'{config.TMP_DIR}/delta.json'
TMP_GLOBAL_PATH = f'{GLOBAL_PATH}.tmp'

galactic_legends = set()
journey_guides = set()
units = comlink.get_game_data(include_pve_units=False, request_segment=4)
layouts = units['unitGuideLayout']
for layout in layouts:
    for layoutTier in layout['layoutTier']:
        for line in layoutTier['layoutLine']:
            for unit in line['unitGuideId']:
                if layout['id'] == 'GALACTIC_LEGENDS':
                    galactic_legends.add(unit)
                    journey_guides.add(unit)
                elif layout['id'] == 'NESTING_DOLL':
                    journey_guides.add(unit)

game_data_seg1 = comlink.get_game_data(include_pve_units=False, request_segment=1)
skills = game_data_seg1['skill']
zeta = {}
omicron = {}
for skill in skills:
    for i, tier in enumerate(skill['tier']):
        if tier['isZetaTier']:
            zeta[skill['id']] = i
        if tier['isOmicronTier']:
            omicron[skill['id']] = i

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
        toon = {k: c[k] for k in ('id', 'relic', 'definitionId', 'currentRarity', 'currentTier', 'skill')}
        roster.append(toon)

    return {
            'name': player['name'],
            'rosterUnit': roster,
            'playerId': player['playerId'],
            'lastActivityTime': player['lastActivityTime'],
            'allycode': player['allyCode'],
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

already_started = False
inactivities = {}

class MyClient(disnake.Client):
    async def on_ready(self):
        global already_started
        if already_started:
            return
        else:
            already_started = True
        # log(f'Logged on as {self.user}!')
        officers_channel = self.get_channel(off_chan)
        if not isinstance(officers_channel, disnake.TextChannel):
            raise ValueError("Invalid officers channel")
        channel = self.get_channel(cur_chan)
        if not isinstance(channel, disnake.TextChannel):
            raise ValueError("Invalid channel")
        thread = channel.get_thread(cur_thrd)
        relic_thread = channel.get_thread(relic_thrd)
        await thread.send(f"{datetime.datetime.now()} Bot starting <@531637776542859265>\n")

        inactivities_thread = officers_channel.get_thread(config.officers_inactivities_thread_id)
        activity_list_thread = officers_channel.get_thread(config.officers_activity_list_thread_id)
        gl_unlock_thread = officers_channel.get_thread(config.officers_gl_unlock_thread_id)
        joins_leaves_thread = officers_channel.get_thread(config.officers_joins_leaves_thread_id)

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

            async for inactivities_message in activity_list_thread.history(limit=100):
                # Check if the message is an embed and has the specific title
                if isinstance(inactivities_message.embeds, list) and len(inactivities_message.embeds) > 0:
                    embed = inactivities_message.embeds[0]
                    if embed.title == "Player Activity":
                        inactive_message = inactivities_message
                        break
                else:
                    inactive_message = None

            activity_list_embed = disnake.Embed(title='Player Activity', colour=0x801010)
            while True:
                GLOBAL['cur_seq'] += 1
                # log('Poll for new update to guild and players')
                await loop.run_in_executor(None, update_guild)
                await loop.run_in_executor(None, update_players)
                #guild = comlink.get_guild(guild_id)
                #players = {p['playerId']: comlink.get_player(player_id=p['playerId']) for p in guild['member']}
                activity_list = []
                for npID, np in GLOBAL['players'].items():
                    lp = GLOBAL['last_players'].get(npID)
                    if lp == None:
                        await joins_leaves_thread.send(f'<@&894268297812541480> {np.get("name", "UNKNOWN")} has joined the guild')
                        # Don't print diff for new players
                        continue
                    else:
                        trash_players = []
                        for lastpID, lastp in GLOBAL['last_players'].items():
                            oldp = GLOBAL['players'].get(lastpID)
                            if oldp == None:
                                await joins_leaves_thread.send(f'<@&894268297812541480> {lastp.get("name", "UNKNOWN")} has left the guild')
                                trash_players.append(lastpID)
                                continue

                        for trash_player in trash_players:
                            GLOBAL['last_players'].pop(trash_player)

                    # check for 24h inactivity
                    last_activity = datetime.datetime.fromtimestamp(int(np['lastActivityTime'])//1000)
                    inactive = datetime.datetime.now() - last_activity
                    days_inactive = inactive.days
                    if days_inactive > inactivities.get(npID, 0):
                        inactivities[npID] = days_inactive
                        day_str = 'days <@&894268297812541480>' if days_inactive > 1 else 'day'
                        await inactivities_thread.send(f'{np.get("name", "UNKNOWN")} has been inactive for {days_inactive} {day_str}')
                        date_name = datetime.datetime.now().strftime("INACTIVE_%Y_%m_%d.py")
                        data_file = os.path.join(config.DAILY_DATA_DIR, date_name)
                        inactives = {}
                        try:
                            with open(data_file, 'r') as fp:
                                inactives = json.load(fp)
                        except:
                            pass
                        inactives[np['allycode']] = days_inactive
                        try:
                            with open(data_file, 'w') as fp:
                                json.dump(inactives, fp)
                        except:
                            pass

                    elif days_inactive == 0 and npID in inactivities:
                        del inactivities[npID]

                    activity_list += [(np.get("name", "UNKNOWN").replace(" ", "")[:10], datetime.timedelta(days=int(inactive.days), seconds=int(inactive.seconds)))]
                    msg = []
                    lp_roster = {c['id']: c for c in lp['rosterUnit']}
                    for c in np['rosterUnit']:
                        lc = lp_roster.get(c['id'])
                        d_split = c["definitionId"].split(":")[0]
                        if (d_split not in GLOBAL['unit_id_to_name'] or d_split not in GLOBAL['unit_id_to_alignment']) and last_updated_names + 100 < GLOBAL['cur_seq']:
                            log(f'Updating names since {d_split} not found in mapping')
                            last_updated_names = GLOBAL['cur_seq']
                            await loop.run_in_executor(None, update_unit_id_to_name)
                        unit_alignment = GLOBAL['unit_id_to_alignment'].get(d_split, 1)
                        latest_zeta_count = 0
                        latest_omicron_count = 0
                        for skill in c['skill']:
                            if omicron.get(skill['id']) == skill['tier']:
                                latest_omicron_count += 1
                            if zeta.get(skill['id']) == skill['tier']:
                                latest_zeta_count += 1

                        initial_zeta_count = 0
                        initial_omicron_count = 0
                        for skill in lc['skill'] if lc else []:
                            if omicron.get(skill['id']) == skill['tier']:
                                initial_omicron_count += 1
                            if zeta.get(skill['id']) == skill['tier']:
                                initial_zeta_count += 1

                        if (not lc 
                            or c['currentRarity'] != lc['currentRarity']
                            or c['currentTier'] != lc['currentTier']
                            or (c.get('relic') and lc.get('relic')
                                and lc['relic']['currentTier'] != c['relic']['currentTier'])):

                            update = GLOBAL['player_updates'].get(npID, {})
                            update['last_updated'] = GLOBAL['cur_seq']
                            toons = update.get('toons', {})
                            unit = toons.get(d_split, {})
                            unit['initial_stars'] = min(lc['currentRarity'] if lc else 0,
                                                        unit.get('initial_stars', 999))
                            unit['initial_gear'] = min(lc['currentTier'] if lc else 0,
                                                       unit.get('initial_gear', 999))
                            unit['initial_zeta_count'] = initial_zeta_count
                            unit['initial_omicron_count'] = initial_omicron_count
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
                            unit['latest_zeta_count'] = latest_zeta_count
                            unit['latest_omicron_count'] = latest_omicron_count
                        
                            unit['alignment'] = unit_alignment
                            toons[d_split] = unit
                            update['toons'] = toons
                            GLOBAL['player_updates'][npID] = update

                activity_list = sorted(activity_list, key=lambda x: x[1])
                al_description = '```'
                for al in activity_list:
                    days = al[1].days
                    hours, remainder = divmod(al[1].seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    al_description += f'{days}:{hours:02d}:{minutes:02d}:{seconds:02d} | {al[0]}\n'

                al_description += '```'
                activity_list_embed.description = al_description
                if inactive_message == None:
                    inactive_message = await activity_list_thread.send(embed=activity_list_embed)
                else:
                    await inactive_message.edit(embed=activity_list_embed)

                deleted_keys = []
                for pID, update in GLOBAL['player_updates'].items():
                    if update['last_updated'] + SEQ_DELAY > GLOBAL['cur_seq']:
                        continue

                    player_name = GLOBAL["players"].get(pID, {}).get("name", "UNKNOWN")
                    for unit_name, stats in update['toons'].items():
                        hit_min = False
                        name = GLOBAL['unit_id_to_name'].get(unit_name, unit_name)
                        
                        gear_init = stats['initial_gear']
                        gear_final = stats['latest_gear']
                        relic_init = stats['initial_relic']
                        relic_final = stats['latest_relic']
                        stars_init = stats['initial_stars']
                        stars_final = stats["latest_stars"]
                        zeta_count_init = stats["initial_zeta_count"]
                        zeta_count_latest = stats["latest_zeta_count"]
                        omicron_count_init = stats["initial_omicron_count"]
                        omicron_count_latest = stats["latest_omicron_count"]

                        init_gear_relic = ''
                        final_gear_relic = ''

                        if gear_final == 1 and gear_init == 0:
                            gear_final = 0
                            gear_init = 0

                        init_gear_relic = f'G{gear_init}'
                        final_gear_relic = f'G{gear_final}'

                        if (init_gear_relic == 'G1' and final_gear_relic == 'G1') or (init_gear_relic == 'G0' and final_gear_relic == 'G1'):
                            init_gear_relic = ''
                            final_gear_relic = ''
                           
                        if relic_init > 0:
                            init_gear_relic = f'R{relic_init}'

                        if relic_final > 0:
                            final_gear_relic = f'R{relic_final}'

                        hit_min |= relic_final >= 7
                        for r_level in (1, 3, 5):
                            hit_min |= relic_init < r_level and relic_final >= r_level

                        embed = disnake.Embed(title=player_name, colour=0x801010)
                        embed.add_field(name=name, value='', inline=False)
                        unit_img_path = utils.get_unit_img_path(name)

                        if not os.path.exists(unit_img_path):
                            utils.update_unit_images(name)

                        gen_path = gen.main(
                            unit_img_path=unit_img_path, 
                            relic_final=final_gear_relic, 
                            relic_init=init_gear_relic, 
                            alignment=stats['alignment'], 
                            stars_init=stars_init, 
                            stars_final=stars_final, 
                            zeta_count_init = zeta_count_init,
                            zeta_count_latest = zeta_count_latest,
                            omicron_count_init = omicron_count_init,
                            omicron_count_latest = omicron_count_latest,
                            unit_name=re.sub(r"[^A-Za-z0-9]+", '', '-'.join(name.split()) ).lower(),
                            player_name='-'.join(player_name.split()),
                            )
                        if os.path.exists(gen_path):
                            embed.set_image(file=disnake.File(gen_path))
                        # elif os.path.exists(unit_img_path):
                        # embed.set_thumbnail(file=disnake.File(unit_img_path)) 
                        log(f'Attempting to send udate message for {player_name}')
                        unlocked = stars_init == 0
                        full_stars = stars_init != 7 and stars_final == 7
                        if unit_name in journey_guides and (hit_min or unlocked or full_stars):
                            await channel.send(embed=embed)
                        elif hit_min:
                            await relic_thread.send(embed=embed)
                        else:
                            await thread.send(embed=embed)

                        try:
                            pass
                        except:
                            pass

                        if stars_init == 0 and unit_name in galactic_legends:
                            await gl_unlock_thread.send(f'{player_name} unlocked {name}\n<@589628217112002571>')

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
                # await asyncio.sleep(1000)
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


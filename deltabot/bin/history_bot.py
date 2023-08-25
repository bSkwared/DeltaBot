import config
import datetime
import json
import os

import disnake
from disnake.ext import commands

import plotly.graph_objects as go

bot = commands.Bot()


allycode_mappings = '''
797668393 : @acekyrios
168232195 : @apexjoker
245638798 : @bradley#9115
842925842 : @camman113
969845633 : @i.chewy
168688624 : @clerical_errors
126483852 : @curlymechanic
467499596 : @_dankobah_
278342864 : @darkhope17
825981817 : @darthsauron77
138959414 : @el_dudarino
231914963 : @estefanwolf
369472317 : @explxsive
937291233 : @rcracingcar
151593975 : @floki_ver_verlander
662511953 : @fnodo
648313163 : @foxesgaming
629268449 : @francescoo7
262722744 : @hawkeye___
738679812 : @Hank#5350
785691717 : @immortal8336
257115149 : @kratos16
938893196 : @martymcfly2.0
243453117 : @fwylo
924957122 : @Kibar#8834
892738564 : @morbidpie
648316781 : @mowmow17
716896212 : @overlord1545
841413243 : @nocturnokvlto
846156634 : @northern_adam#8701
538994795 : @sjay#8131
637384578 : @rslimshark
917787877 : @bskwared
676728824 : @Renegade7976#9848
869469465 : @roklar
326458668 : @sapphirefox1515
367251355 : @sergeantpickle
413742635 : @halis360
992228328 : @danielwg008
849672945 : @unicorncakes
972981788 : @xraus_pete
153822847 : @zyphon7
847818777 : @bestbudben
351352931 : @brothersofgoodandevil
667937846 : @ddtorch
874296875 : @shaneo97#4561
769144997 : @stryderjzw
'''

user_to_ally = {}
for line in allycode_mappings.splitlines():
    if not line:
        continue

    allycode, username = line.split(':')
    allycode = allycode.strip()
    username = username.strip()
    # remove @
    username = username[1:]
    user_to_ally[username] = allycode



def name_tag_combine(name, tag):
    username = name
    if tag and tag != '0':
        username += f'#{tag}'
    return username


@bot.slash_command(name="individual")
async def individual(inter, allycode: str = None, user: disnake.User = None):
    author_username = name_tag_combine(inter.author.name, inter.author.tag)

    if allycode and user:
        await inter.response.send_message('Please provide only an allycode or a user (or neither)')
        return

    gp_allycode = None
    if allycode:
        if len(allycode) != 9 or not allycode.isdigit():
            await inter.response.send_message(f'invalid allycode (should be 9 digits): {allycode}')
            return
        gp_allycode = allycode

    else:
        subject_username = author_username if not user else name_tag_combine(user.name, user.tag)
        if subject_username not in user_to_ally:
            await inter.response.send_message(f'Unable to find allycode for {author_username}')
            return
        gp_allycode = user_to_ally[subject_username]



    date_gp = {}
    latest_name = None
    name = ''
    for filename in os.listdir(config.DAILY_DATA_DIR):
        try:
            year, month, day = map(int, filename[:-3].split('_'))
        except:
            continue

        with open(os.path.join(config.DAILY_DATA_DIR, filename), 'r') as fp:
            guild_data = json.load(fp)

        individual_data = guild_data.get('guild_members', {}).get(gp_allycode, {})
        ship_gp = individual_data.get('ship_gp')
        char_gp = individual_data.get('char_gp')
        cur_name  = individual_data.get('name')
        if ship_gp != None and char_gp != None:
            date_gp[datetime.datetime(year, month, day)] = ship_gp + char_gp

        if cur_name and (latest_name == None or datetime.datetime(year, month, day) > latest_name):
            name = cur_name
            latest_name = datetime.datetime(year, month, day)

    if not name:
        name = allycode
    dates = []
    GPs = []
    for date in sorted(date_gp.keys()):
        dates.append(date)
        GPs.append(date_gp[date])

    if not dates or not GPs:
        await inter.response.send_message('unable to find data')
    else:
        fig = go.Figure()
        fig.add_trace(go.Line(x=dates, y=GPs))
        fig.update_layout(
            title=f"{name}'s GP Growth",
            xaxis_title="Date",
            yaxis_title="GP",
        )


        fig_filepath = os.path.join(config.TMP_DIR, f'{allycode}_individual_gp.png')
        fig.write_image(fig_filepath)
        await inter.response.send_message(file=disnake.File(fig_filepath))




'''
date_gp = {}
for filename in os.listdir(config.DAILY_DATA_DIR):
    try:
        year, month, day = map(int, filename[:-3].split('_'))
    except:
        continue

    with open(os.path.join(config.DAILY_DATA_DIR, filename), 'r') as fp:
        guild_data = json.load(fp)

    individual_data = guild_data.get('guild_members', {}).get("917787877", {})
    ship_gp = individual_data.get('ship_gp')
    char_gp = individual_data.get('char_gp')
    if ship_gp != None and char_gp != None:
        date_gp[datetime.datetime(year, month, day)] = ship_gp + char_gp

print(date_gp)
dates = []
GPs = []
for date in sorted(date_gp.keys()):
    dates.append(date)
    GPs.append(date_gp[date])

print(dates)
print(GPs)
'''

bot.run(config.discord_token)




#jimport datetime
#jimport os
#jimport asyncio
#jimport config
#jimport disnake
#jimport stackprinter
#jimport json
#jimport requests
#jimport urllib.request
#jimport utils
#jimport bin.Image_generator as gen
#j
#jimport logging
#j
#jdisnake_logger = logging.getLogger('disnake')
#jdisnake_logger.setLevel(logging.DEBUG)
#jhandler = logging.FileHandler(filename=os.path.join(config.TMP_DIR,
#j                                                    'disnake.log'),
#j                              encoding='utf-8',
#j                              mode='w')
#jhandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#jdisnake_logger.addHandler(handler)
#j
#j
#j
#jSLEEP_S = 30
#jSEQ_DELAY = 3
#jcomlink = SwgohComlink(url='http://localhost:3200')
#jplayer_data = comlink.get_player(config.allycode)
#jplayer_data['name']
#jguild_id = player_data['guildId']
#jcur_chan = config.accomplishments_channel_id
#jcur_thrd = config.accomplishments_thread_id
#jrelic_thrd = config.relics_thread_id
#joff_chan = config.officers_channel_id
#jGLOBAL_PATH = f'{config.TMP_DIR}/delta.json'
#jTMP_GLOBAL_PATH = f'{GLOBAL_PATH}.tmp'
#j
#jgalactic_legends = set()
#jjourney_guides = set()
#junits = comlink.get_game_data(include_pve_units=False, request_segment=4)
#jlayouts = units['unitGuideLayout']
#jfor layout in layouts:
#j    for layoutTier in layout['layoutTier']:
#j        for line in layoutTier['layoutLine']:
#j            for unit in line['unitGuideId']:
#j                if layout['id'] == 'GALACTIC_LEGENDS':
#j                    galactic_legends.add(unit)
#j                    journey_guides.add(unit)
#j                elif layout['id'] == 'NESTING_DOLL':
#j                    journey_guides.add(unit)
#j
#jgame_data_seg1 = comlink.get_game_data(include_pve_units=False, request_segment=1)
#jskills = game_data_seg1['skill']
#jzeta = {}
#jomicron = {}
#jfor skill in skills:
#j    for i, tier in enumerate(skill['tier']):
#j        if tier['isZetaTier']:
#j            zeta[skill['id']] = i
#j        if tier['isOmicronTier']:
#j            omicron[skill['id']] = i
#j
#jGLOBAL = {'guild': [], 'players': {}, 'last_players': {}, 'unit_id_to_name' : {}, 'player_updates': {}, 'cur_seq': 0, 'unit_id_to_alignment': {}}
#jdef log(msg):
#j    utils.logger.info(msg)
#j
#jtry:
#j    with open(GLOBAL_PATH, 'r') as fp:
#j        file_global = json.loads(fp.read())
#j    ng = {k: file_global.get(k, type(GLOBAL[k])()) for k in GLOBAL.keys()}
#j    GLOBAL = ng
#jexcept:
#j    log(f'Unable to load config from {GLOBAL_PATH}')
#j
#jdef update_unit_id_to_name():
#j    name_key_to_string = {}
#j    localization = comlink.get_localization(id=comlink.localization_version,
#j                                            unzip=True)['Loc_ENG_US.txt']
#j    for line in localization.splitlines():
#j        if line.strip().startswith('#'):
#j            continue
#j        else:
#j            k, v = line.split('|')
#j            name_key_to_string[k] = v
#j
#j    
#j
#j    id_to_name = {}
#j    id_to_alignment = {}
#j    units = comlink.get_game_data(include_pve_units=False)['units']
#j    for unit in units:
#j        unit_id, _ = unit['id'].split(':')
#j        id_to_name[unit_id] = name_key_to_string[unit['nameKey']]
#j        id_to_alignment[unit_id] = unit['forceAlignment']
#j        
#j    name_key_to_string = []
#j
#j    GLOBAL['unit_id_to_name'] = id_to_name
#j    GLOBAL['unit_id_to_alignment'] = id_to_alignment
#j
#jdef get_guild_data(gID):
#j    for _ in range(3):
#j        guild = comlink.get_guild(gID)
#j        if isinstance(guild, dict) and 'member' in guild:
#j            return guild
#j
#j    return {}
#j
#jdef update_guild():
#j    guild = get_guild_data(guild_id)
#j    if guild:
#j        GLOBAL['guild'] = guild
#j
#jdef get_player_data(pID):
#j    player = comlink.get_player(player_id=pID)
#j    roster = []
#j    if 'rosterUnit' not in player:
#j        try:
#j            log(f'blake keys: {player.keys()}')
#j        except:
#j            log(f'blake player: {player}')
#j    for c in player['rosterUnit']:
#j        toon = {k: c[k] for k in ('id', 'relic', 'definitionId', 'currentRarity', 'currentTier', 'skill')}
#j        roster.append(toon)
#j
#j    return {
#j            'name': player['name'],
#j            'rosterUnit': roster,
#j            'playerId': player['playerId'],
#j            'lastActivityTime': player['lastActivityTime'],
#j    }
#j
#jdef update_players():
#j    players = {}
#j    for p in GLOBAL['guild']['member']:
#j        for _ in range(3):
#j            try:
#j                players[p['playerId']] = get_player_data(p['playerId'])
#j                break
#j            except Exception as e:
#j                log(f'blake breaking {e}')
#j                pass
#j
#j    #GLOBAL['players'] = {p['playerId']: comlink.get_player(player_id=p['playerId']) for p in GLOBAL['guild']['member']}
#j    GLOBAL['players'] = players
#j
#jalready_started = False
#jinactivities = {}
#j
#jclass MyClient(disnake.Client):
#j    async def on_ready(self):
#j        global already_started
#j        if already_started:
#j            return
#j        else:
#j            already_started = True
#j        # log(f'Logged on as {self.user}!')
#j        officers_channel = self.get_channel(off_chan)
#j        if not isinstance(officers_channel, disnake.TextChannel):
#j            raise ValueError("Invalid officers channel")
#j        channel = self.get_channel(cur_chan)
#j        if not isinstance(channel, disnake.TextChannel):
#j            raise ValueError("Invalid channel")
#j        thread = channel.get_thread(cur_thrd)
#j        relic_thread = channel.get_thread(relic_thrd)
#j        await thread.send(f"{datetime.datetime.now()} Bot starting <@531637776542859265>\n")
#j
#j        inactivities_thread = officers_channel.get_thread(config.officers_inactivities_thread_id)
#j        gl_unlock_thread = officers_channel.get_thread(config.officers_gl_unlock_thread_id)
#j
#j        try:
#j            loop = asyncio.get_event_loop()
#j
#j            last_players = {}
#j            players = {}
#j            last_updated_names = -100
#j            # pID: {
#j            #     'last_updated': cur_seq,
#j            #     'toons': {
#j            #         'Toon name': {
#j            #             'initial_stars': 4,
#j            #             'initial_gear': 3,
#j            #             'initial_relic': 8,
#j            #         },
#j            #     },
#j            # }
#j            while True:
#j                GLOBAL['cur_seq'] += 1
#j                # log('Poll for new update to guild and players')
#j                await loop.run_in_executor(None, update_guild)
#j                await loop.run_in_executor(None, update_players)
#j                #guild = comlink.get_guild(guild_id)
#j                #players = {p['playerId']: comlink.get_player(player_id=p['playerId']) for p in guild['member']}
#j
#j                for npID, np in GLOBAL['players'].items():
#j                    lp = GLOBAL['last_players'].get(npID)
#j                    if lp == None:
#j                        await officers_channel.send(f'<@&962890734174892112> {np.get("name", "UNKNOWN")} has joined the guild')
#j                        # Don't print diff for new players
#j                        continue
#j                    else:
#j                        trash_players = []
#j                        for lastpID, lastp in GLOBAL['last_players'].items():
#j                            oldp = GLOBAL['players'].get(lastpID)
#j                            if oldp == None:
#j                                await officers_channel.send(f'<@&962890734174892112> {lastp.get("name", "UNKNOWN")} has left the guild')
#j                                trash_players.append(lastpID)
#j                                continue
#j
#j                        for trash_player in trash_players:
#j                            GLOBAL['last_players'].pop(trash_player)
#j
#j                    # check for 24h inactivity
#j                    last_activity = datetime.datetime.fromtimestamp(int(np['lastActivityTime'])//1000)
#j                    days_inactive = (datetime.datetime.now() - last_activity).days
#j                    days_inactive = (datetime.datetime.now() - last_activity).seconds // 1000
#j                    if days_inactive > inactivities.get(npID, 0):
#j                        inactivities[npID] = days_inactive
#j                        day_str = 'days' if days_inactive > 1 else 'day'
#j                        await inactivities_thread.send(f'{np.get("name", "UNKNOWN")} has been inactive for {days_inactive} {day_str}')
#j
#j                    elif days_inactive == 0 and npID in inactivities:
#j                        del inactivities[npID]
#j
#j                    msg = []
#j                    lp_roster = {c['id']: c for c in lp['rosterUnit']}
#j                    for c in np['rosterUnit']:
#j                        lc = lp_roster.get(c['id'])
#j                        d_split = c["definitionId"].split(":")[0]
#j                        if (d_split not in GLOBAL['unit_id_to_name'] or d_split not in GLOBAL['unit_id_to_alignment']) and last_updated_names + 100 < GLOBAL['cur_seq']:
#j                            log(f'Updating names since {d_split} not found in mapping')
#j                            last_updated_names = GLOBAL['cur_seq']
#j                            await loop.run_in_executor(None, update_unit_id_to_name)
#j                        unit_alignment = GLOBAL['unit_id_to_alignment'].get(d_split, 1)
#j                        latest_zeta_count = 0
#j                        latest_omicron_count = 0
#j                        for skill in c['skill']:
#j                            if omicron.get(skill['id']) == skill['tier']:
#j                                latest_omicron_count += 1
#j                            if zeta.get(skill['id']) == skill['tier']:
#j                                latest_zeta_count += 1
#j
#j                        initial_zeta_count = 0
#j                        initial_omicron_count = 0
#j                        for skill in lc['skill'] if lc else []:
#j                            if omicron.get(skill['id']) == skill['tier']:
#j                                initial_omicron_count += 1
#j                            if zeta.get(skill['id']) == skill['tier']:
#j                                initial_zeta_count += 1
#j
#j                        if (not lc 
#j                            or c['currentRarity'] != lc['currentRarity']
#j                            or c['currentTier'] != lc['currentTier']
#j                            or (c.get('relic') and lc.get('relic')
#j                                and lc['relic']['currentTier'] != c['relic']['currentTier'])):
#j
#j                            update = GLOBAL['player_updates'].get(npID, {})
#j                            update['last_updated'] = GLOBAL['cur_seq']
#j                            toons = update.get('toons', {})
#j                            unit = toons.get(d_split, {})
#j                            unit['initial_stars'] = min(lc['currentRarity'] if lc else 0,
#j                                                        unit.get('initial_stars', 999))
#j                            unit['initial_gear'] = min(lc['currentTier'] if lc else 0,
#j                                                       unit.get('initial_gear', 999))
#j                            unit['initial_zeta_count'] = initial_zeta_count
#j                            unit['initial_omicron_count'] = initial_omicron_count
#j                            try:
#j                                unit['initial_relic'] = min(max(0, lc['relic']['currentTier'] - 2
#j                                                               if (lc and lc.get('relic'))
#j                                                               else 0),
#j                                                            unit.get('initial_relic', 999))
#j                            except Exception as e:
#j                                raise e
#j                            unit['latest_stars'] = c['currentRarity'] if c else 0
#j                            unit['latest_gear'] = c['currentTier'] if c else 0
#j                            unit['latest_relic'] = max(0, c['relic']['currentTier'] - 2
#j                                                           if (c and c.get('relic'))
#j                                                           else 0)
#j                            unit['latest_zeta_count'] = latest_zeta_count
#j                            unit['latest_omicron_count'] = latest_omicron_count
#j                        
#j                            unit['alignment'] = unit_alignment
#j                            toons[d_split] = unit
#j                            update['toons'] = toons
#j                            GLOBAL['player_updates'][npID] = update
#j
#j
#j
#j                deleted_keys = []
#j                for pID, update in GLOBAL['player_updates'].items():
#j                    if update['last_updated'] + SEQ_DELAY > GLOBAL['cur_seq']:
#j                        continue
#j
#j                    player_name = GLOBAL["players"].get(pID, {}).get("name", "UNKNOWN")
#j                    for unit_name, stats in update['toons'].items():
#j                        hit_min = False
#j                        name = GLOBAL['unit_id_to_name'].get(unit_name, unit_name)
#j                        
#j                        gear_init = stats['initial_gear']
#j                        gear_final = stats['latest_gear']
#j                        relic_init = stats['initial_relic']
#j                        relic_final = stats['latest_relic']
#j                        stars_init = stats['initial_stars']
#j                        stars_final = stats["latest_stars"]
#j                        zeta_count_init = stats["initial_zeta_count"]
#j                        zeta_count_latest = stats["latest_zeta_count"]
#j                        omicron_count_init = stats["initial_omicron_count"]
#j                        omicron_count_latest = stats["latest_omicron_count"]
#j
#j                        init_gear_relic = ''
#j                        final_gear_relic = ''
#j
#j                        if gear_final == 1 and gear_init == 0:
#j                            gear_final = 0
#j                            gear_init = 0
#j
#j                        init_gear_relic = f'G{gear_init}'
#j                        final_gear_relic = f'G{gear_final}'
#j
#j                        if (init_gear_relic == 'G1' and final_gear_relic == 'G1') or (init_gear_relic == 'G0' and final_gear_relic == 'G1'):
#j                            init_gear_relic = ''
#j                            final_gear_relic = ''
#j                           
#j                        if relic_init > 0:
#j                            init_gear_relic = f'R{relic_init}'
#j
#j                        if relic_final > 0:
#j                            final_gear_relic = f'R{relic_final}'
#j
#j                        hit_min |= relic_final >= 7
#j                        for r_level in (1, 3, 5):
#j                            hit_min |= relic_init < r_level and relic_final >= r_level
#j
#j                        embed = disnake.Embed(title=player_name, colour=0x801010)
#j                        embed.add_field(name=name, value='', inline=False)
#j                        unit_img_path = utils.get_unit_img_path(name)
#j
#j                        if not os.path.exists(unit_img_path):
#j                            utils.update_unit_images(name)
#j
#j                        gen_path = gen.main(
#j                            unit_img_path=unit_img_path, 
#j                            relic_final=final_gear_relic, 
#j                            relic_init=init_gear_relic, 
#j                            alignment=stats['alignment'], 
#j                            stars_init=stars_init, 
#j                            stars_final=stars_final, 
#j                            zeta_count_init = zeta_count_init,
#j                            zeta_count_latest = zeta_count_latest,
#j                            omicron_count_init = omicron_count_init,
#j                            omicron_count_latest = omicron_count_latest,
#j                            unit_name=''.join(filter(str.isalnum, '-'.join(name.split()))).lower()
#j                            )
#j                        if os.path.exists(gen_path):
#j                            embed.set_image(file=disnake.File(gen_path))
#j                        # elif os.path.exists(unit_img_path):
#j                        # embed.set_thumbnail(file=disnake.File(unit_img_path)) 
#j                        log(f'Attempting to send udate message for {player_name}')
#j                        unlocked = stars_init == 0
#j                        full_stars = stars_init != 7 and stars_final == 7
#j                        if unit_name in journey_guides and (hit_min or unlocked or full_stars):
#j                            await channel.send(embed=embed)
#j                        elif hit_min:
#j                            await relic_thread.send(embed=embed)
#j                        else:
#j                            await thread.send(embed=embed)
#j
#j                        if stars_init == 0 and unit_name in galactic_legends:
#j                            await gl_unlock_thread.send(f'{player_name} unlocked {name}\n<@589628217112002571>')
#j
#j                    deleted_keys.append(pID)
#j
#j                for k in deleted_keys:
#j                    del GLOBAL['player_updates'][k]
#j
#j                GLOBAL['last_players'].update(GLOBAL['players'])
#j                try:
#j                    with open(TMP_GLOBAL_PATH, 'w') as fp:
#j                        fp.write(json.dumps(GLOBAL, indent=2))
#j                        fp.flush()
#j                        os.fsync(fp.fileno())
#j                    os.replace(TMP_GLOBAL_PATH, GLOBAL_PATH)
#j                except:
#j                    log(f'Failed to update {GLOBAL_PATH}')
#j                log(f'Begin sleeping for {SLEEP_S}s')
#j                # await asyncio.sleep(SLEEP_S)
#j                # await asyncio.sleep(1000)
#j                for _ in range(3):
#j                    try:
#j                        requests.get(config.healthcheck_url, timeout=10)
#j                        break
#j                    except requests.RequestException as e:
#j                        log(f'Failed to ping watchdog: {e}')
#j
#j        finally:
#j            stackprinter.show()
#j            os._exit(1)
#j            pass
#j            #await channel.send("Bot stopping")
#j
#j
#j    async def on_message(self, message):
#j        log(f'Message from {message.author}: {message.content}')
#j
#jclient = MyClient()
#jclient.run(config.discord_token)
#j

import config
import datetime
import json
import os
import plotly.express as px

import numpy as np


import disnake
from disnake.ext import commands

import plotly.graph_objects as go
import pandas as pd

import datetime

bot = commands.Bot()

allycodes_to_ids = '''
797668393 : 0 : <@165166478490861568>
168232195 : 1 : <@548367852587974669>
813135746 : 0 : <@526049061015519234>
245638798 : 1 : <@405170025331163156>
969845633 : 1 : <@315946527786926082>
168688624 : 1 : <@349270395725152259>
126483852 : 1 : <@479812280901566464>
278342864 : 1 : <@894234525230587935>
624284899 : 0 : <@361107717621809155>
825981817 : 1 : <@936863439501025321>
231914963 : 1 : <@642680810310336532>
369472317 : 0 : <@339493684498399234>
937291233 : 1 : <@399674557025484813>
151593975 : 0 : <@1092874921438367784>
662511953 : 1 : <@886597175537197086>
648313163 : 1 : <@347985192440299521>
629268449 : 0 : <@494626126652506133>
176784778 : 0 : <@376772749017874433>
262722744 : 0 : <@351172603974647828>
785691717 : 0 : <@1098254972149313617>
257115149 : 0 : <@511865842766577680>
938893196 : 1 : <@988583679842451516>
243453117 : 1 : <@207293257762340864>
892738564 : 0 : <@229972789442904065>
648316781 : 1 : <@298311434155065356>
716896212 : 1 : <@101813675391717376>
841413243 : 0 : <@323005722562527233>
172727459 : 0 : <@624332475182874664>
846156634 : 1 : <@814739992612962315>
132572786 : 0 : <@967738116846780426>
538994795 : 1 : <@607624076688621608>
637384578 : 1 : <@241304454027018240>
917787877 : 1 : <@531637776542859265>
676728824 : 0 : <@804916714281762826>
326458668 : 1 : <@895291606821928970>
239491824 : 0 : <@269747113389326337>
413742635 : 1 : <@621668466901909505>
992228328 : 1 : <@589628217112002571>
849672945 : 0 : <@703314346692051026>
972981788 : 1 : <@537516656281387038>
746827833 : 0 : <@628215732890632232>
153822847 : 1 : <@426906482550898700>
847818777 : 1 : <@614900489812836384>
351352931 : 0 : <@514972281353666590>
667937846 : 0 : <@481684568378703877>
489517331 : 0 : <@479318956604260353>
769144997 : 1 : <@81650192071262208>
'''

id_to_ally = {}
for line in allycodes_to_ids.splitlines():
    if not line:
        continue

    allycode, _, ID = line.split(' : ')
    id_to_ally[int(ID[2:-1])] = allycode



def load_gp(daily_data, allycode, guild_combined):
    char_gp = load_char_gp(daily_data, allycode, guild_combined)
    ship_gp = load_ship_gp(daily_data, allycode, guild_combined)
    if char_gp == None or ship_gp == None:
        return None
    return char_gp + ship_gp


def load_modscore(daily_data, allycode, guild_combined):
    raw_mod = load_raw_mods(daily_data, allycode, guild_combined)
    char_gp = load_char_gp(daily_data, allycode, guild_combined)
    if raw_mod == None or char_gp == None:
        return None

    return raw_mod / (char_gp * 3 / 100_000)


def load_raw_mods(daily_data, allycode, guild_combined):
    total = None
    for ac, m in daily_data.get('guild_members', {}).items():
        if guild_combined or ac == allycode:
            if 'speed_mods' not in m:
                continue
            total = total or 0
            for speed, count in enumerate(m['speed_mods']):
                if speed <= 10:
                    continue

                speed_value = (  -6.3058820272303500e+000 * (speed**0)
                               +  1.3035991984201347e+000 * (speed**1)
                               + -9.6654093848707642e-002 * (speed**2)
                               +  2.7728738967038821e-003 * (speed**3))

                total += count * speed_value

    return total



def load_char_gp(daily_data, allycode, guild_combined):
    members = daily_data.get('guild_members', {})
    total = None
    for ac, m in daily_data.get('guild_members', {}).items():
        if guild_combined or ac == allycode:
            if 'char_gp' not in m:
                continue
            total = total or 0
            total += m.get('char_gp', 0)
    return total


def load_ship_gp(daily_data, allycode, guild_combined):
    members = daily_data.get('guild_members', {})
    total = None
    for ac, m in daily_data.get('guild_members', {}).items():
        if 'ship_gp' not in m:
            continue
        if guild_combined or ac == allycode:
            total = total or 0
            total += m.get('ship_gp', 0)
    return total


def load_mods_15_speed(daily_data, allycode, guild_combined):
    return count_mods_speed_threshold(daily_data, allycode, 15, guild_combined)


def load_mods_20_speed(daily_data, allycode, guild_combined):
    return count_mods_speed_threshold(daily_data, allycode, 20, guild_combined)


def count_mods_speed_threshold(daily_data, allycode, threshold, guild_combined):
    total = None
    for ac, m in daily_data.get('guild_members', {}).items():
        if guild_combined or ac == allycode:
            if 'speed_mods' not in m:
                continue
            total = total or 0
            total += sum(m.get('speed_mods', [])[threshold:])
    return total
    


STATS = {
        'gp': {
            'ui_name': 'GP',
            'load_func': load_gp,
        },
        'modscore': {
            'ui_name': 'Modscore (divided by GP)',
            'load_func': load_modscore,
        },
        'character_gp': {
            'ui_name': 'Character GP',
            'load_func': load_char_gp,
        },
        'ship_gp': {
            'ui_name': 'Ship GP',
            'load_func': load_ship_gp,
        },
        'raw_mods': {
            'ui_name': 'Raw Modscore (not divided by GP)',
            'load_func': load_raw_mods,
        },
        'mods_with_15_speed': {
            'ui_name': 'Mods >= 15 speed',
            'load_func': load_mods_15_speed,
        },
        'mods_with_20_speed': {
            'ui_name': 'Mods >= 20 speed',
            'load_func': load_mods_20_speed,
        },
}

async def autocomp_stats(inter: disnake.ApplicationCommandInteraction, user_input: str):
    return [stat for stat in STATS.keys() if user_input.lower() in stat]



@bot.slash_command(name="progression", description="Show chart of progression based on chosen stat")
async def progression(
        inter,
        stat: str = commands.Param(autocomplete=autocomp_stats, description='What stat to show progression in'),
        days_back: int = commands.Param(description='How many days to go back in history', default=90, le=1000),
        guild_combined: bool = commands.Param(description='UNUSED', default=False),
        hide_self: bool = commands.Param(description='Include yourself with other users', default=False),
        user1: disnake.User = commands.param(description='Additional user to chart', default=None),
        user2: disnake.User = commands.param(description='Additional user to chart', default=None),
        user3: disnake.User = commands.param(description='Additional user to chart', default=None),
        user4: disnake.User = commands.param(description='Additional user to chart', default=None),
        ally1: str = commands.param(description='Additional allycode to chart', default=None),
        ally2: str = commands.param(description='Additional allycode to chart', default=None),
        ally3: str = commands.param(description='Additional allycode to chart', default=None),
        ally4: str = commands.param(description='Additional allycode to chart', default=None),
        ):

    subject_allycodes = []
    err_msg = []
    def add_users_ac(user):
        if user.id not in id_to_ally:
            err_msg.append(f'Unable to find allycode for {user.name}')
            return
        subject_allycodes.append(id_to_ally[user.id])

    def add_ac(ac):
        if len(ac) != 9 or not ac.isdigit():
            err_msg.append(f'invalid allycode (should be 9 digits): {ac}')
            return
        subject_allycodes.append(ac)

    for u in (None if hide_self or guild_combined else inter.author, user1, user2, user3, user4):
        if u:
            add_users_ac(u)

    for ac in (ally1, ally2, ally3, ally4):
        if ac:
            add_ac(ac)

    if not guild_combined and not subject_allycodes:
        err_msg.append(f'Please provide users or allycodes')

    if guild_combined and subject_allycodes:
        err_msg.append(f'Please do not add users or allycodes for combined data')

    if err_msg:
        await inter.response.send_message('\n'.join(err_msg))
        return

    await inter.response.defer()
    cur_stat = STATS[stat]
    days = []
    now = datetime.datetime.now()
    cur_date = now - datetime.timedelta(days=days_back)
    while cur_date <= now:
        days.append(datetime.datetime(day=cur_date.day, month=cur_date.month, year=cur_date.year))
        cur_date += datetime.timedelta(days=1)


    GUILD_FAKE_AC = 'CCD123'
    GUILD_NAME = 'CCD'
    ac_data = {}
    ac_latest_name = {}
    if guild_combined:
        assert not subject_allycodes
        subject_allycodes.append(GUILD_FAKE_AC)
        ac_latest_name[GUILD_FAKE_AC] = GUILD_NAME

    for cur_date in days:
        filename = cur_date.strftime("%Y_%m_%d.py")
        try:
            with open(os.path.join(config.DAILY_DATA_DIR, filename), 'r') as fp:
                guild_data = json.load(fp)
        except:
            continue

        for sac in subject_allycodes:
            if sac not in ac_data:
                ac_data[sac] = []
            ac_data[sac].append(cur_stat['load_func'](guild_data, sac, guild_combined))
            member = guild_data['guild_members'].get(sac, {})
            if 'name' in member:
                ac_latest_name[sac] = member['name'].replace(' ', '')[:10]

    if not ac_data:
        await inter.followup.send('unable to find data')
        return

    
    plot_data = {'Date': days}
    names = []
    for ac, gps in ac_data.items():
        plot_data[ac_latest_name[ac]] = gps
        names.append(ac_latest_name[ac])

    df = pd.DataFrame.from_dict(plot_data)
    fig = px.line(df, x='Date', y=df.columns[1:], template='plotly_dark',
            title=f'{cur_stat["ui_name"]} for {", ".join(names)} last {days_back} days',
            labels={'variable':'Player', 'value':cur_stat['ui_name']})
    # fig.update_yaxes(rangemode="tozero")
    fig_filepath = os.path.join(config.TMP_DIR, f'{stat}_since_{days_back}_{inter.author.name}.png')
    fig.write_image(fig_filepath)
    await inter.followup.send(file=disnake.File(fig_filepath))

    try:
        os.remove(fig_filepath)
    except:
        pass

bot.run(config.discord_token)

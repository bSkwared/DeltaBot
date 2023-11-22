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

'''
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



'''
end = WD.get_current_datetime()
start = end - datetime.timedelta(days=args.duration)

gp_names = ['redfox', 'sapp']
gp_diff = [100, 200]
gp_perc = [0.1, 0.2]

fig = px.line({'Date': dates, 'GP': gps}, x='Date', y='GP')


fig = px.bar({'Name': gp_names, 'Growth': gp_diff}, x='Name', y='Growth')
fig.update_xaxes(dtick=1)
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})
fig.write_image("tmp/fig1.png")

fig = px.bar({'Name': gp_names, 'Growth': gp_perc}, x='Name', y='Growth')
fig.update_xaxes(dtick=1)
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})
fig.write_image("tmp/fig2.png")
print(len(gp_names))
'''

def modscore(speed_mods, char_gp):
    return raw_mod_value(speed_mods) / (char_gp * 3 / 100_000)

def get_subject_allycode(author, allycode, user):
    if allycode and user:
        raise Exception('Please provide only an allycode or a user (or neither)')

    subject_allycode = None
    if allycode:
        if len(allycode) != 9 or not allycode.isdigit():
            raise Exception(f'invalid allycode (should be 9 digits): {allycode}')
        return allycode

    else:
        author_username = name_tag_combine(author.name, author.tag)
        subject_username = author_username if not user else name_tag_combine(user.name, user.tag)
        if subject_username not in user_to_ally:
            raise Exception(f'Unable to find allycode for {author_username}')
        return user_to_ally[subject_username]


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
    individual_data = daily_data.get('guild_members', {}).get(allycode, {})
    if 'speed_mods' not in individual_data:
        return None

    total = 0
    for speed, count in enumerate(individual_data['speed_mods']):
        if speed <= 10:
            continue

        speed_value = (  -6.3058820272303500e+000 * (speed**0)
                       +  1.3035991984201347e+000 * (speed**1)
                       + -9.6654093848707642e-002 * (speed**2)
                       +  2.7728738967038821e-003 * (speed**3))

        total += count * speed_value

    return total


def load_char_gp(daily_data, allycode, guild_combined):
    return daily_data.get('guild_members', {}).get(allycode, {}).get('char_gp')


def load_ship_gp(daily_data, allycode, guild_combined):
    return daily_data.get('guild_members', {}).get(allycode, {}).get('ship_gp')


def load_mods_15_speed(daily_data, allycode, guild_combined):
    return count_mods_speed_threshold(daily_data, allycode, 15, guild_combined)


def load_mods_20_speed(daily_data, allycode, guild_combined):
    return count_mods_speed_threshold(daily_data, allycode, 20, guild_combined)


def count_mods_speed_threshold(daily_data, allycode, threshold, guild_combined):
    individual_data = daily_data.get('guild_members', {}).get(allycode, {})
    if 'speed_mods' not in individual_data:
        return None
    return sum(individual_data['speed_mods'][threshold:])
    


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
        allycode: str = commands.param(description='Defaults to who ran this command', default=None),
        user: disnake.User = commands.param(description='Defaults to who ran this command', default=None),
        ally1: str = commands.param(description='UNUSED - Additional allycode to chart', default=None),
        ally2: str = commands.param(description='UNUSED - Additional allycode to chart', default=None),
        ally3: str = commands.param(description='UNUSED - Additional allycode to chart', default=None),
        ally4: str = commands.param(description='UNUSED - Additional allycode to chart', default=None),
        user1: disnake.User = commands.param(description='UNUSED - Additional user to chart', default=None),
        user2: disnake.User = commands.param(description='UNUSED - Additional user to chart', default=None),
        user3: disnake.User = commands.param(description='UNUSED - Additional user to chart', default=None),
        user4: disnake.User = commands.param(description='UNUSED - Additional user to chart', default=None),
        ):
    try:
        subject_allycode = get_subject_allycode(inter.author, allycode, user)
    except Exception as e:
        await inter.response.send_message(str(e))
        return

    subject_allycodes = [subject_allycode] 

    await inter.response.defer()
    cur_stat = STATS[stat]
    days = []
    now = datetime.datetime.now()
    cur_date = now - datetime.timedelta(days=days_back)
    while cur_date <= now:
        days.append(datetime.datetime(day=cur_date.day, month=cur_date.month, year=cur_date.year))
        cur_date += datetime.timedelta(days=1)



    ac_data = {}
    ac_latest_name = {}
    ac_last_name_date = {}
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

        cur_name  = guild_data['guild_members'].get(sac, {}).get('name')
        print(cur_name)
        cur_name_newer = ac_last_name_date.get(sac) == None or cur_date > ac_last_name_date.get(sac)
        if cur_name and cur_name_newer:
            ac_latest_name[sac] = cur_name
            ac_last_name_date[sac] = cur_date

    if not ac_data:
        await inter.followup.send('unable to find data')
        return

    
    print(days)
    print(ac_data)
    print(ac_latest_name)
    plot_data = {'Date': days}
    names = []
    for ac, gps in ac_data.items():
        plot_data[ac_latest_name[ac]] = gps
        names.append(ac_latest_name[ac])

    df = pd.DataFrame.from_dict(plot_data)
    print(df)
    print(f'columns: {df.columns[1]}')
    print(f'columns: {df.columns}')
    fig = px.line(df, x='Date', y=df.columns[1:], template='plotly_dark')
    # fig.update_yaxes(rangemode="tozero")
    fig_filepath = os.path.join(config.TMP_DIR, f'{stat}_since_{days_back}_{inter.author.name}.png')
    fig.write_image(fig_filepath)
    await inter.followup.send(file=disnake.File(fig_filepath))

    try:
        os.remove(fig_filepath)
    except:
        pass

bot.run(config.discord_token)

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
'''


@bot.slash_command(name="bbbbbbbbbindividual")
async def bbbbbbbbbindividual(inter, allycode: str = None, user: disnake.User = None):
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





bot.run(config.discord_token)
'''




import datetime
import plotly.express as px

'''
end = WD.get_current_datetime()
start = end - datetime.timedelta(days=args.duration)
'''

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


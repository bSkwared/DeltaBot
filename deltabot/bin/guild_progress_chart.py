import argparse
import config.config as config
import datetime
import plotly.express as px
import warehouse.data as WD
import warehouse.analytics as WA

parser = argparse.ArgumentParser()
parser.add_argument('-g', '--guild-id', required=True, type=str,
                    help='Guild ID to chart GP for.')
parser.add_argument('-d', '--duration', default=30, type=int,
                    help='Number of days to chart GP over.')

args = parser.parse_args()

end = WD.get_current_datetime()
start = end - datetime.timedelta(days=args.duration)
print(args)
print(end)
print(start)
WD.setup_warehouse(config.DEV_DB)
#print([p.name for p in WD.get_latest_guild_members('G746160409')])
#import sys
#sys.exit(0)

dates, gp_progress, names = WA.get_individual_gp_progress(args.guild_id, start, end)
#print(WA.get_guild_gp_progress(args.guild_id, start, end))

gp_names = []
gp_diff = []
gp_perc = []
for ac, gps in gp_progress.items():
    diff = gps[1] - gps[0]
    gp_diff.append(diff)
    gp_perc.append(diff / gps[0])
    gp_names.append(names[ac])




fig = px.bar({'Name': gp_names, 'Growth': gp_diff}, x='Name', y='Growth')
fig.update_xaxes(dtick=1)
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})
fig.write_image("tmp/fig1.png")

fig = px.bar({'Name': gp_names, 'Growth': gp_perc}, x='Name', y='Growth')
fig.update_xaxes(dtick=1)
fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})
fig.write_image("tmp/fig2.png")
print(len(gp_names))


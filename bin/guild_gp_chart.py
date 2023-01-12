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

progress = WA.get_guild_gp_progress(args.guild_id, start, end)
print(progress)
dates, gps = zip(*progress)
print(dates)
print(gps)

fig = px.line({'Date': dates, 'GP': gps}, x='Date', y='GP')
fig.write_image("tmp/fig1.png")

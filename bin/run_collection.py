import warehouse.data as data
import config.config as config
import api_swgoh_help.client as ash_client
import sys
import ntplib
import json
import os
import datetime



def main(args):
    is_prod = '--prod' in args
    print(is_prod)
    data.setup_warehouse(config.PROD_DB if is_prod else config.DEV_DB)
    with open(config.AUTH_CONFIG, 'r') as fp:
        auth = json.load(fp)
    client = ash_client.APIClient(username=auth['username'], password=auth['password'])

    guilds = client.get_guilds([auth['allycode']])
    guild_names = ', '.join([g.name for g in guilds.values()])
    print(f'Retreived guilds: {guild_names}')
    players = {}
    for g in guilds.values():
        players.update(client.get_players(g.member_allycodes))
    print(json.dumps([p.__dict__ for p in players.values()]))
    total_gp = 0
    for p in players.values():
        total_gp += p.total_gp
    print(total_gp)



if __name__ == "__main__":
    main(sys.argv)



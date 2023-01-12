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

    with open(config.AUTH_CONFIG, 'r') as fp:
        auth = json.load(fp)
    client = ash_client.APIClient(username=auth['username'], password=auth['password'])

    data.setup_warehouse(config.PROD_DB if is_prod else config.DEV_DB)
    known_allycodes = data.get_allycodes()
    guilds = {}
    guild_found = set()
    for allycode in known_allycodes:
        if allycode in guild_found:
            continue
        g = client.get_guilds([allycode])
        for guild in g.values():
            print(f'Found guild {guild.name} with members {guild.member_allycodes}')
            guild_found.update(guild.member_allycodes)
            guilds[guild.guild_id] = guild


    guild_names = ', '.join([g.name for g in guilds.values()])
    print(f'Retreived guilds: {guild_names}')

    players = {}
    for g in guilds.values():
        print(f'Fetching players in {g.name}')
        players.update(client.get_players(g.member_allycodes))

    for ac in known_allycodes:
        if ac not in players:
            print(f'Fetching unguilded player {ac}')
            players.update(client.get_players([ac]))


    time = data.get_current_datetime()
    print(f'Current time {time}, saving {len(players.keys())} players ' \
          f'and {len(guilds.keys())} guilds')
    data.save_data(list(guilds.values()), list(players.values()), time)

if __name__ == "__main__":
    main(sys.argv)



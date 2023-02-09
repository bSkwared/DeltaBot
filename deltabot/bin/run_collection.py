import warehouse.data as data
import config.config as CFG
import api_swgoh_help.client as ash_client
import sys
import ntplib
import json
import os
import datetime



def main(args):
    is_prod = '--prod' in args

    client = ash_client.APIClient(username=CFG.username, password=CFG.password)

    data.setup_warehouse(CFG.STATS_DB)
    known_allycodes = data.get_allycodes()
    guilds = {}
    guild_found = set()
    for allycode in known_allycodes:
        if allycode in guild_found:
            continue
        cur_player = client.get_players([allycode])
        if not cur_player[allycode].guild_id:
            # Player not in guild, so calling get_guilds will take forever and fail
            continue
        g = client.get_guilds([allycode])
        for guild in g.values():
            print(f'Found guild {guild.name} with {len(guild.member_allycodes)} members')
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



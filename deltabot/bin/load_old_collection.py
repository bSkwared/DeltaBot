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
    is_csv = '--csv' in args
    is_json = '--json' in args
    assert '--timestamp' in args
    timestamp = int(args[args.index('--timestamp') + 1])

    players = []

    if is_csv:
        assert '--guild-id' in args, 'csv flag must provide guild-id'
        guild_id = args[args.index('--guild-id') + 1]
        filename = args[args.index('--csv') + 1]
        with open(filename, 'r') as fp:
            contents = fp.read()

        first = True
        for l in contents.splitlines():
            if first:
                first = False
                continue

            #print(l)
            p = eval(l)

            players.append(ash_client.Player(p[1], p[0].splitlines()[0], guild_id, p[2], p[3],
                                             p[5], p[6], p[4], p[8], p[7]))

    if is_json:
        filename = args[args.index('--json') + 1]
        with open(filename, 'r') as fp:
            contents = json.loads(fp.read())

        players.extend(ash_client.parse_players_list(contents))


    data.setup_warehouse(config.STATS_DB)
    data.save_data([], players, datetime.datetime.fromtimestamp(timestamp))


if __name__ == "__main__":
    main(sys.argv)



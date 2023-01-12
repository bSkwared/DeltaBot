from api_swgoh_help import api_swgoh_help
import sys
import json
from datetime import datetime, timezone
import ntplib

class Guild:
    def __init__(self, guild_id, name, description, member_allycodes):
        self.guild_id = guild_id
        self.name = name
        self.description = description
        self.member_allycodes = member_allycodes

class Player:
    def __init__(self, allycode, name, guild_id, ship_gp, character_gp, gac_league,
                 gac_division, gac_rank, fleet_arena_rank, squad_arena_rank):
        self.allycode = allycode
        self.name = name
        self.guild_id = guild_id
        self.ship_gp = ship_gp
        self.character_gp = character_gp
        self.gac_league = gac_league
        self.gac_division = gac_division
        self.gac_rank = gac_rank
        self.fleet_arena_rank = fleet_arena_rank
        self.squad_arena_rank = squad_arena_rank

def convert_dict_to_guild(guild):
    roster = guild.get('roster', [])
    if not roster:
        print(f'WARN: {guild["name"]} has empty roster')
    member_allycodes = [m.get('allyCode', 0) for m in roster]
    if not all(member_allycodes):
        print(f'WARN: {guild["name"]} has missing allycodes')
    return Guild(guild['id'], guild['name'], guild['desc'], member_allycodes)

def parse_gp_stats(stats):
    gp_stats = {'ships': 0, 'characters': 0}
    for stat in stats:
        if stat['nameKey'] == 'Galactic Power (Ships):':
            gp_stats['ships'] = stat['value']
        elif stat['nameKey'] == 'Galactic Power (Characters):':
            gp_stats['characters'] = stat['value']

    return gp_stats

def parse_gac_stats(grand_arena):
    assert isinstance(grand_arena, list), f'ERROR: expcted {grand_arena} list, got {type(grand_arena)}'
    current_gac = grand_arena[-1] if grand_arena else {'league': 'UNKNOWN', 'division': 0, 'rank': 0}
    return {
        'league': current_gac.get('league', 'UNKNOWN'),
        'division': convert_gac_division(current_gac.get('division', 0)),
        'rank': current_gac.get('rank', 0),
    }


def convert_gac_division(division):
    return 6 - (division//5)

def convert_dict_to_player(player):
    stats = parse_gp_stats(player['stats'])

    return Player(player['allyCode'], player['guildRefId'], stats['ships'],
                  stats['characters'], player['gac_league'], gac_division, gac_rank,
                  fleet_rank, squad_rank)



class APIClient:
    def __init__(self, username, password):
        """
        Parameters:
        username (str): Username for swgoh help API
        password (str): Password for swgoh help API
        """
        #with open('./ally_passwd.txt') as fd:
        #    ally_passwd = fd.read()
        self.client = api_swgoh_help.api_swgoh_help({'username': username,
                                                     'password': password})

    def get_endpoint_list(allycodes, endpoint):
        """Return json parsed result of call to endpoint.

        Parameters:
        allycodes (List[int]): List of allycodes to get guilds for
        endpoint (str): Endpoint to hit, either 'player' or 'guild'

        Returns:
        List[Dict]: List of raw dicts parsed from remote API.
        """
        if endpoint == 'player':
            data = self.client.fetchPlayers(allycodes)
        elif endpoint == 'guild':
            data = self.client.fetchGuilds(allycodes)
        else:
            print(f'ERROR: {endpoint} is not a valid endpoint')

        result = []
        try:
            result = json.loads(data)
        except ValueError as e:
            print(f'ERROR: Unable to parse json from {data} - {e}')

        assert isinstance(result, list), f'ERROR: expected a list but ' \
                                         f'{result} is a {type(result)}'

        return result


    def get_guilds(self, allycodes):
        """Get guilds for each of the allycodes. Duplicate guilds are removed.

        Parameters:
        allycodes (List[int]): List of allycodes to get guilds for.

        Returns:
        Dict[str, Guild]: Map of guild IDs to guild objects.
        """
        assert isinstance(allycodes, list), f'{allycodes} must be a list, ' \
                                            f'not {type(allycodes)}'
        guilds = get_endpoint_list(allycodes, 'guilds')
        assert isinstance(guilds, list), f'Expected list, got {type(guilds)}: {guilds}'

        # Parse guilds into Guild classes
        guilds_dict = {}
        for guild in guilds:
            g = convert_dict_to_guild(guild)
            guilds_dict[g.guild_id] = g

        return guilds_dict


    def get_players(self, allycodes):
        """Get players for each of the allycodes. Duplicate allycodes are removed.

        Parameters:
        allycodes (List[int]): List of allycodes to get data for.

        Returns:
        Dict[str, Player]: Map of allycodes to Player objects.
        """
        assert isinstance(allycodes, list), f'{allycodes} must be a list, ' \
                                            f'not {type(allycodes)}'
        guilds = get_endpoint_list(allycodes, 'players')
        assert isinstance(guilds, list), f'Expected list, got {type(players)}: {player}'

        # Parse players into Player classes
        players_dict = {}
        for player in players:
            # Logic for removing duplicate players
            if player['allyCode'] in players_dict:
                continue

            p = convert_dict_to_player(player)
            players_dict[p.allycode] = p

        return guilds_dict


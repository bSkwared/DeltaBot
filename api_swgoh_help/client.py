from api_swgoh_help import api_swgoh_help
import sys

class Guild:
    def __init__(self, guild_id, name, description, member_allycodes):
        self.guild_id = guild_id
        self.name = name
        self.description = description
        self.member_allycodes = member_allycodes

class Player:
    def __init__(self, allycode, name, guild_id, ship_gp, character_gp, gac_league,
                 gac_division, gac_rank, fleet_rank, squad_rank, roster):
        self.allycode = allycode
        self.name = name
        self.guild_id = guild_id
        self.ship_gp = ship_gp
        self.character_gp = character_gp
        self.gac_league = gac_league
        self.gac_division = gac_division
        self.gac_rank = gac_rank
        self.fleet_rank = fleet_rank
        self.squad_rank = squad_rank
        self.roster = roster

    @property
    def total_gp(self):
        return self.ship_gp + self.character_gp


class Toon:
    def __init__(self, toon_id, name, stars, gear_level, relic_level):
        self.toon_id = toon_id
        self.name = name
        self.stars = stars
        self.gear_level = gear_level
        self.relic_level = relic_level


def convert_dict_to_guild(guild):
    roster = guild.get('roster', [])
    if not roster:
        print(f'WARN: {guild["name"]} has empty roster')
    member_allycodes = [m.get('allyCode', 0) for m in roster]
    if not all(member_allycodes):
        print(f'WARN: {guild["name"]} has missing allycodes')
        print(f'{roster}')
        return None
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
    gp = parse_gp_stats(player['stats'])
    gac = parse_gac_stats(player['grandArena'])
    roster = parse_roster(player['roster'])

    return Player(player['allyCode'], player['name'], player['guildRefId'],
                  gp['ships'], gp['characters'], gac['league'], gac['division'],
                  gac['rank'], player['arena']['ship']['rank'],
                  player['arena']['char']['rank'], roster)


def parse_players_list(players_list):
    players_dict = {}
    for player in players_list:
        # Logic for removing duplicate players
        if player['allyCode'] in players_dict:
            continue

        p = convert_dict_to_player(player)
        players_dict[p.allycode] = p

    return players_dict

def parse_relic_level(relic):
    if not relic:
        return 0

    # currentTier is set to 1 until g13. At g13, it's set to 2.
    # Then, it is set to 3 at relic 1 and increases with each relic level
    # eg, ct=4 is relic 2, ct=5 is relic 3, ...
    return max(0, relic.get('currentTier', 0) - 2)


def parse_roster(roster):
    toons = []
    for t in roster:
        toons.append(Toon(t['id'], t['nameKey'] if t['nameKey'] else t['defId'], t['rarity'], t['gear'],
                          parse_relic_level(t['relic'])))

    return toons


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

    def get_endpoint_list(self, allycodes, endpoint):
        """Return json parsed result of call to endpoint.

        Parameters:
        allycodes (List[int]): List of allycodes to get guilds for
        endpoint (str): Endpoint to hit, either 'players' or 'guilds'

        Returns:
        List[Dict]: List of raw dicts parsed from remote API.
        """
        endpoints = {
                'players': self.client.fetchPlayers,
                'guilds': self.client.fetchGuilds,
        }
        assert endpoint in endpoints.keys(), f'{endpoint} is an invalid endpoint'

        result = []
        for _ in range(3):
            result = endpoints[endpoint](allycodes)
            if isinstance(result, list):
                return result

            elif endpoint == 'guilds' and isinstance(result, dict) \
                    and result.get('status_code', 0) == 404 \
                    and "Could not find any guilds affiliated" in result.get('message', ''):
                return []

        print(f'ERROR: Unable to parse {result} of type {type(result)}, expected list')
        return []


    def get_guilds(self, allycodes):
        """Get guilds for each of the allycodes. Duplicate guilds are removed.

        Parameters:
        allycodes (List[int]): List of allycodes to get guilds for.

        Returns:
        Dict[str, Guild]: Map of guild IDs to guild objects.
        """
        assert isinstance(allycodes, list), f'{allycodes} must be a list, ' \
                                            f'not {type(allycodes)}'

        # Add retry
        for _ in range(3):
            guilds = self.get_endpoint_list(allycodes, 'guilds')
            assert isinstance(guilds, list), f'Expected list, got {type(guilds)}: {guilds}'

            # Parse guilds into Guild classes
            guilds_dict = {}
            found_acs = set()
            found_mistake = False
            for guild in guilds:
                g = convert_dict_to_guild(guild)
                if g == None:
                    found_mistake = True
                    break
                guilds_dict[g.guild_id] = g
                found_acs.update(g.member_allycodes)

            # Check that all allycodes were returned
            found_all_acs = set(allycodes).issubset(found_acs)
            if not found_mistake and found_all_acs:
                break

        else:
            assert False, f'Unable to load guilds for allycodes {allycodes}'

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

        expected_acs = set(allycodes)
        for _ in range(3):
            players = self.get_endpoint_list(allycodes, 'players')
            assert isinstance(players, list), f'Expected list, got {type(players)}: {player}'
            players_dict = parse_players_list(players)

            found_acs = set(players_dict.keys())
            if expected_acs == found_acs:
                break
            else:
                print(f'WARN: When attempting to load {allycodes}, only found {found_acs}')

        else:
            assert False, f'Unable to load players for allycodes {allycodes}'


        # Parse players into Player classes
        return players_dict



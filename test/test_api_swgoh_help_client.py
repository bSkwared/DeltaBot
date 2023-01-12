import pytest
import api_swgoh_help.client as client

@pytest.mark.parametrize("guild_id,name,desc,allycodes",[
    ("guildID1", "Guild's first name", "Guild description", [1, 2, 3]),
    ("NDKER2094", "BIg GUild NAme 234520l", "Join our 500M GP", [123456789, 928453892, 376028472]),
])
def test_convert_dict_to_guild_valid(guild_id, name, desc, allycodes):

    g = {
        "id": guild_id,
        "name": name,
        "desc": desc,
        "roster": [{"allyCode": a} for a in allycodes],
    }

    converted_guild = client.convert_dict_to_guild(g)
    assert converted_guild.guild_id == guild_id
    assert converted_guild.name == name
    assert converted_guild.description == desc
    assert converted_guild.member_allycodes == allycodes


@pytest.mark.parametrize("roster,expected_allycodes,err_str",[
    ([], [], 'WARN: guild_name has empty roster'),
    ([{"id":"123"},{"id":"124","allyCode":1}], [0, 1], 'WARN: guild_name has missing allycodes'),
])
def test_convert_dict_to_guild_invalid(mocker, roster, expected_allycodes, err_str):
    g = {
        "id": '123',
        "name": 'guild_name',
        "desc": '123',
        "roster": roster,
    }
    mocker.patch('builtins.print')
    converted_guild = client.convert_dict_to_guild(g)

    print.assert_called_once_with(err_str)
    assert converted_guild.guild_id == '123'
    assert converted_guild.name == 'guild_name'
    assert converted_guild.description == '123'
    assert converted_guild.member_allycodes == expected_allycodes

@pytest.mark.parametrize("stats,expected_ship_gp,expected_character_gp",[
    (
      [
          {
            "nameKey": "Galactic Power:",
            "value": 3437838,
            "index": 1
          },
          {
            "nameKey": "Galactic Power (Characters):",
            "value": 2080901,
            "index": 2
          },
          {
            "nameKey": "Galactic Power (Ships):",
            "value": 1356937,
            "index": 3
          },
          {
            "nameKey": "Lifetime Championship Score:",
            "value": 30527,
            "index": 4
          },
      ],
      1356937,
      2080901,
    ),
    (
      [
          {
            "nameKey": "Galactic Power (Characters):",
            "value": 1,
            "index": 2
          },
          {
            "nameKey": "Galactic Power (Ships):",
            "value": 2,
            "index": 3
          },
      ],
      2,
      1,
    ),
])
def test_parse_gp_stats(mocker, stats, expected_ship_gp, expected_character_gp):
    gp_stats = client.parse_gp_stats(stats)
    assert gp_stats['ships'] == expected_ship_gp
    assert gp_stats['characters'] == expected_character_gp

@pytest.mark.parametrize("stats,expected_league,expected_division,expected_rank",[
    (
        [{'seasonId': '4zone_5v5_ga2_c3s1_32a',
          'eventInstanceId': 'GA2_SEASON_32A:O1665435600000',
          'league': 'BRONZIUM', 'wins': 0, 'losses': 0, 'eliteDivision': False,
          'seasonPoints': 0, 'division': 10, 'joinTime': 1666672020000,
          'endTime': 1667768400000, 'remove': False, 'rank': 16718},
         {'seasonId': '4zone_5v5_ga2_c3s1_34a',
          'eventInstanceId': 'GA2_SEASON_34A:O1670277600000',
          'league': 'BRONZIUM', 'wins': 0, 'losses': 0, 'eliteDivision': False,
          'seasonPoints': 3911, 'division': 10, 'joinTime': 1670656636000,
          'endTime': 1672610400000, 'remove': False, 'rank': 9638}
        ],
        'BRONZIUM',
        4,
        9638,
    ),
    (
        [{'seasonId': '4zone_5v5_ga2_c3s1_32a',
          'eventInstanceId': 'GA2_SEASON_32A:O1665435600000',
          'league': 'BRONZIUM', 'wins': 0, 'losses': 0, 'eliteDivision': False,
          'seasonPoints': 5764, 'division': 25, 'joinTime': 1665445466000,
          'endTime': 1667768400000, 'remove': False, 'rank': 10867},
         {'seasonId': '4zone_3v3_ga2_c3s1_33a',
             'eventInstanceId': 'GA2_SEASON_33A:O1667858400000',
             'league': 'CHROMIUM', 'wins': 0, 'losses': 0, 'eliteDivision': False,
             'seasonPoints': 1477, 'division': 5, 'joinTime': 1667858417000,
             'endTime': 1670191200000, 'remove': False, 'rank': 5536},
         {'seasonId': '4zone_5v5_ga2_c3s1_34a',
          'eventInstanceId': 'GA2_SEASON_34A:O1670277600000',
          'league': 'BRONZIUM', 'wins': 0, 'losses': 0, 'eliteDivision': False,
          'seasonPoints': 1482, 'division': 20, 'joinTime': 1670277673000,
          'endTime': 1672610400000, 'remove': False, 'rank': 12069}
         ],
        'BRONZIUM',
        2,
        12069
    ),
    (
        [],
        'UNKNOWN',
        6,
        0
    ),
    (
        [{'division': 5}],
        'UNKNOWN',
        5,
        0
    ),
    (
        [{'division': 10}],
        'UNKNOWN',
        4,
        0
    ),
    (
        [{'division': 15}],
        'UNKNOWN',
        3,
        0
    ),
    (
        [{'division': 20}],
        'UNKNOWN',
        2,
        0
    ),
    (
        [{'division': 25}],
        'UNKNOWN',
        1,
        0
    ),
])
def test_parse_gac_stats(stats, expected_league, expected_division, expected_rank):
    gac_stats = client.parse_gac_stats(stats)
    assert gac_stats['league'] == expected_league
    assert gac_stats['division'] == expected_division
    assert gac_stats['rank'] == expected_rank

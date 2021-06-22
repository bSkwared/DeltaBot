from api_swgoh_help import api_swgoh_help, settings

# Change the settings below
creds = settings('<USERNAME>', '<PASSWORD>')
client = api_swgoh_help(creds)
allycode = 123456789


def getGuild(api_client, allycode):
    """ :parameters api_swgoh_help instance and player allycode """
    payload = {'allycodes': [allycode], 'language': "eng_us", 'enums': True}
    result = api_client.fetchGuilds(payload)
    return result


def getGuildAllycodes(guild_dict):
    allycodes = []
    g_members = guild_dict[0]['roster']
    for g_member in g_members:
        try:
            allycodes.append(g_member['allyCode'])
        except Exception as e:
            print("Exception caught: {0}".format(str(e)))
            print("Guild member: {0}".format(g_member))
            print("Input type: {}".format(type(guild_dict)))
            # pprint.pprint(guild_dict)
            return ([])
    return allycodes


# Fetch a list of guild member allycodes
members = getGuild(client, allycode)
g_allycodes = getGuildAllycodes(members)
print(g_allycodes)
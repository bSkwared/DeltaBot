import json
with open('/home/nopass/test/DeltaBot/deltabot/daily_data/2023_07_21.py', 'r') as fp:
    old = json.loads(fp.read())
with open('/home/nopass/test/DeltaBot/deltabot/daily_data/2023_10_18.py', 'r') as fp:
    new = json.loads(fp.read())

old_mods_above_10 = {}
new_mods_above_10 = {}
name = {}
for member in old['guild_members'].keys():
    old_mods_above_10[member] = sum(old['guild_members'][member]['speed_mods'][5:])

for member in new['guild_members'].keys():
    new_mods_above_10[member] = sum(new['guild_members'][member]['speed_mods'][5:])
    name[member] = new['guild_members'][member]['name']

diff = []
for ac, name in name.items():
    if ac not in old_mods_above_10:
        continue
    diff.append((name, new_mods_above_10[ac] - old_mods_above_10[ac]))

diff = sorted(diff, key=lambda i: i[1])
print('\n'.join(map(lambda t: f'{t[0]}\t{t[1]}', diff)))





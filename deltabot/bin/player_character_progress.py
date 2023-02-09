import json
import api_swgoh_help.client as ash_client

start_file = 'our_guild_dec8.json'
end_file = 'our_guild_dec30.json'

with open(start_file, 'r') as fp:
    initial = json.load(fp)

with open(end_file, 'r') as fp:
    final = eval(fp.read())


# Map {allycode: {toon_id: Toon}}
initial_map = {}
final_map = {}
initial_gp = {}
gp_diff = {}

# Map {allycode: name}
names = {}
for p in initial + final:
    names[p['allyCode']] = p['name']


def parse_toons(roster):
    toons = {}
    for t in roster:
        toon = {}
        toon['stars'] = t['rarity']
        toon['gear_level'] = t['gear']
        toon['gear_slots_filled'] = len(t['equipped'])
        toon['relic'] = t['relic']['currentTier'] if t['relic'] else 0
        toons[t['nameKey']] = toon

    return toons


for p in initial:
    initial_gp[p['allyCode']] = sum(ash_client.parse_gp_stats(p['stats']).values())
    initial_map[p['allyCode']] = parse_toons(p['roster'])

for p in final:
    gp_diff[p['allyCode']] = sum(ash_client.parse_gp_stats(p['stats']).values()) - initial_gp.get(p['allyCode'], 0)
    final_map[p['allyCode']] = parse_toons(p['roster'])

lowest_gps = sorted(gp_diff.values())
cutoff = lowest_gps[5]
print(cutoff)
print(lowest_gps[0])

for ac, toons in final_map.items():
    initial_toons = initial_map.get(ac)
    if not initial_toons:
        print(f'Skipping {names[ac]}, not found in initial map')
        continue


    print(f'\n\nComparing toons for {names[ac]}')
    for name, t in toons.items():
        if name not in initial_toons:
            diffs = f'{name} - '
            for i_k, i_v in t.items():
                diffs += f'{i_k}: {i_v}, '
        elif t != initial_toons[name]:
            diffs = f'{name} - '
            for (i_k, i_v), (f_k, f_v) in zip(initial_toons[name].items(), t.items()):
                if i_v != f_v:
                    diffs += f'{f_k}: {i_v} -> {f_v}, '


            print(diffs)




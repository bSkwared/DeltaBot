import peewee as PW
import sys
import ntplib
import json
import os
import datetime

db = PW.SqliteDatabase('dev.db')
tables_to_create = []

class BaseModel(PW.Model):
    class Meta:
        database = db


class Guild(BaseModel):
    ref_id = PW.CharField(unique=True)
    name = PW.CharField()

tables_to_create.append(Guild)


class Player(BaseModel):
    allycode = PW.IntegerField(unique=True)
    name = PW.CharField()

tables_to_create.append(Player)


class CollectionTime(BaseModel):
    time = PW.DateTimeField()

tables_to_create.append(CollectionTime)


class PlayerStats(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    player = PW.ForeignKeyField(Player, backref='stats')
    guild = PW.ForeignKeyField(Guild, backref='stats')
    ship_gp = PW.IntegerField()
    toon_gp = PW.IntegerField()
    gac_league = PW.CharField()
    gac_division = PW.IntegerField()
    gac_rank = PW.IntegerField()
    fleet_arena_rank = PW.IntegerField()
    squad_arena_rank = PW.IntegerField()

tables_to_create.append(PlayerStats)


class Toon(BaseModel):
    toon_id = PW.CharField(unique=True)
    name = PW.CharField()
    player = PW.ForeignKeyField(Player, backref='toons')

tables_to_create.append(Toon)
     

class AbilityDefinition(BaseModel):
    ability_id = PW.CharField(unique=True)
    tiers = PW.IntegerField()
    is_zeta = PW.BooleanField()

tables_to_create.append(AbilityDefinition)


class AbilityLevel(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    toon = PW.ForeignKeyField(Toon, backref='abilities')
    tier = PW.IntegerField()
    ability_definition = PW.ForeignKeyField(AbilityDefinition)

tables_to_create.append(AbilityLevel)


class ToonStats(BaseModel):
    player_stats = PW.ForeignKeyField(PlayerStats, backref='toons')
    gp = PW.IntegerField()
    stars = PW.IntegerField()
    gear_level = PW.IntegerField()
    relic_level = PW.IntegerField()
    gear_slots_filled = PW.IntegerField()

tables_to_create.append(ToonStats)


class Mod(BaseModel):
    id = PW.CharField(unique=True)
    shape = PW.IntegerField()
    mod_set = PW.IntegerField()
    primary_stat = PW.CharField()

tables_to_create.append(Mod)


class ModStats(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    mod = PW.ForeignKeyField(Mod, backref='stats')
    dots = PW.IntegerField()
    color = PW.CharField()
    level = PW.IntegerField()
    primary_value = PW.CharField()

tables_to_create.append(ModStats)


class SecondaryStat(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    mod = PW.ForeignKeyField(Mod, backref='secondaries')
    stat = PW.CharField()
    value = PW.CharField()
    num_rolls = PW.IntegerField()

tables_to_create.append(SecondaryStat)


class ModAssignment(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    toon = PW.ForeignKeyField(Toon, backref='mods')
    mod = PW.ForeignKeyField(Mod, backref='toon')

tables_to_create.append(ModAssignment)


db.create_tables(tables_to_create)
#Player(allycode=917787877, name='RedFox').save()

player_dump = {}
with open('guild_player_stats.json', 'r') as fp:
    player_dump = json.load(fp)


c = ntplib.NTPClient()
r = c.request('time.google.com')
log_time = datetime.datetime.fromtimestamp(r.tx_time, datetime.timezone.utc)
print(log_time)
time, is_new_time = CollectionTime.get_or_create(time=log_time)
if not is_new_time:
    print("ERROR: this time has already collected all statistics")

def parse_gp_stats(stats):
    gp_stats = {}
    for stat in stats:
        if stat['nameKey'] == 'Galactic Power (Ships):':
            gp_stats['ships'] = stat['value']
        elif stat['nameKey'] == 'Galactic Power (Characters):':
            gp_stats['toons'] = stat['value']

    return gp_stats

def convert_gac_division(division):
    return 6 - (division//5)

guilds_seen = {}
for player in player_dump:
    start_creation = datetime.datetime.now()
    #breakpoint()

    # Load current player, create if new, update name if changed
    try:
        p = Player().get(Player.allycode == player['allyCode'])
        if p.name != player['name']:
            p.name = player['name']
            p.save()
            print('name saved')
    except Player.DoesNotExist:
        p = Player(allycode=player['allyCode'], name=player['name'])
        p.save()


    # Load player's guild, create if new, update name if changed
    gid = player['guildRefId']
    if gid in guilds_seen:
        g = guilds_seen[gid]
        print('found guild in map')

    else:
        try:
            g = Guild().get(Guild.ref_id == player['guildRefId'])
            if g.name != player['guildName']:
                g.name = player['guildName']
                g.save()
            print('foundu guild in db')
        except Guild.DoesNotExist:
            print('creating new guild')
            g = Guild(ref_id=player['guildRefId'], name=player['guildName'])
            g.save()


    guilds_seen[gid] = g
    print(g)


    gp_stats = parse_gp_stats(player['stats'])
    grand_arena = player['grandArena'][-1] if len(player['grandArena']) else {'league': 'UNKNOWN', 'division': 'UNKNOWN', 'rank': 69420}
    ps = PlayerStats(time=time,
                     player=p,
                     guild=g,
                     ship_gp=gp_stats['ships'],
                     toon_gp=gp_stats['toons'],
                     gac_league=grand_arena['league'],
                     gac_division=convert_gac_division(grand_arena['division']),
                     gac_rank=grand_arena['rank'],
                     fleet_arena_rank=player['arena']['ship']['rank'],
                     squad_arena_rank=player['arena']['char']['rank'])
    ps.save()

    for toon in player['roster']:
        try:
            t = Toon().get(Toon.toon_id == toon['id'])
        except Toon.DoesNotExist:
            t = Toon(toon_id=toon['id'], name=toon['nameKey'], player=p)
            t.save()


        for ability in toon['skills']:
            try:
                ad = AbilityDefinition().get(AbilityDefinition.ability_id == ability['id'])
                if ad.tiers != ability['tiers'] or ad.is_zeta != ability['isZeta']:
                    ad.tiers = ability['tiers']
                    ad.is_zeta = ability['isZeta']
                    ad.save()
            except AbilityDefinition.DoesNotExist:
                ad = AbilityDefinition(ability_id=ability['id'], tiers=ability['tiers'], is_zeta=ability['isZeta'])
                ad.save()

            try:
                al = AbilityLevel().get(toon=t, tier=ability['tier'], ability_definition=ad)
            except AbilityLevel.DoesNotExist:
                al = AbilityLevel(time=time, toon=t, tier=ability['tier'], ability_definition=ad)
                al.save()

    end_time = datetime.datetime.now()
    print(f'Finished player in {end_time - start_creation}')






    #sd = StatsDump(guild=Guild(ref_id=player['guildRefId']), timestamp=log_time, player=p)
    #sd.save()

    #for unit in player['roster']:
    #    t = Toon(stats_dump=sd, stars=unit['rarity'], gear_level=unit['gear'], relic_level=unit['relic']['currentTier'])




    

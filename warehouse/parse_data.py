import peewee as PW
import sys
import ntplib
import json
import os
import datetime

db = PW.SqliteDatabase('dev.db')
def create_tables(db):
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
    db.create_tables(tables_to_create)

def load_json(filename):
    player_dump = {}
    with open(sys.argv[1], 'r') as fp:
        player_dump = json.load(fp)
    return player_dump


def get_log_time():
    c = ntplib.NTPClient()
    r = c.request('time.google.com')
    log_time = datetime.datetime.fromtimestamp(r.tx_time, datetime.timezone.utc)
    time, is_new_time = CollectionTime.get_or_create(time=log_time)
    if not is_new_time:
        print("ERROR: this time has already collected all statistics")
    return time

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
stat_names = {}
toons_seen = {}
AD_seen = {}
start_creation = datetime.datetime.now()

def get_stat_name_obj(stat_name):
    if stat_name in stat_names:
        return stat_names[stat_name]

    try:
        sn = Stat().get(Stat.stat_name == stat_name)
    except Stat.DoesNotExist:
        sn = Stat(stat_name=stat_name)
        sn.save()
    stat_names[stat_name] = sn

    return sn


def get_or_create_mod(mod_id, shape, mod_set, primary_stat):
    try:
        m = Mod().get(Mod.mod_id == mod_id)
    except Mod.DoesNotExist:
        m = Mod(mod_id=mod_id, shape=shape, mod_set=mod_set,
                primary_stat=primary_stat)
        m.save()
    return m

with db.atomic() as transactoin:
    for player in player_dump:
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

        else:
            try:
                g = Guild().get(Guild.ref_id == player['guildRefId'])
                if g.name != player['guildName']:
                    g.name = player['guildName']
                    g.save()
                print('found guild in db')
            except Guild.DoesNotExist:
                print('creating new guild')
                g = Guild(ref_id=player['guildRefId'], name=player['guildName'])
                g.save()


        guilds_seen[gid] = g


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



end_time = datetime.datetime.now()
print(f'Finished all players in {end_time - start_creation}')
print(f'Averaged {(end_time - start_creation)/len(player_dump)} per player')



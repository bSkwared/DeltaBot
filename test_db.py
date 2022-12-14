import peewee as PW
import ntplib
import datetime
import json
import os
import datetime

db = PW.SqliteDatabase('dev.db')

class BaseModel(PW.Model):
    class Meta:
        database = db

class Guild(BaseModel):
    ref_id = PW.CharField(primary_key=True)
    name = PW.CharField()

class Player(BaseModel):
    ally_code = PW.IntegerField(unique=True)
    name = PW.CharField()

class StatsDump(BaseModel):
    timestamp = PW.DateTimeField()
    player = PW.ForeignKeyField(Player)
    guild = PW.ForeignKeyField(Guild)

class Toon(BaseModel):
    stats_dump = PW.ForeignKeyField(StatsDump)
    gp = PW.IntegerField()
    stars = PW.IntegerField()
    gear_level = PW.IntegerField()
    relic_level = PW.IntegerField()
    gear_slots_filled = PW.IntegerField()

class Mod(BaseModel):
    shape = PW.IntegerField()
    mod_set = PW.IntegerField()
    dots = PW.IntegerField()
    color = PW.CharField()
    level = PW.IntegerField()
    primary_stat = PW.CharField()
    primary_value = PW.CharField()

class SecondaryStat(BaseModel):
    stat = PW.CharField()
    value = PW.CharField()
    num_rolls = PW.IntegerField()

db.create_tables([Guild, Player, StatsDump, Toon, Mod, SecondaryStat])
#Player(ally_code=917787877, name='RedFox').save()

player_dump = {}
with open('guild_player_stats.json', 'r') as fp:
    player_dump = json.load(fp)


c = ntplib.NTPClient()
r = c.request('time.google.com')
log_time = datetime.datetime.fromtimestamp(r.tx_time, datetime.timezone.utc)

for player in player_dump:
    #breakpoint()
    p, _ = Player.get_or_create(ally_code=player['allyCode'], name=player['name'])

    sd = StatsDump(guild=Guild(ref_id=player['guildRefId']), timestamp=log_time, player=p)
    sd.save()

    for unit in player['roster']:
        t = Toon(stats_dump=sd, stars=unit['rarity'], gear_level=unit['gear'], relic_level=unit['relic']['currentTier']




    

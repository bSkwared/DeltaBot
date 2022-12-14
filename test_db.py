import peewee as PW
import datetime

db = PW.SqliteDatabase('dev.db')

class Guild(PW.Model):
    name = PW.CharField()

class Player(PW.Model):
    ally_code = PW.IntegerField(unique=True)
    name = PW.CharField()

class StatsDump(PW.Model):
    timestamp = DateTimeField()
    player = PW.ForeignKeyField(Player)
    guild = PW.ForeignKeyField(Guild)

class Toon(PW.Model):
    gp = PW.IntegerField()
    stars = PW.IntegerField()
    gear_level = PW.IntegerField()
    relic_level = PW.IntegerField()
    gear_slots_filled = PW.IntegerField()

class Mod(PW.Model):
    shape = PW.IntegerField()
    mod_set = PW.IntegerField()
    dots = PW.IntegerField()
    color = PW.CharField()
    level = PW.IntegerField()
    primary_stat = PW.CharField()
    primary_value = PW.CharField()

class SecondaryMod(PW.Model):
    stat = PW.CharField()
    value = PW.CharField()
    num_rolls = PW.IntegerField()

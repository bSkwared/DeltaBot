import peewee as PW
from datetime import datetime, timezone
import warehouse.data as WD
import ntplib

def print_max_rank():
    players = WD.Player.select()
    max_fleet = 0
    max_squad = 0
    for p in players:
        max_fleet = max(max_fleet, p.fleet_rank)
        max_squad = max(max_squad, p.squad_rank)
    print(f'Max fleet rank: {max_fleet}')
    print(f'Max squad rank: {max_squad}')


def get_individual_gp_progress(guild_id, begin, end):
    '''
    Parameters:
    guild_id (str): Guild ID to get GP progress for.
    begin (datetime): Time to start looking for GP after.
    end (datetime): Time to end looking for GP after.

    Returns:
    List((datetime, int)): List of tuples with time and GP, chronologically
    '''
    times = (WD.CollectionTime
             .select()
             .where((begin < WD.CollectionTime.time)
                  & (WD.CollectionTime.time < end))
             .order_by(WD.CollectionTime.time.asc()))

    before = True
    dates = []
    gp_before = {}
    gp_progress = {}
    names = {}
    for t in (times[0], times[-1]):
        print(f'Found time {t}: {t.time}')
        dates.append(t)
        try:
            mxp  = (WD.Player
                   .select()
                   .where((WD.Player.time == t)
                          & (WD.Player.guild_id == guild_id)))
        except:
            continue

        for p in mxp:
            if before:
                gp_before[p.allycode] = p.character_gp + p.ship_gp
            elif p.allycode in gp_before:
                names[p.allycode] = p.name
                gp_progress[p.allycode] = (gp_before[p.allycode], p.character_gp + p.ship_gp)
                
        before = False

    return dates, gp_progress, names

def get_guild_gp_progress(guild_id, begin, end):
    '''
    Parameters:
    guild_id (str): Guild ID to get GP progress for.
    begin (datetime): Time to start looking for GP after.
    end (datetime): Time to end looking for GP after.

    Returns:
    List((datetime, int)): List of tuples with time and GP, chronologically
    '''
    times = (WD.CollectionTime
             .select()
             .where((begin < WD.CollectionTime.time)
                  & (WD.CollectionTime.time < end))
             .order_by(WD.CollectionTime.time.asc()))

    progress = []
    m = (WD.Player
         .select(WD.Player.allycode, WD.Player.name, PW.fn.COUNT().alias('count'))
         .group_by(WD.Player.allycode))




    for t in times:
        print(f'Found time {t}: {t.time}')
        mxp  = (WD.Player
               .select(WD.Player.id)
               .where(WD.Player.time <= t)
               .group_by(WD.Player.allycode)
               .having(WD.Player.time == PW.fn.MAX(WD.Player.time)))
        in_guild = (WD.Player
                    .select()
                    #.select(WD.Player.time, WD.Player.character_gp, WD.Player.ship_gp)
                    .join(mxp, on=(WD.Player.id == mxp.c.id))
                    #.where(WD.Player.guild_id == guild_id))
                    #for stormcrow
                    .where((WD.Player.guild_id == guild_id) & (WD.Player.allycode == 413742635)))


        total_gp = sum([p.character_gp + p.ship_gp for p in in_guild])
        print(total_gp)
        progress.append((t.time, total_gp))

    return progress

'''
class CollectionTime(BaseModel):
    time = PW.DateTimeField()


class Guild(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    guild_id = PW.CharField()
    name = PW.CharField()
    description = PW.CharField()


class Player(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    allycode = PW.IntegerField()
    name = PW.CharField()
    guild_id = PW.CharField()
    ship_gp = PW.IntegerField()
    character_gp = PW.IntegerField()
    gac_league = PW.CharField()
    gac_division = PW.IntegerField()
    gac_rank = PW.IntegerField()
    fleet_rank = PW.IntegerField()
    squad_rank = PW.IntegerField()
'''

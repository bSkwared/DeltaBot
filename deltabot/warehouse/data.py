import peewee as PW
from datetime import datetime, timezone
import ntplib

global_db = None
database_proxy = PW.DatabaseProxy()

class BaseModel(PW.Model):
    class Meta:
        database = database_proxy


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


class Toon(BaseModel):
    toon_id = PW.CharField(unique=True)
    name = PW.CharField()
    player = PW.ForeignKeyField(Player)


class ToonStats(BaseModel):
    time = PW.ForeignKeyField(CollectionTime)
    toon = PW.ForeignKeyField(Toon)
    stars = PW.IntegerField()
    gear_level = PW.IntegerField()
    relic_level = PW.IntegerField()


def setup_warehouse(db_filename):
    db = PW.SqliteDatabase(db_filename)
    #global_db = PW.SqliteDatabase(db_filename)
    database_proxy.initialize(db)
    #database_proxy.initialize(global_db)

    tables = [
        CollectionTime,
        Guild,
        Player,
        Toon,
        ToonStats,
    ]
    db.create_tables(tables)

def get_or_create_guild(client_guild, time):
    """Read guild from database or if it has been updated, update the database.

    Parameters:
    client_guild (client.Guild): Current guild information.
    time (CollectionTime): Time of data collection

    Returns:
    data.Guild: Most recent Guild object from the database, whether new or not.
    """
    # For now, we will just save everything since it will make this easier
    # TODO: optimize db to only store updates
    '''
    try:
        # Try to read guild and verify name and description are unchanged
        return Guild().get((Guild.guild_id == client_guild.guild_id) &
                           (Guild.name == client_guild.name) &
                           (Guild.description == client_guild.description))

    except Guild.DoesNotExist:
        pass
    '''

    # If name/description are changed or guild doesn't exist, create a new entry
    guild = Guild(time=time, guild_id=client_guild.guild_id,
                  name=client_guild.name, description=client_guild.description)
    guild.save()
    return guild


def get_toon(toon):
    try:
        return Toon().get(Toon.toon_id == toon.toon_id)
    except Toon.DoesNotExist:
        return None


def get_toon_stats(warehouse_toon, client_toon):
    ct = client_toon
    try:
        return ToonStats().get((ToonStats.toon == warehouse_toon) &
                               (ToonStats.stars == ct.stars) &
                               (ToonStats.gear_level == ct.gear_level) &
                               (ToonStats.relic_level == ct.relic_level))
    except ToonStats.DoesNotExist:
        return None


def update_roster(client_player, warehouse_player, time):
    cp = client_player
    wp = warehouse_player
    for ct in cp.roster:
        if not ct.name:
            print(f'ERROR: {ct.name} is empty for {ct.toon_id}')
            continue
        t = get_toon(ct)
        if not t:
            t = Toon(toon_id=ct.toon_id, name=ct.name, player=wp)
            t.save()

        ts = get_toon_stats(t, ct)
        if not ts:
            ts = ToonStats(time=time, toon=t, stars=ct.stars,
                           gear_level=ct.gear_level, relic_level=ct.relic_level)
            ts.save()


def get_or_create_player(client_player, time):
    """Read player from database or if it has been updated, update the database.

    Parameters:
    client_player (client.Player): Current player information.
    time (CollectionTime): Time of data collection

    Returns:
    data.Player: Most recent Player object from the database, whether new or not.
    """
    # For now, we will just save everything since it will make this easier
    # TODO: optimize db to only store updates
    '''
    try:
        # Try to read player and verify name and description are unchanged
        return Player.get((Player.allycode == client_player.allycode) &
                          (Player.name == client_player.name) &
                          (Player.guild_id == client_player.guild_id) &
                          (Player.ship_gp == client_player.ship_gp) &
                          (Player.character_gp == client_player.character_gp) &
                          (Player.gac_league == client_player.gac_league) &
                          (Player.gac_division == client_player.gac_division) &
                          (Player.gac_rank == client_player.gac_rank) &
                          (Player.fleet_rank == client_player.fleet_rank) &
                          (Player.squad_rank == client_player.squad_rank))

    except Player.DoesNotExist:
        pass
    '''
    p = client_player
    player = Player(time=time, allycode=p.allycode, name=p.name,
                    guild_id=p.guild_id, ship_gp=p.ship_gp,
                    character_gp=p.character_gp, gac_league=p.gac_league,
                    gac_division=p.gac_division, gac_rank=p.gac_rank,
                    fleet_rank=p.fleet_rank, squad_rank=p.squad_rank)
    player.save()

    update_roster(client_player, player, time)

    return player


def get_current_datetime():
    try:
        c = ntplib.NTPClient()
        r = c.request('pool.ntp.org')
        return (datetime
                .fromtimestamp(r.tx_time, timezone.utc)
                .replace(microsecond=0)
                .replace(tzinfo=None))
    except Exception as e:
        print('ERROR": Unable to reach ntp server - {e}')
        return datetime.now()

def get_latest_guild_members(guild_id):
    latest_time = (Player
                   .select(PW.fn.MAX(Player.time))
                   .where(Player.guild_id == guild_id)).get()
    print(f'{latest_time.time.time}')

    return get_guild_members(guild_id, latest_time.time)


def get_guild_members(guild_id, time):
    return (Player
            .select()
            .where((Player.guild_id == guild_id)
                 & (Player.time == time)))

def save_data(guilds, players, collection_time):
    """Save guilds and players into database. (not true atm: Only updated if there is a change).

    Parameters:
    collection_time (datetime): Time of data collection
    guilds (List[client.Guild]): Guilds to update.
    players (List[client.Player]): Players to update.
    """
    time, is_new_time = CollectionTime.get_or_create(time=collection_time)
    if not is_new_time:
        print("WARN: this time has already saved stats")

    with database_proxy.atomic():
        for g in guilds:
            get_or_create_guild(g, time)

        for p in players:
            try:
                get_or_create_player(p, time)
            except:
                print(f'ERROR: Unable to create player {p.allycode}, {p.name}, {p.guild_id}, {p.ship_gp}, {p.character_gp}, {p.gac_league}, {p.gac_division}, {p.gac_rank}, {p.fleet_rank}, {p.squad_rank}')
                pass

def get_allycodes():
    ps = Player().select(PW.fn.DISTINCT(Player.allycode))
    return [p.allycode for p in ps]


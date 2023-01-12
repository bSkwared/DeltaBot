import peewee as PW

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

def setup_warehouse(db_filename):
    db = PW.SqliteDatabase(db_filename)
    database_proxy.initialize(db)

    tables = [
        CollectionTime,
        Guild,
        Player,
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
    try:
        # Try to read guild and verify name and description are unchanged
        return Guild().get((Guild.guild_id == client_guild.guild_id) &
                           (Guild.name == client_guild.name) &
                           (Guild.description == client_guild.description))

    except Guild.DoesNotExist:
        pass

    # If name/description are changed or guild doesn't exist, create a new entry
    guild = Guild(time, client_guild.guild_id, client_guild.name,
                  client_guild.description)
    guild.save()
    return guild


def get_or_create_player(client_player, time):
    """Read player from database or if it has been updated, update the database.

    Parameters:
    client_player (client.Player): Current player information.
    time (CollectionTime): Time of data collection

    Returns:
    data.Player: Most recent Player object from the database, whether new or not.
    """
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

    print(f'blake: time {time}')
    player = Player(time=time, allycode=client_player.allycode, name=client_player.name,
                    guild_id=client_player.guild_id, ship_gp=client_player.ship_gp,
                    character_gp=client_player.character_gp, gac_league=client_player.gac_league,
                    gac_division=client_player.gac_division, gac_rank=client_player.gac_rank,
                    fleet_rank=client_player.fleet_rank, squad_rank=client_player.squad_rank)
    player.save()
    return player


def save_data(guilds, players, collection_time):
    """Save guilds and players into database. Only updated if there is a change.

    Parameters:
    collection_time (datetime): Time of data collection
    guilds (List[client.Guild]): Guilds to update.
    players (List[client.Player]): Players to update.
    """
    time, is_new_time = CollectionTime.get_or_create(time=collection_time)
    if not is_new_time:
        print("WARN: this time has already saved stats")

    for g in guilds:
        get_or_create_guild(g, time)

    for p in players:
        get_or_create_player(p, time)


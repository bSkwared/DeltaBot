import peewee as PW

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

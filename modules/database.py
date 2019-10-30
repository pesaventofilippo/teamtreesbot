from pony.orm import Database, Required, Optional

db = Database("sqlite", "../teamtreesbot.db", create_db=True)


class Chat(db.Entity):
    chatId = Required(int, sql_type='BIGINT')


class Data(db.Entity):
    trees = Required(int, default=0)
    topTen = Optional(str)
    lastGoal = Required(int, default=0)
    total = Required(int, default=20000000)


db.generate_mapping(create_tables=True)

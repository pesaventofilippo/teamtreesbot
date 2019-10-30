from pony.orm import Database, Required, Optional

db = Database("sqlite", "../teamtreesbot.db", create_db=True)


class Chat(db.Entity):
    chatId = Required(int)
    isGroup = Required(bool, default=False)


class Data(db.Entity):
    trees = Required(int, default=0)
    topTen = Optional(str)
    lastGoal = Required(int, default=0)
    total = Required(int, default=20000000)


db.generate_mapping(create_tables=True)

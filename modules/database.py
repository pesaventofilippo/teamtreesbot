from pony.orm import Database, Required

db = Database("sqlite", "../teamtreesbot.db", create_db=True)


class Chat(db.Entity):
    chatId = Required(int)
    isGroup = Required(bool, default=False)


class Data(db.Entity):
    trees = Required(int, default=0)
    lastGoal = Required(int, default=0)


class Message(db.Entity):
    trees = Required(str, default="<i>Server Error.</i>")


db.generate_mapping(create_tables=True)

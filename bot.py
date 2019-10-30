from telepot import Bot
from telepot.exception import TelegramError, BotWasBlockedError, BotWasKickedError
from time import sleep
from threading import Thread
from pony.orm import db_session, select
from bs4 import BeautifulSoup
from requests import get
from random import randint
from modules.database import Chat, Data


try:
    f = open('token.txt', 'r')
    token = f.readline().strip()
    f.close()
except FileNotFoundError:
    token = input(" * Paste here the BotFather API Token: ")
    f = open('token.txt', 'w')
    f.write(token)
    f.close()

bot = Bot(token)
goalInterval = 500000


@db_session
def fetchData():
    if not Data.exists(lambda d: d.id == 0):
        Data(id=0)
    data = Data.get(id=0)
    res = get('https://www.teamtrees.org/')
    soup = BeautifulSoup(res.content, "html.parser")
    trees = int(soup.find(id="totalTrees").get_attribute_list("data-count")[0])
    data.trees = trees


@db_session
def sendUpdates():
    data = Data.get(id=0)
    currentGoal = data.trees - data.trees % goalInterval
    if currentGoal > data.lastGoal:
        for chat in select(c for c in Chat)[:]:
            try:
                bot.sendMessage(chat.chatId, "🌲 #TeamTrees just reached <b>{:,} trees!</b>".format(currentGoal), parse_mode="HTML")
            except (BotWasBlockedError, BotWasKickedError):
                chat.delete()
            except TelegramError:
                pass
    data.lastGoal = currentGoal


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    text = msg['text'].replace('@' + bot.getMe()['username'], "")
    data = Data.get(id=0)

    if not Chat.exists(lambda c: c.chatId == chatId):
        Chat(chatId=chatId)
    chat = Chat.get(chatId=chatId)

    if text == "/start":
        bot.sendMessage(chatId, "Hey, <b>{}</b> 👋🏻\n"
                                "This is the <b>#TeamTrees Bot</b> :)\n"
                                "Type /trees to see the current status.\n\n"
                                "🌲 🌳 🌴 🎄 🍃 🌿 🌱".format(name), parse_mode="HTML")
        bot.sendSticker(chatId, "CAADBAADdwADzuP8FeiKBxqq6gfLFgQ")

    elif text == "/trees":
        trees = data.trees
        total = data.total
        remaining = total - trees
        bot.sendMessage(chatId, "<b>#TeamTrees Status</b>\n\n"
                                "🌱 Trees Planted: <b>{:,} ({}%)</b>\n"
                                "🌿 Remaining: <b>{:,} ({}%)</b>\n"
                                "🌳 Final Goal: <b>{:,}</b> trees\n\n"
                                "🌲 teamtrees.org".format(trees, round(trees*100/total, 2), remaining,
                                                          round(remaining*100/total, 2), total), parse_mode="HTML")

    elif text == "/stickers":
        stickList = ["CAADBAADcgADzuP8Fb--m9HX6prgFgQ", "CAADBAADcwADzuP8FcvqieezaDU8FgQ",
                     "CAADBAADdAADzuP8FUqO7MJGu2WcFgQ", "CAADBAADdQADzuP8FX1KYl9MWeJkFgQ",
                     "CAADBAADegADzuP8FXI3aGoccbBYFgQ", "CAADBAADdgADzuP8Fcw9U24tumhEFgQ"]
        ind = randint(0, 5)
        bot.sendSticker(chatId, stickList[ind])


def accept_msgs(msg):
    Thread(target=reply, args=[msg]).start()


bot.message_loop({'chat': accept_msgs})

while True:
    fetchData()
    sendUpdates()
    sleep(60)

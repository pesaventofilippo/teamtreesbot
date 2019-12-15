from telepot import Bot
from telepot.exception import TelegramError, BotWasBlockedError, BotWasKickedError
from pony.orm import db_session, select
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime
from threading import Thread
from random import randint
from time import sleep
from modules.database import Chat, Data, Message


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


@db_session
def fetchData():
    if not Data.exists(lambda d: d.id == 0):
        Data(id=0)
    data = Data.get(id=0)
    res = get('https://www.teamtrees.org')
    soup = BeautifulSoup(res.content, "html.parser")
    trees = int(soup.find(id="totalTrees").get_attribute_list("data-count")[0])
    data.trees = trees


@db_session
def sendUpdates():
    data = Data.get(id=0)
    goalInterval = 500000
    currentGoal = data.trees - data.trees % goalInterval
    if currentGoal > data.lastGoal:
        for chat in select(c for c in Chat)[:]:
            try:
                chatId = chat.chatId if not chat.isGroup else int("-100" + str(chat.chatId))
                bot.sendMessage(chatId, "🌲 #TeamTrees just reached <b>{:,} trees!</b>".format(currentGoal), parse_mode="HTML")
            except (BotWasBlockedError, BotWasKickedError):
                chat.delete()
            except TelegramError:
                pass
    data.lastGoal = currentGoal


@db_session
def createMessage():
    if not Message.exists(lambda m: m.id == 0):
        Message(id=0)
    message = Message.get(id=0)
    data = Data.get(id=0)
    trees = data.trees
    totalTrees = 20000000
    remainingTrees = totalTrees - trees
    days = (datetime.now() - datetime(2019,10,25)).days
    totalDays = 68
    remainingDays = totalDays - days
    remainingTrees = max(0, remainingTrees)
    remainingDays = max(0, remainingDays)
    message.trees = "<b>#TeamTrees Status</b>\n\n" \
              "🌱 Trees Planted: <b>{:,} ({}%)</b>\n" \
              "🌿 Remaining: <b>{:,} ({}%)</b>\n" \
              "🌳 Final Goal: <b>{:,} trees</b>\n\n" \
              "📆 Days Passed: <b>{} days ({}%)</b>\n" \
              "🕙 Remaining: <b>{} days ({}%)</b>\n\n" \
              "🌲 teamtrees.org".format(trees, round(trees * 100 / totalTrees, 1), remainingTrees,
                                        round(remainingTrees * 100 / totalTrees, 1), totalTrees, days,
                                        round(days * 100 / totalDays, 1), remainingDays, round(remainingDays * 100 / totalDays, 1))


@db_session
def reply(msg):
    chatId = msg['chat']['id']
    name = msg['from']['first_name']
    text = msg['text'].replace('@' + bot.getMe()['username'], "")
    data = Data.get(id=0)
    message = Message.get(id=0)

    safeChatId = chatId if chatId > 0 else int(str(chatId)[4:])

    if not Chat.exists(lambda c: c.chatId == safeChatId):
        Chat(chatId=safeChatId, isGroup=chatId<0)
    chat = Chat.get(chatId=safeChatId)

    if text == "/start":
        bot.sendMessage(chatId, "Hey, <b>{}</b>!\n"
                                "This is the <b>#TeamTrees Bot</b> 👋🏻\n"
                                "Type /trees to see the current status, or /stickers to get the stickers pack.\n\n"
                                "🌲 🌳 🌴 🎄 🍃 🌿 🌱".format(name), parse_mode="HTML")
        bot.sendSticker(chatId, "CAADBAADdwADzuP8FeiKBxqq6gfLFgQ")

    elif text == "/trees":
        bot.sendMessage(chatId, message.trees, parse_mode="HTML")

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
    createMessage()
    sleep(20)

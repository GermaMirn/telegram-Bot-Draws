import telebot
from datetime import datetime
from telebot import types
from getBotInstance import bot
from db.dbRequests import addNewUser, checkDraw, getAllDraws, getStartDateDraw, getAuthorDraw, getInformationDraw, getEndDateDraw, getWinnersDraw, addParticipants, getParticipants

def welcomeUser(message):
    bot.send_message(
        message.chat.id,
        f"Приветсвую <b><u>{message.from_user.first_name}</u></b> в нашем Телеграм боте.\n\nЭтот телеграм бот <b>предоставляет</b> "
        "следующие опции:\n\t\t\t1)<b>Регистрация в розыгрыше</b>\n\t\t\t2)<b>Просмотр информации о розыгрыше</b>\n\t\t\t3)<b>Итоги розыгрыша</b>\n\nДля начало давай определимся с <b>Розыгрышем</b>, который тебя интересует:",
        parse_mode="html"
    )
    addNewUser(message.from_user.username, message.chat.id)

    showDrawMenu(message)

def showDrawMenu(message):
    allDraw = types.InlineKeyboardButton("Все возможные розыгрыши", callback_data="allDraw")
    writeDraw = types.InlineKeyboardButton("Ввести название розыгрыша", callback_data="writeDraw")

    drawMarkup = types.InlineKeyboardMarkup()
    drawMarkup.row(allDraw)
    drawMarkup.row(writeDraw)
    menuMessage = bot.send_message(message.chat.id, "Выбери один из пунктов:", reply_markup=drawMarkup)
    return menuMessage.message_id

def listOfDraws(message):
    try:
        for i in range(0, 2):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i)
    except:
        pass
    
    allDraws = getAllDraws()
    bot.send_message(message.chat.id,
                     f"<b>Все розыгрыши:</b>\n {'\n '.join(allDraws)} \n\n <b>Количество розыгрышей:{len(allDraws)}</b>",
                     parse_mode="html")

    markupDraw = types.ReplyKeyboardMarkup()
    for draw_name in allDraws:
        button = types.KeyboardButton(f"{draw_name}")
        markupDraw.add(button)
    
    bot.send_message(message.chat.id,
                     "Напишите мне какой вас розыгрышь интересует:",
                     parse_mode="html", reply_markup=markupDraw)    

def urlDrawMenu(message, drawName):
    try:
        for i in range(0, 4):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i)
    except:
        pass

    global CURRENTDRAW
    try: 
        CURRENTDRAW = drawName
    except:
        showDrawMenu(message)

    if checkDraw(drawName):
        InfoDrawUser = types.InlineKeyboardButton("Информация о розыгрыше", callback_data=f"infoDrawUser")
        participate = types.InlineKeyboardButton("Принять участие в розыгрыше", callback_data=f"participate")
        drawPanelMarkup = types.InlineKeyboardMarkup()
        drawPanelMarkup.row(InfoDrawUser)
        drawPanelMarkup.row(participate)

        bot.send_message(message.chat.id, f"Панель для '{CURRENTDRAW}' розыгрыша:", reply_markup=drawPanelMarkup)
    else:
        bot.send_message(message.chat.id, f"такой розыгрыш не найден: {CURRENTDRAW}")
        showDrawMenu(message)

def handleDrawName(message):
    try:
        for i in range(0, 4):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i)
    except:
        pass

    global CURRENTDRAW
    try: 
        CURRENTDRAW = message.text
    except:
        showDrawMenu(message)

    if checkDraw(message.text):
        InfoDrawUser = types.InlineKeyboardButton("Информация о розыгрыше", callback_data=f"infoDrawUser")
        participate = types.InlineKeyboardButton("Принять участие в розыгрыше", callback_data=f"participate")
        drawPanelMarkup = types.InlineKeyboardMarkup()
        drawPanelMarkup.row(InfoDrawUser)
        drawPanelMarkup.row(participate)

        bot.send_message(message.chat.id, f"Панель для '{CURRENTDRAW}' розыгрыша:", reply_markup=drawPanelMarkup)
    else:
        bot.send_message(message.chat.id, f"такой розыгрыш не найден: {CURRENTDRAW}")
        showDrawMenu(message)

userInfoMessages = {}
def InfoDrawUser(call):
    userID = call.from_user.id
    if userID in userInfoMessages:
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=userInfoMessages[userID])
        except:
            pass
    try:
        dateStr = str(getStartDateDraw(CURRENTDRAW))
        dateObject = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f")
        winners = getWinnersDraw(CURRENTDRAW)
        participates = getParticipants(CURRENTDRAW)
        lenParticipates = 0

        if list == type(winners):
            winners = '\n '.join(f"@{winner}" for winner in winners)

        if list == type(participates):
            lenParticipates = len(participates)

        infoMessage = bot.send_message(
            call.message.chat.id, 
            f"<b>Создатель розыгрыша:</b> {getAuthorDraw(CURRENTDRAW)}\n\n"
            f"<b>Описание розыгрыша:</b> {getInformationDraw(CURRENTDRAW)}\n\n"
            f"<b>Начало розыгрыша с {dateObject.strftime("%d.%m.%y")} до {getEndDateDraw(CURRENTDRAW)}</b>\n\n"
            f"<b>Победители в розыгрыше:</b>\n {winners}\n\n"
            f"<b>Количество участников:</b> {lenParticipates}", 
            parse_mode="html"
        )
        userInfoMessages[userID] = infoMessage.message_id
    except Exception as e:
        showDrawMenu(call.message)
        print(CURRENTDRAW, e)

def participate(call):
    try:
        participant = call.from_user.username
        answer = addParticipants(CURRENTDRAW, participant)
        bot.send_message(call.message.chat.id, f"{answer}")

    except Exception as e:
        print(e)
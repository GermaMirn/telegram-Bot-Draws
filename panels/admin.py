from telebot import types
from datetime import datetime
from getBotInstance import bot
from db.dbRequests import createDraw, deleteDraw, getAllDraws, addAdmin, deleteAdmin, getAllAdmins, getAllUsers, checkDraw, getAuthorDraw, getInformationDraw, getStartDateDraw, getEndDateDraw, addWinner, getWinnersDraw, getParticipants, getAllChatID, getDrawURLFromDb, deleteWinner, addTelegramChannelName, deleteTelegramChannelName, gettelegramChannelNames

def welcomeAdmin(message):
    bot.send_message(
        message.chat.id,
        "<b>Ку админ</b>.\n\nВот <b>главная</b> панель:", 
        parse_mode="html"
    )
    mainPanelAdmin(message)

def mainPanelAdmin(message):
    panelForDraw = types.InlineKeyboardButton("Панель розыгрыша", callback_data="panelForDraw")
    panelForStatistics = types.InlineKeyboardButton("Статистика Bota", callback_data="panelForStatistics")
    panelForNewDraw = types.InlineKeyboardButton("Создание нового розыгрыша", callback_data="panelForNewDraw")
    panelForAdmins= types.InlineKeyboardButton("Панель админов", callback_data="panelForAdmins")
    panelForNewsletter = types.InlineKeyboardButton("Рассылка информации", callback_data="panelForNewsletter")

    mainMarkup = types.InlineKeyboardMarkup()
    mainMarkup.row(panelForDraw, panelForStatistics)
    mainMarkup.row(panelForAdmins)
    mainMarkup.row(panelForNewDraw)
    mainMarkup.row(panelForNewsletter)

    bot.send_message(message.chat.id, "Главная панель админа: ", reply_markup=mainMarkup)


def panelForDraw(message):
    global CURRENTDRAW
    try: 
        CURRENTDRAW = message.text
    except:
        mainPanelAdmin(message)

    if checkDraw(message.text):
        InfoDraw = types.InlineKeyboardButton("Информация о розыгрыше", callback_data=f"infoDraw")
        getDrawURL = types.InlineKeyboardButton("Получить url для розыгрыша", callback_data=f"getDrawURL")
        deleteDraw = types.InlineKeyboardButton("Удалить розыгрыш", callback_data=f"deleteDraw")
        determineWinners = types.InlineKeyboardButton("Добавить победителя", callback_data=f"determineWinners")
        deleteWinners = types.InlineKeyboardButton("Удалить победителя", callback_data=f"deleteWinners")
        addSponsor = types.InlineKeyboardButton("Добавить спонсора", callback_data=f"addSponsor")
        deleteSponsor = types.InlineKeyboardButton("Удалить спонсора", callback_data=f"deleteSponsor")
        drawPanelMarkup = types.InlineKeyboardMarkup()
        drawPanelMarkup.row(InfoDraw)
        drawPanelMarkup.row(getDrawURL)
        drawPanelMarkup.row(determineWinners)
        drawPanelMarkup.row(deleteWinners)
        drawPanelMarkup.row(addSponsor)
        drawPanelMarkup.row(deleteSponsor)
        drawPanelMarkup.row(deleteDraw)

        bot.send_message(message.chat.id, f"Панель для '{CURRENTDRAW}' розыгрыша:", reply_markup=drawPanelMarkup)
    else:
        bot.send_message(message.chat.id, f"такой розыгрыш не найден: {CURRENTDRAW}")
        mainPanelAdmin(message)


def InfoDraw(call):
    try:
        dateStr = str(getStartDateDraw(CURRENTDRAW))
        dateObject = datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S.%f")
        winners = getWinnersDraw(CURRENTDRAW)
        participates = getParticipants(CURRENTDRAW)
        getTelegramChannelNames = gettelegramChannelNames(CURRENTDRAW)
        lenParticipates = 0

        if list == type(winners):
            winners = '\n '.join(f"@{winner}" for winner in winners)

        if list == type(participates):
            lenParticipates = len(participates)
            participates = '\n '.join(f"@{participate}" for participate in participates)

        if list == type(getTelegramChannelNames):
            getTelegramChannelNames = '\n '.join(f"@{telegramChannelNames}" for telegramChannelNames in getTelegramChannelNames)

        bot.send_message(
            call.message.chat.id, 
            f"<b>Создатель розыгрыша:</b> {getAuthorDraw(CURRENTDRAW)}\n\n"
            f"<b>Описание розыгрыша:</b> {getInformationDraw(CURRENTDRAW)}\n\n"
            f"<b>Начало розыгрыша с {dateObject.strftime("%d.%m.%y")} до {getEndDateDraw(CURRENTDRAW)}</b>\n\n"
            f"<b>Победители в розыгрыше:</b>\n {winners}\n\n"
            f"<b>Участники розыгрыша:</b>\n {participates}\n<b>Количество участников:</b> {lenParticipates}\n\n"
            f"<b>Спонсоры розыгрыша:</b>\n {getTelegramChannelNames}", 
            parse_mode="html"
        )
    except Exception as e:
        mainPanelAdmin(call.message)

def getDrawURL(call):
    try:
        bot.send_message(
            call.message.chat.id, 
            f"<b>Вот url для розыгрыша {CURRENTDRAW}:</b>  {getDrawURLFromDb(CURRENTDRAW)}", 
            parse_mode="html"
        )
    except Exception as e:
        mainPanelAdmin(call.message)

def deleteDraws(call):
    try:
        curDraw = CURRENTDRAW
    except Exception as e:
        curDraw = False
        mainPanelAdmin(call.message)
    
    def permissionToDelete(call):
        bot.send_message(call.message.chat.id, f"Что бы удалить розыгрыш напишите: 'удалить' ")
        bot.register_next_step_handler(call.message, delete)

    def delete(message):
        permission = message.text

        if permission.lower() == "удалить":
            try:
                deleteDraw(CURRENTDRAW)
                bot.send_message(message.chat.id, f"Розыгрыш был удалён")
            except Exception as e:
                bot.send_message(message.chat.id, f"Не удалось получить информацию: {str(e)}")
        else:
            bot.send_message(message.chat.id, f"Удаление не потвердилось")

    if curDraw:
        permissionToDelete(call)

def determineWinners(call):
    try:
        curDraw = CURRENTDRAW
    except Exception as e:
        curDraw = False
        mainPanelAdmin(call.message)

    def getUsernameWinner(call):
        bot.send_message(call.message.chat.id, "Введите никнейм пользователя, который выграл: ")
        bot.register_next_step_handler(call.message, getWinnerAndAddWinner)
    
    def getWinnerAndAddWinner(message):
        usernameWinner = message.text
        try:
            bot.send_message(call.message.chat.id, f"{addWinner(CURRENTDRAW, usernameWinner)}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось получить информацию: {str(e)}")
    if curDraw:
        getUsernameWinner(call)

def deleteWinners(call):
    try:
        curDraw = CURRENTDRAW
    except Exception as e:
        curDraw = False
        mainPanelAdmin(call.message)
        
    def getUsernameWinner(call):
        bot.send_message(call.message.chat.id, "Введите никнейм пользователя, которого удаляем: ")
        bot.register_next_step_handler(call.message, getWinnerAndDeleteWinner)

    def getWinnerAndDeleteWinner(message):
        usernameWinner = message.text
        try:
            bot.send_message(call.message.chat.id, f"{deleteWinner(CURRENTDRAW, usernameWinner)}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось получить информацию: {str(e)}")

    if curDraw:
        getUsernameWinner(call)

def addSponsor(call):
    try:
        curDraw = CURRENTDRAW
    except Exception as e:
        curDraw = False
        mainPanelAdmin(call.message)

    def getTelegramChannelNames(call):
        bot.send_message(call.message.chat.id, "Введите название канала:")
        bot.register_next_step_handler(call.message, getTelegramChannelNamesAdd)
    
    def getTelegramChannelNamesAdd(message):
        telegramChannelName = message.text
        try:
            bot.send_message(call.message.chat.id, f"{addTelegramChannelName(CURRENTDRAW, telegramChannelName)}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось получить информацию: {str(e)}")
    if curDraw:
        getTelegramChannelNames(call)

def deleteSponsor(call):
    try:
        curDraw = CURRENTDRAW
    except Exception as e:
        curDraw = False
        mainPanelAdmin(call.message)
        
    def getTelegramChannelNames(call):
        bot.send_message(call.message.chat.id, "Введите название канала: ")
        bot.register_next_step_handler(call.message, getTelegramChannelNamesAndDelete)

    def getTelegramChannelNamesAndDelete(message):
        telegramChannelName = message.text
        try:
            bot.send_message(call.message.chat.id, f"{deleteTelegramChannelName(CURRENTDRAW, telegramChannelName)}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Не удалось получить информацию: {str(e)}")

    if curDraw:
        getTelegramChannelNames(call)
    

def panelForStatistics(message):
    allUsersBot = types.InlineKeyboardButton("Все пользователи", callback_data="allUsersBot")
    allAdmins = types.InlineKeyboardButton("Все администраторы", callback_data="allAdmins")
    allDraws = types.InlineKeyboardButton("Все розыгрыши", callback_data="allDraws")
    
    statisticsPanelMarkup = types.InlineKeyboardMarkup()
    statisticsPanelMarkup.row(allAdmins)
    statisticsPanelMarkup.row(allDraws, allUsersBot)

    bot.send_message(message.chat.id, "Панель со статистикой Бота:", reply_markup=statisticsPanelMarkup)


def allUsersBot(message):
    users = getAllUsers()
    bot.send_message(message.chat.id,
                     f"<b>Все пользователи:</b>\n {'\n '.join(f"@{user}" for user in users)} \n\n <b>Количество пользователей:{len(users)}</b>",
                     parse_mode="html")
    panelForStatistics(message)

def allAdmins(message):
    allAdmins = getAllAdmins()
    bot.send_message(message.chat.id,
                     f"<b>Все администраторы:</b>\n {'\n '.join(f"@{admin}" for admin in allAdmins)} \n\n <b>Количество администраторов:{len(allAdmins)}</b>",
                     parse_mode="html")

def allDraws(message):
    allDraws = getAllDraws()
    bot.send_message(message.chat.id,
                     f"<b>Все розыгрыши:</b>\n {'\n '.join(allDraws)} \n\n <b>Количество розыгрышей:{len(allDraws)}</b>",
                     parse_mode="html")
    panelForStatistics(message)



def panelForNewDraw(message):
    dataForNewDraw = {
        "nameDraw": message.text,
        "endDate": "",
        "information": "",
        "author": message.from_user.first_name,
        "drawURL": "https://t.me/luckyForDrawBot?start=" + message.text
    }

    def getEndDate(message):
        bot.send_message(message.chat.id, "Напишите окончание розыгрыша: ")
        bot.register_next_step_handler(message, getInformation)
    
    def getInformation(message):
        bot.send_message(message.chat.id, "Напишите информацию о розыгрыше(возможно использовать до 250 символов): ")
        dataForNewDraw["endDate"] = message.text
        bot.register_next_step_handler(message, createNewDraw)
    
    def createNewDraw(message):
        dataForNewDraw["information"] = message.text
        createDraw(dataForNewDraw["nameDraw"], dataForNewDraw["endDate"], dataForNewDraw["information"], dataForNewDraw["author"], dataForNewDraw["drawURL"])
        mainPanelAdmin(message)
    getEndDate(message)

def panelForAdmins(message):
    allAdmins = types.InlineKeyboardButton("Все администраторы", callback_data="allAdmins")
    deleteAdmins = types.InlineKeyboardButton("Удалить администратора", callback_data="deleteAdmins")
    addAdmins = types.InlineKeyboardButton("Добавить администратора", callback_data="addAdmins")

    newPanelAdminsMarkup = types.InlineKeyboardMarkup()

    newPanelAdminsMarkup.row(deleteAdmins)
    newPanelAdminsMarkup.row(addAdmins)
    newPanelAdminsMarkup.row(allAdmins)

    bot.send_message(message.chat.id, "Панель для управления администраторами:", reply_markup=newPanelAdminsMarkup)

def deleteAdmins(message):
    uswernameAdmin = message.text
    answer = deleteAdmin(uswernameAdmin)
    bot.send_message(message.chat.id, f"{answer}")
    panelForAdmins(message)

def addAdmins(message):
    uswernameAdmin = message.text
    answer = addAdmin(uswernameAdmin)
    bot.send_message(message.chat.id, f"{answer}")
    panelForAdmins(message)

def panelForNewsletter(message):
    global DATAFORNEWLETTER
    DATAFORNEWLETTER = {}

    bot.send_message(message.chat.id, "Введите название поста:")
    bot.register_next_step_handler(message, getTitle)

def getTitle(message):
    DATAFORNEWLETTER['title'] = message.text
    bot.send_message(message.chat.id, "Теперь отправьте фото для поста:")
    bot.register_next_step_handler(message, getPhoto)

def getPhoto(message):
    if message.photo:
        DATAFORNEWLETTER['photo'] = message.photo[-1].file_id
        bot.send_message(message.chat.id, "Отлично! Теперь отправьте текст для поста:")
        bot.register_next_step_handler(message, getInfo)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фото")

def getInfo(message):
    chatsID = getAllChatID()

    DATAFORNEWLETTER['info'] = message.text

    for chatID in chatsID:
        bot.send_photo(chatID, photo=DATAFORNEWLETTER['photo'], caption=f"{DATAFORNEWLETTER['title']}\n\n\n{DATAFORNEWLETTER['info']}")

    bot.send_message(message.chat.id, "Рекламное сообщение отправлено всем пользователям!")
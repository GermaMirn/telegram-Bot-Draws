from getBotInstance import bot
from telebot import types
import panels.user as user
import panels.admin as admin
from db.dbRequests import getAllAdmins
from db.dbRequests import createForHostMainTables, getAllDraws, addNewUser, gettelegramChannelNames

keybordMessageId = None

def getAllAdmin():
    allAdmins = getAllAdmins()
    global ADMIN
    ADMIN = allAdmins
    if len(allAdmins) == 0:
        ADMIN = [
            "obladaetyou",
            "nerdOfi"
        ]


def isAdmin(username):
    return username in ADMIN

userData = {}

@bot.message_handler(commands=["start"])
def start(message):
    addNewUser(message.from_user.username, message.chat.id)
    username = message.from_user.username
    if isAdmin(username):
        admin.welcomeAdmin(message)
    else:
        params = message.text.split()

        if len(params) > 1:
            drawName = params[1]
            userData[message.chat.id] = {'drawName': drawName}

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = types.KeyboardButton("Я не робот")
            keyboard.add(button)

            bot.send_message(message.chat.id, "Привет! Пожалуйста, нажмите кнопку ниже для проверки.", reply_markup=keyboard)
        else:
            user.welcomeUser(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("draw_"))
def handleDrawSelection(call):
    drawName = call.data.split("_")[1]
    userData[call.message.chat.id] = {'drawName': drawName}
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Я не робот")
    keyboard.add(button)
    bot.send_message(call.message.chat.id, "Привет! Пожалуйста, нажмите кнопку ниже для проверки.", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Я не робот")
def checkSubscription(message):
    chatId = message.chat.id
    userId = message.from_user.id
    allDraws = getAllDraws()

    drawName = userData.get(chatId, {}).get('drawName')
    if not drawName:
        bot.send_message(chatId, "Не удалось получить информацию о розыгрыше.")
        return

    channelId = gettelegramChannelNames(drawName)
    refactoryChannelId = ", ".join(f"@{channel}" for channel in channelId)
    hideKeyboard = types.ReplyKeyboardRemove()

    try:
        status = bot.get_chat_member(refactoryChannelId, userId).status

        if status in ['member', 'administrator', 'creator']:
            if drawName in allDraws:
                bot.send_message(message.chat.id, "Вы успешно прошли проверку!", reply_markup=hideKeyboard)
                user.urlDrawMenu(message, drawName)
            else:
                bot.send_message(message.chat.id, "К сожалению, этот розыгрышь уже закончился. Однако у нас есть ещё и другие розыгрыши", reply_markup=hideKeyboard)
                user.welcomeUser(message)
        else:
            bot.send_message(chatId, f"Вы не подписаны на нашего спонсора. Пожалуйста, подпишитесь: {refactoryChannelId}")
    except Exception as e:
        bot.send_message(message.chat.id, "К сожалению, этот розыгрышь уже закончился. Однако у нас есть ещё и другие розыгрыши", reply_markup=hideKeyboard)
        user.welcomeUser(message)
        print(e)


@bot.message_handler(commands=["help"])
def helpMenu(message):
    username = message.from_user.username
    if isAdmin(username):
        bot.send_message(
        message.chat.id,
        f"<b>/help</b> - открывает информацию о быстрых командах\n<b>/panel</b> - открывает главную панель\n<b>/panelForDraw</b> - открывает панель определённого розыгрыша\n<b>/panelForStatistics</b> - открывает панель со статистикой Бота\n<b>/panelForNewDraw</b> - открывает панель для нового розыгрыша",
        parse_mode="html"
    )
    else:
        bot.send_message(
        message.chat.id,
        f"<b>/help</b> - открывает информацию о быстрых командах\n<b>/panel</b> - открывает главную панель",
        parse_mode="html"
    )

@bot.message_handler(commands=["panelForDraw"])
def panelForDraw(message):
    username = message.from_user.username
    if isAdmin(username):
        admin.panelForDraw(message)


@bot.message_handler(commands=["panelForStatistics"])
def panelForStatistics(message):
    username = message.from_user.username
    if isAdmin(username):
        admin.panelForStatistics(message)


@bot.message_handler(commands=["panelForNewDraw"])
def panelForNewDraw(message):
    username = message.from_user.username
    if isAdmin(username):
        admin.panelForNewDraw(message)


@bot.message_handler(commands=["panel"])
def mainPanel(message):
    global keybordMessageId
    username = message.from_user.username
    if isAdmin(username):
        admin.mainPanelAdmin(message)
    else:
        try:
            for i in range(0, 10):
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i)
        except:
            pass
        if keybordMessageId:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=keybordMessageId)
            except:
                pass
        keybordMessageId = user.showDrawMenu(message)

CALLBACK_FUNCTIONS_ADMIN = {
    "panelForDraw": lambda call: (
        bot.send_message(call.message.chat.id, "Напишите название розыгрыша: "),
        bot.register_next_step_handler(call.message, admin.panelForDraw)
    ),
    "panelForStatistics": admin.panelForStatistics,
    "panelForNewDraw": lambda call: (
        bot.send_message(call.message.chat.id, "Напишите название нового розыгрыша: "),
        bot.register_next_step_handler(call.message, admin.panelForNewDraw)
    ),
    "panelForAdmins": admin.panelForAdmins,
    "infoDraw": lambda call: admin.InfoDraw(call),
    "allUsersBot": admin.allUsersBot,
    "allDraws": admin.allDraws,
    "allAdmins": admin.allAdmins,
    "deleteDraw": admin.deleteDraws,
    "getDrawURL": admin.getDrawURL,
    "determineWinners": lambda call: admin.determineWinners(call),
    "deleteWinners": lambda call: admin.deleteWinners(call),
    "addSponsor": lambda call: admin.addSponsor(call),
    "deleteSponsor": lambda call: admin.deleteSponsor(call),
    "deleteAdmins": lambda call: (
        bot.send_message(call.message.chat.id, "Напишите имя администратора: "),
        bot.register_next_step_handler(call.message, admin.deleteAdmins)
    ),
    "addAdmins": lambda call: (
        bot.send_message(call.message.chat.id, "Напишите имя администратора: "),
        bot.register_next_step_handler(call.message, admin.addAdmins)
    ),
    "panelForNewsletter": admin.panelForNewsletter,
}

CALLBACK_FUNCTIONS_USER = {
    "allDraw": lambda call: (
        bot.send_message(call.message.chat.id, "Вот все доступные розыгрыши:"),
        user.listOfDraws(call.message),
        # bot.register_next_step_handler(call.message, user.handleDrawName)
    ),
    "writeDraw": lambda call: (
        bot.send_message(call.message.chat.id, "Чтобы продолжить, введите название розыгрыша: "),
        bot.register_next_step_handler(call.message, user.handleDrawName)),
    "infoDrawUser": lambda call: user.InfoDrawUser(call),
    "participate": lambda call: user.participate(call),
}

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data in CALLBACK_FUNCTIONS_USER:
        CALLBACK_FUNCTIONS_USER[call.data](call)
    try:
        if call.data in CALLBACK_FUNCTIONS_ADMIN:
            CALLBACK_FUNCTIONS_ADMIN[call.data](call)
    except:
        if call.data in CALLBACK_FUNCTIONS_ADMIN:
            CALLBACK_FUNCTIONS_ADMIN[call.data](call.message)


if __name__ == '__main__':
    createForHostMainTables()
    getAllAdmin()
    bot.polling(none_stop=True)
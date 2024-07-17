from getBotInstance import bot
import panels.user as user
import panels.admin as admin
from db.dbRequests import getAllAdmins
from db.dbRequests import createForHostMainTables, getAllDraws, addNewUser

keybordMessageId = None

def getAllAdmin():
    allAdmins = getAllAdmins()
    global ADMIN
    ADMIN = allAdmins


def isAdmin(username):
    return username in ADMIN

@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.username
    if isAdmin(username):
        admin.welcomeAdmin(message)
    else:
        params = message.text.split()
        if len(params) > 1:
            param = params[1]
            allDraws = getAllDraws()
            if param in allDraws:
                addNewUser(message.from_user.username, message.chat.id)
                user.urlDrawMenu(message, param)
            else:
                bot.send_message(message.chat.id, "К сожалению, этот розыгрышь уже закончился. Однако у нас есть ещё и другие розыгрыши")
                user.welcomeUser(message)
        else:
            user.welcomeUser(message)

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
        bot.register_next_step_handler(call.message, user.handleDrawName)
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
from db.connectionPool import getConnection, releaseConnection
from db.config import host, dbUser, password, dbName

def createForHostMainTables():
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute(
        """
          CREATE TABLE IF NOT EXISTS admins(
            id SERIAL PRIMARY KEY,
            admin VARCHAR(100) NOT NULL
          );
        """)
      connection.commit()

      cursor.execute(
        """
          CREATE TABLE IF NOT EXISTS usernames(
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            chatID INTEGER NOT NULL
          );
        """)
      connection.commit()

      cursor.execute(
        """
          CREATE TABLE IF NOT EXISTS draws(
            id SERIAL PRIMARY KEY,
            draw VARCHAR(100) NOT NULL
          );
        """)
      connection.commit()

      cursor.execute(
        """
          CREATE TABLE IF NOT EXISTS drawDetails(
            id SERIAL PRIMARY KEY,
            drawId INTEGER NOT NULL REFERENCES draws(id) ON DELETE CASCADE,
            author VARCHAR(100),
            creationDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            endDate VARCHAR(20),
            information VARCHAR(250),
            winners TEXT[],
            participants TEXT[],
            drawURL VARCHAR(120)
          );
        """)
      connection.commit()

  except Exception as e:
    return f"Ошибка: {e}"
  finally:
    releaseConnection(connection)

def getParticipants(drawName):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      query = """
          SELECT participants
          FROM drawDetails
          JOIN draws ON drawDetails.drawId = draws.id
          WHERE draws.draw = %s
      """
      cursor.execute(query, (drawName,))
      result = cursor.fetchone()
      if result and result[0]:
        return result[0]
      else:
        return "Участников ещё нет"
  except Exception as e:
    return f"Не получилось получить информацию о участников: {e}"
  finally:
    releaseConnection(connection)

def getWinnersDraw(nameDraw):
  connection = getConnection()

  try:
    with connection.cursor() as cursor:
      query = """
          SELECT winners
          FROM drawDetails
          JOIN draws ON drawDetails.drawId = draws.id
          WHERE draws.draw = %s
      """
      cursor.execute(query, (nameDraw,))
      result = cursor.fetchone()
      if result and result[0]:
        return result[0]
      else:
        return "победители ещё не определенны"
  except Exception as e:
    return f"Не получилось получить информацию о победителях: {e}"
  finally:
    releaseConnection(connection)

def getAuthorDraw(nameDraw):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      query = """
        SELECT author 
        FROM drawDetails 
        JOIN draws ON drawDetails.drawId = draws.id 
        WHERE draws.draw = %s
      """
      cursor.execute(query, (nameDraw,))
      result = cursor.fetchone()
      if result:
        return result[0]
      else:
        return "Не получилось получить информацию об авторе"
  except Exception as e:
    return f"Не получилось получить информацию об авторе {e}"
  finally:
    releaseConnection(connection)

def getInformationDraw(nameDraw):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      query = """
        SELECT information 
        FROM drawDetails 
        JOIN draws ON drawDetails.drawId = draws.id 
        WHERE draws.draw = %s
      """
      cursor.execute(query, (nameDraw,))
      result = cursor.fetchone()
      if result:
        return result[0]
      else:
        return "Не получилось получить информацию о розыгрыше"
  except Exception as e:
    return f"Не получилось получить информацию о розыгрыше {e}"
  finally:
    releaseConnection(connection)

def getStartDateDraw(nameDraw):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      query = """
        SELECT creationDate 
        FROM drawDetails 
        JOIN draws ON drawDetails.drawId = draws.id 
        WHERE draws.draw = %s
      """
      cursor.execute(query, (nameDraw,))
      result = cursor.fetchone()
      if result:
        return result[0]
      else:
        return "Не получилось получить дату начало розыгрыша"
  except Exception as e:
    return f"Не получилось получить дату начало розыгрыша {e}"
  finally:
    releaseConnection(connection)

def getEndDateDraw(nameDraw):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      query = """
        SELECT endDate 
        FROM drawDetails 
        JOIN draws ON drawDetails.drawId = draws.id 
        WHERE draws.draw = %s
      """
      cursor.execute(query, (nameDraw,))
      result = cursor.fetchone()
      if result:
        return result[0]
      else:
        return "Не получилось получить дату окончания розыгрыша"
  except Exception as e:
    return f"Не получилось получить дату окончания розыгрыша {e}"
  finally:
    releaseConnection(connection)

def createDraw(nameDraw, endDate, information, author, drawURL):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""
          INSERT INTO draws (draw) VALUES (%s) RETURNING id;
      """, (nameDraw,))
      draw_id = cursor.fetchone()[0]

      cursor.execute("""
          INSERT INTO drawDetails (drawId, endDate, information, author, drawURL) 
          VALUES (%s, %s, %s, %s, %s);
      """, (draw_id, endDate, information, author, drawURL))
      connection.commit()

      return "Новый розыгрыш был создан"
  except Exception as e:
    return f"Новый розыгрыш не получилось создать.Ошибка: {e}"
  finally:
    releaseConnection(connection)

def deleteDraw(nameDraw):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""
          DELETE FROM draws WHERE draw = %s;
      """, (nameDraw,))
      connection.commit()
      return "Розыгрыш был удалён"
  except Exception as e:
    print(f"Ошибка: {e}")
    return "Розыгрыш не получилось удалить"
  finally:
    releaseConnection(connection)

def checkDraw(nameDraw, schema='public'):
  connection = getConnection()
  allDraws = getAllDraws()
  try:
    return nameDraw in allDraws

  except Exception as e:
    print(f"Ошибка: {e}")
    return "Не получилось обратиться к бд"
  finally:
    releaseConnection(connection)

def getAllDraws():
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""
          SELECT draw FROM draws;
      """)
      allDraws = cursor.fetchall()
      processedData = [row[0] for row in allDraws]
      return processedData
  except Exception as e:
    print(f"Ошибка: {e}")
    return []
  finally:
    releaseConnection(connection)

def addWinner(drawName, winner):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""SELECT id FROM draws WHERE draw = %s;""", (drawName,))
      draw_id = cursor.fetchone()
      
      if not draw_id:
          return "Розыгрыш не найден"

      draw_id = draw_id[0]

      cursor.execute(
      """
          UPDATE drawDetails
          SET winners = array_append(winners, %s)
          WHERE drawId = %s;
      """, (winner, draw_id))
      connection.commit()
      return "Победитель был добавлен"
  except Exception as e:
    return f"Ошибка: {e}"
  finally:
    releaseConnection(connection)

def getDrawURLFromDb(drawName):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute(
      """
      SELECT drawDetails.drawURL
      FROM draws
      JOIN drawDetails ON draws.id = drawDetails.drawId
      WHERE draws.draw = %s;
      """, (drawName,)
      )
      
      drawURLExists = cursor.fetchone()

      if drawURLExists == False:
        return f"Не получилось получить url {drawName} розыгрыша"

      return drawURLExists[0]
  except Exception as e:
    return f"Ошибка: {e}"
  finally:
    releaseConnection(connection)

def addParticipants(drawName, participants):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""SELECT id FROM draws WHERE draw = %s;""", (drawName,))
      draw_id = cursor.fetchone()
      
      if not draw_id:
          return "Розыгрыш не найден"
      
      draw_id = draw_id[0]

      cursor.execute("""
        SELECT EXISTS(
            SELECT 1 
            FROM drawDetails 
            WHERE drawId = %s AND %s = ANY(participants)
          );
      """, (draw_id, participants))
      participant_exists = cursor.fetchone()[0]

      if participant_exists:
          return "Вы уже являетесь участником"

      cursor.execute(
      """
        UPDATE drawDetails
        SET participants = array_append(participants, %s)
        WHERE drawId = %s;
      """, (participants, draw_id))
      connection.commit()
      return "Участник был добавлен"
  except Exception as e:
    return f"Ошибка: {e}"
  finally:
    releaseConnection(connection)

def addAdmin(username):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("SELECT COUNT(*) FROM admins WHERE admin = %s;", (username,))
      adminExists = cursor.fetchone()[0]
      
      if adminExists:
          return "Админ уже существует"
      
      cursor.execute("INSERT INTO admins (admin) VALUES (%s);", (username,))
      connection.commit()
      return "Новый админ был добавлен"
    
  except Exception as e:
    print(f"Ошибка: {e}")
    return "Нового администратора не получилось добавить"
  finally:
    releaseConnection(connection)

def deleteAdmin(username):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("SELECT COUNT(*) FROM admins WHERE admin = %s;", (username,))
      adminExists = cursor.fetchone()[0]

      if adminExists == False:
          return "Данный администратор не существует"

      cursor.execute("""
          DELETE FROM admins WHERE admin = %s;
      """, (username,))
      connection.commit()
      return "Администратор был удалён"
  except Exception as e:
    print(f"Ошибка: {e}")
    return "Не получилось удалить администратора"
  finally:
    releaseConnection(connection)

def getAllAdmins():
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT admin FROM admins;
        """)
        allAdmins = cursor.fetchall()
        processedData = [row[0] for row in allAdmins]
        return processedData
  except Exception as e:
    print(f"Ошибка: {e}")
    return []
  finally:
    releaseConnection(connection)

def addNewUser(username, chatID):
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("SELECT COUNT(*) FROM usernames WHERE username = %s;", (username,))
      user_exists = cursor.fetchone()[0]
      
      if user_exists:
          return "Пользователь уже существует"
      
      cursor.execute("INSERT INTO usernames (username, chatID) VALUES (%s, %s);", (username, chatID))
      connection.commit()
      return "Новый пользователь был добавлен"
  except Exception as e:
    print(f"Ошибка: {e}")
    return "Нового пользователя не получилось добавить"
  finally:
    releaseConnection(connection)

def getAllUsers():
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""
          SELECT username FROM usernames;
      """)
      allAUsers = cursor.fetchall()
      processedData = [row[0] for row in allAUsers]
      return processedData
  except Exception as e:
    print(f"Ошибка: {e}")
    return []
  finally:
    releaseConnection(connection)

def getAllChatID():
  connection = getConnection()
  try:
    with connection.cursor() as cursor:
      cursor.execute("""
          SELECT chatID FROM usernames;
      """)
      allAUsers = cursor.fetchall()
      processedData = [row[0] for row in allAUsers]
      return processedData
  except Exception as e:
    print(f"Ошибка: {e}")
    return []
  finally:
    releaseConnection(connection)

# def deleteStatistics():
#   connection = getConnection()
#   try:
#     with connection.cursor() as cursor:     
#       cursor.execute("DELETE FROM usernames")
#       connection.commit()
#       print("ok")
#       return "Все пользователи были удалены"
#   except Exception as e:
#     print(f"Ошибка: {e}")
#     return "Не получилось удалить пользователей"
#   finally:
#     releaseConnection(connection)
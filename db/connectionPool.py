from psycopg2 import pool
from db.config import host, dbUser, password, dbName

connectionPool = pool.SimpleConnectionPool(
    1,
    20,
    host=host,
    user=dbUser,
    password=password,
    database=dbName
)

def getConnection():
    return connectionPool.getconn()

def releaseConnection(connection):
    connectionPool.putconn(connection)
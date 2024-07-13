import pymysql
from config import MySQL_config


def get_connection():
    connection = pymysql.connect(
        host=MySQL_config.HOST,
        port=MySQL_config.PORT,
        user=MySQL_config.USER,
        password=MySQL_config.PASSWORD,
        database=MySQL_config.DATABASE,
        charset='utf8mb4',
    )
    return connection
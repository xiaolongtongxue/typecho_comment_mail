# -*- coding: UTF-8 -*-
from mysql import connector
from mysql.connector import Error

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_DATABASE = "{MySQL的typecho数据库}"
MYSQL_USER = "{MySQL的用户名}"
MYSQL_PASSWD = "{MySQL的实际密码}"
MYSQL_TABLE_FIRST = "typecho_"

if __name__ == '__main__':
    connection = connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWD,
        database=MYSQL_DATABASE
    )
    cursor = connection.cursor(prepared=True)
    try:
        sql_set_a = "ALTER TABLE `" + MYSQL_TABLE_FIRST + \
                    "comments` ADD COLUMN `ismailsend` tinyint NOT NULL DEFAULT 0;"
        sql_set_b = "UPDATE `" + MYSQL_TABLE_FIRST + "comments` SET `ismailsend`=1;"
        cursor.execute(sql_set_a, ())
        cursor.execute(sql_set_b, ())
        connection.commit()
    except Error as error:
        print("error")
        print(error)
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

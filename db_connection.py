import pymysql.cursors
from loguru import logger
import datetime


# develop db connection
def create_connection():
    connection = pymysql.connect(host='localhost',
                                 user='Kelvin',
                                 password='Kelvin159368247@',
                                 database='Cyberbroad',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


# connect to Account_creator table
# return resultall dict
def get_total_info():
    connection = create_connection()

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT `Id`,`Name`, `ixigua`, `bilibili`, `oper_name`, `Last_update` FROM `Account_creator`"
            cursor.execute(sql)
            resultall = cursor.fetchall()

    return resultall

# get last video info
# param table_name string
# return result dict
def get_creator_info(table_name):
    connection = create_connection()

    with connection:
        with connection.cursor() as cursor:
            sql = f"SELECT `Id`,`Name`, `Link`, `Last_update` FROM `{table_name}` ORDER BY id DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()

    return result

# insert new video info
# param value tuple table_name string
def insert_new_video(value, table_name):
    connection = create_connection()

    with connection:
        with connection.cursor() as cursor:
            sql = f"INSERT INTO {table_name} (Name, Link, Last_update) VALUES (%s, %s, %s)"
            
            cursor.execute(sql, value)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()



#  update time info in Account_creator
def update_time(Name, Time):
    connection = create_connection()
    with connection:
        with connection.cursor() as cursor:
            sql = f"UPDATE Account_creator SET Last_update = '{Time}' WHERE Name = '{Name}' "
            cursor.execute(sql)
            connection.commit()

# insert error channel info ixigua
# param value tuple table_name string
def insert_error_channel_ixigua(value):
    connection = create_connection()

    with connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Error_record (Name, ixigua, oper_name, Time, Error_msg) VALUES (%s, %s, %s, %s, %s)"
            
            cursor.execute(sql, value)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()


# insert error channel info bilibili
# param value tuple table_name string
def insert_error_channel_bilibili(value):
    connection = create_connection()

    with connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO Error_record (Name, bilibili, oper_name, Time, Error_msg) VALUES (%s, %s, %s, %s, %s)"
            
            cursor.execute(sql, value)
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
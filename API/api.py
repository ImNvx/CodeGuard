import mysql.connector
import json

CONFIG_PATH = 'config.json'


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())


if __name__ == "__main__":

    db_login = read_json(CONFIG_PATH)

    mydb = mysql.connector.connect(
        host = db_login['mysql-host'],
        user = db_login['mysql-user'],
        password = db_login['mysql-pass'],
        database = db_login['mysql-database']
    )

    mycursor = mydb.cursor()

    mycursor.execute("SHOW TABLES")

    for x in mycursor:
        print(x) 
import json
import mysql.connector
from datetime import datetime

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

class CodeGuard_Database:
    def __init__(self, TABLE, ACCEPTED, CONFIG_PATH):
        self.TABLE = TABLE
        self.ACCEPTED = ACCEPTED
        self.CONFIG_PATH = CONFIG_PATH

    def connect_mysql(self):
        db_login = read_json(self.CONFIG_PATH)

        mydb = mysql.connector.connect(
            host = db_login['mysql-host'],
            user = db_login['mysql-user'],
            password = db_login['mysql-pass'],
            database = db_login['mysql-database']
        )

        return mydb

    def add_solution(self, solution_id, user_id, problem_id, score, timestamp, weird_percent, text): #timestamp trb UNIX
        try:#           int     , string , string    ,string, string   , float / None, string
            sql_timestamp = datetime.fromtimestamp(int(timestamp) / 1000) #transformam timpu in sql
            sql = "INSERT INTO " + self.TABLE + " (solution_id, user_id, problem_id, score, timestamp, weird_percent, text) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (solution_id, user_id, problem_id, score, sql_timestamp, weird_percent, text)

            mydb = self.connect_mysql()
            mycursor = mydb.cursor()

            mycursor.execute(sql, val)
            mydb.commit()

            mydb.close()
            return True
        except Exception as e:
            print(e)
            return False

    def get_code(self, solution_id): #solution_id -> text
        try:
            sql = "SELECT text FROM " + self.TABLE +" WHERE solution_id = %s" #luam dupa id
            val = (solution_id,)

            mydb = self.connect_mysql()
            mycursor = mydb.cursor()

            mycursor.execute(sql, val)

            myresult = mycursor.fetchall()

            mydb.close()

            return myresult[0][0]
        except Exception as e:
            print(e)
            return None

    def get_weird_percent(self, solution_id):#solution_id -> weird_percent
        try:
            sql = "SELECT weird_percent FROM " + self.TABLE +" WHERE solution_id = %s" #luam dupa id
            val = (solution_id,)

            mydb = self.connect_mysql()
            mycursor = mydb.cursor()

            mycursor.execute(sql, val)

            myresult = mycursor.fetchall()

            mydb.close()

            return myresult[0][0]
        except Exception as e:
            return None

    def update_weird_percent(self, solution_id, weird_percent):
        try:
            sql = 'UPDATE ' + self.TABLE + ' SET weird_percent = %s WHERE solution_id = %s'
            val = (weird_percent, solution_id)

            mydb = self.connect_mysql()
            mycursor = mydb.cursor()

            mycursor.execute(sql, val)
            mydb.commit()

            mydb.close()
            return weird_percent
        except Exception as e:
            return None

    def get_latest(self, user, problem_id, score = None):
        try:# ultima solutie cu scorul score de la useru user la problema problem_id
            if score == None:
                score = self.ACCEPTED

            sql = "SELECT solution_id FROM " + self.TABLE + " WHERE user_id = %s AND problem_id = %s AND score = %s ORDER BY timestamp DESC LIMIT 1"
            val = (user, problem_id, score)

            mydb = self.connect_mysql()
            mycursor = mydb.cursor()

            mycursor.execute(sql, val)

            myresult = mycursor.fetchall()

            mydb.close()

            return myresult[0][0]
        except Exception as e:
            #print(e)
            return None
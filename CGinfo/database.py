'''
Documentatie:
functii: 
    -initialize_database():
        -verifica daca exista baza de date si daca nu, o creeeaza
        -nu returneaza nimic

    -add_submission(
        kn_submission_id,   #int
        time_stamp,         #int , timp UNIX
        source_code,        #string
        problem_id,         #int
        score,              #int
        user_id,            #int
        contest_id,         #int
        weird_percent,      #float
        db_path=DB_NAME
    ):
        -adauga o submisie in baza de date
        -weird_percent trebuie calculat inainte ca functia sa fie apelata
        -nu returneaza nimic

    -add_contest(
        name,           #string
        start_time,     #int
        end_time,       #int
        nume_clasa,     #string
        nivel_clasa,    #int
        lista_probleme, #lista in python
        fetched=False,  #bool, nu conteaza:-)
        db_path=DB_NAME
    ):
        -adauga un concurs la baza de date
        -returneaza idul concursului

    -get_submissions_for_elev(elev : Elev, count: int = -1):
        -daca count != -1 returneaza o lista cu #count# cele mai noi submisii elevului
        -daca count == -1 returneaza toate submisiile elevului
        -lista este asa: [(type Submisie), (type Submisie), ...]
    
    -get_batch_for_jaccard(elev : Elev, problem_id, count = -1, db_path = DB_NAME):
        -daca count != -1 returneaza o lista cu #count# cele mai noi submisii acceptate la problema problem_id trimise de alt utilizator decat elev
        -daca count == -1 returneaza o lista cu toate submisiile acceptate la problema problem_id trimise de alt utilizator decat elev
        -lista este asa: [(type Submisie), (type Submisie), ...]

    -get_all_contests():
        -returneaza o lista cu toate concursurile
        -lista este asa: [(type Contest), (type Contest), ...]

    -update_contest_fetched(contest_id: int, value: bool, db_path=DB_NAME):
        -modifica fetched pentru contestul care idul egal cu contest_id
        -nu returneaza nimic

    -get_unfetched_finished_contests(current_time_unix: int, db_path=DB_NAME):
        -gaseste si returneaza contesturile la care inca nu le am dat fetch si care s au terminat(end_time <= curent_time_unix)
        -returneaza o lista asa : [(type Contest), (type Contest), ...]
'''

import sqlite3
import os
from CGinfo.CGinfo_ds import Elev, Contest, Submisie
import json



DB_NAME = "Userdata/CGinfo.db"


def initialize_database(db_path=DB_NAME):

    db_exists = os.path.exists(db_path)

    if db_exists == False:
        print("Creem baza de date")
    else:
        print("Baza de date exista deja")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursuri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            start_time INTEGER,
            end_time INTEGER,
            nume_clasa TEXT,
            nivel_clasa INTEGER,
            lista_probleme TEXT,
            fetched BOOLEAN
        )
    """)

    cursor.execute("""
        CREATE TABLE submissi (
            kn_submision_id INTEGER PRIMARY KEY,
            time_stamp INTEGER,
            source_code TEXT,
            problem_id INTEGER,
            score INTEGER,
            user_id INTEGER,
            contest_id INTEGER,
            weird_percent REAL,
            similarity_percent REAL,
            FOREIGN KEY (contest_id) REFERENCES concursuri(id)
        );
    """)

    conn.commit()
    conn.close()

    print("Baza de date a fost creata impreuna cu tabelele")

def add_submission(
    kn_submission_id,
    time_stamp,
    source_code,
    problem_id,
    score,
    user_id,
    contest_id,
    weird_percent,
    similarity_percent,
    db_path=DB_NAME
):
    print(os.path.abspath(DB_NAME))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO submissi (
            kn_submision_id,
            time_stamp,
            source_code,
            problem_id,
            score,
            user_id,
            contest_id,
            weird_percent,
            similarity_percent
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kn_submission_id,
        time_stamp,
        source_code,
        problem_id,
        score,
        user_id,
        contest_id,
        weird_percent,
        similarity_percent
    ))

    conn.commit()
    conn.close()


def add_contest( # creaza un conccurs si returneaza idul sau
    name,
    start_time,
    end_time,
    nume_clasa,
    nivel_clasa,
    lista_probleme, #lista in python
    fetched=False,
    db_path=DB_NAME
):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO concursuri (
            name,
            start_time,
            end_time,
            nume_clasa,
            nivel_clasa,
            lista_probleme,
            fetched
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        start_time,
        end_time,
        nume_clasa,
        nivel_clasa,
        json.dumps(lista_probleme),  # convertim lista
        int(fetched)
    ))

    contest_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return contest_id

def get_submissions_for_elev(elev: Elev, count: int = -1):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if count == -1:
        cursor.execute("""
            SELECT
                kn_submision_id,
                time_stamp,
                source_code,
                problem_id,
                score,
                user_id,
                contest_id,
                weird_percent,
                similarity_percent
            FROM submissi
            WHERE user_id = ?
            ORDER BY time_stamp DESC
        """, (elev.id,))
    else:
        cursor.execute("""
            SELECT
                kn_submision_id,
                time_stamp,
                source_code,
                problem_id,
                score,
                user_id,
                contest_id,
                weird_percent,
                similarity_percent
            FROM submissi
            WHERE user_id = ?
            ORDER BY time_stamp DESC
            LIMIT ?
        """, (elev.id, count))

    rows = cursor.fetchall()
    conn.close()

    submissions = []

    for row in rows:
        submissions.append(Submisie(
            id=row[0],
            time_stamp=row[1],
            content=row[2],
            problem_id=row[3],
            score=row[4],
            user_id=row[5],
            contest_id=row[6],
            weird_percent=row[7],
            similarity_percent=row[8]
        ))

    return submissions

def get_all_contests():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            start_time,
            end_time,
            nume_clasa,
            nivel_clasa,
            lista_probleme,
            fetched
        FROM concursuri
    """)

    rows = cursor.fetchall()
    conn.close()

    contests = []

    for row in rows:
        contests.append(Contest(
            id=row[0],
            name=row[1],
            start_time=row[2],
            end_time=row[3],
            nume_clasa=row[4],
            nivel_clasa=row[5],
            lista_probleme=json.loads(row[6]),
            fetched=row[7]
        ))

    return contests

def update_contest_fetched(contest_id: int, value: bool, db_path=DB_NAME):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE concursuri
        SET fetched = ?
        WHERE id = ?
    """, (int(value), contest_id))

    conn.commit()
    conn.close()

def get_unfetched_finished_contests(current_time_unix: int, db_path=DB_NAME):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            start_time,
            end_time,
            nume_clasa,
            nivel_clasa,
            lista_probleme,
            fetched
        FROM concursuri
        WHERE fetched = 0 AND end_time <= ?
    """, (current_time_unix,))

    rows = cursor.fetchall()
    conn.close()

    contests = []

    for row in rows:
        contests.append(Contest(
            id=row[0],
            name=row[1],
            start_time=row[2],
            end_time=row[3],
            nume_clasa=row[4],
            nivel_clasa=row[5],
            lista_probleme=json.loads(row[6]),
            fetched=row[7]
        ))

    return contests

def get_batch_for_jaccard(elev : Elev, problem_id, count = -1, db_path = DB_NAME):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if count == -1:
        cursor.execute("""
            SELECT
                kn_submision_id,
                time_stamp,
                source_code,
                problem_id,
                score,
                user_id,
                contest_id,
                weird_percent,
                similarity_percent
            FROM submissi
            WHERE user_id != ? AND score = 100 AND problem_id = ?
            ORDER BY time_stamp DESC
        """, (elev.id, problem_id))
    else:
        cursor.execute("""
            SELECT
                kn_submision_id,
                time_stamp,
                source_code,
                problem_id,
                score,
                user_id,
                contest_id,
                weird_percent,
                similarity_percent
            FROM submissi
            WHERE user_id != ? AND score = 100 AND problem_id = ?
            ORDER BY time_stamp DESC
            LIMIT ?
        """, (elev.id, problem_id, count))

    rows = cursor.fetchall()
    conn.close()

    submissions = []

    for row in rows:
        submissions.append(Submisie(
            id=row[0],
            time_stamp=row[1],
            content=row[2],
            problem_id=row[3],
            score=row[4],
            user_id=row[5],
            contest_id=row[6],
            weird_percent=row[7],
            similarity_percent=row[8]
        ))

    return submissions

if __name__ == "__main__": #asta ii numa de test
    initialize_database()

    update_contest_fetched(1, False)

    print(get_unfetched_finished_contests(420))

    #exit()
    if(False):
        contest_id = add_contest(
            name="ONI 2026",
            start_time=123,
            end_time=420,
            nume_clasa="B",
            nivel_clasa=11,
            lista_probleme=[1001, 1002, 1003],
            fetched=True
        )

        add_submission(
            kn_submission_id=88,
            time_stamp=125,
            source_code="print('Hello')",
            problem_id=1001,
            score=100,
            user_id=42,
            contest_id=contest_id,
            weird_percent=0
        )
        add_submission(
            kn_submission_id=89,
            time_stamp=126,
            source_code="print('Hello guys')",
            problem_id=1001,
            score=100,
            user_id=43,
            contest_id=1,
            weird_percent=0
        )

    elev1 = Elev("Andrei", "Andrei_the_killer", 42)
    elev2 = Elev("Vlad", "Vlad_the_killer", 43)

    submisii = get_submissions_for_elev(elev1)

    for s in submisii:
        print(s.user_id, s.score, s.time_stamp, s.content)

    concursuri = get_all_contests()

    for c in concursuri:
        print(c.id)
        print(c.name)
        print(c.lista_probleme)
        print(c.fetched)
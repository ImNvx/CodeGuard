import mysql.connector
import json
from datetime import datetime
from datasketch import MinHash, MinHashLSH
import re

CONFIG_PATH = 'config.json'
TABLE = 'solutions'

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def tokenize_cpp(code: str):
    """
    Simple normalization for C++-like code:
    - removes comments (basic)
    - splits into tokens
    - normalizes identifiers/numbers
    """
    # remove single-line comments
    code = re.sub(r"//.*", " ", code)
    # remove multi-line comments
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)

    tokens = re.findall(r"[A-Za-z_]\w*|\d+|==|!=|<=|>=|[^\s]", code)

    normalized = []
    for t in tokens:
        if t.isdigit():
            normalized.append("NUM")
        elif re.match(r"[A-Za-z_]\w*", t):
            normalized.append("ID")
        else:
            normalized.append(t)

    return normalized

def get_minhash(tokens, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for t in tokens:
        m.update(t.encode("utf8"))
    return m

def connect_mysql():
    db_login = read_json(CONFIG_PATH)

    mydb = mysql.connector.connect(
        host = db_login['mysql-host'],
        user = db_login['mysql-user'],
        password = db_login['mysql-pass'],
        database = db_login['mysql-database']
    )

    return mydb

def add_solution(solution_id, user_id, problem_id, score, timestamp, weird_percent, text): #timestamp trb UNIX
    try:
        sql_timestamp = datetime.fromtimestamp(int(timestamp) / 1000)
        sql = "INSERT INTO " + TABLE + " (solution_id, user_id, problem_id, score, timestamp, weird_percent, text) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (solution_id, user_id, problem_id, score, sql_timestamp, weird_percent, text)

        mydb = connect_mysql()
        mycursor = mydb.cursor()

        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "bagat")

        mydb.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_code(solution_id):
    try:
        sql = "SELECT text FROM " + TABLE +" WHERE solution_id = %s"
        val = (solution_id,)

        mydb = connect_mysql()
        mycursor = mydb.cursor()

        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

        mydb.close()

        return myresult[0][0]
    except Exception as e:
        print(e)
        return None


def get_similarity(solution_ids, threshold=0.5):
    """
    Returns: list where result[i] = max similarity of solution i with any other solution
    """
    solutions =[]

    for id in solution_ids:
        solution = get_code(id)
        if(solution != None):
            solutions.append(solution)
        else:
            print("erroare la similaritate cand am apelat get_code")
            return None

    n = len(solutions)

    # Build MinHash signatures
    minhashes = []
    lsh = MinHashLSH(threshold=threshold, num_perm=128)

    for i, code in enumerate(solutions):
        tokens = tokenize_cpp(code)
        m = get_minhash(tokens)

        minhashes.append(m)
        lsh.insert(str(i), m)

    # Query nearest neighbors
    max_sim = [0.0] * n

    for i in range(n):
        candidates = lsh.query(minhashes[i])

        for c in candidates:
            j = int(c)
            if i == j:
                continue

            sim = minhashes[i].jaccard(minhashes[j])
            if sim > max_sim[i]:
                max_sim[i] = sim

    return max_sim


if __name__ == "__main__":
    #add_solution(4, "eric.mester", "/problems/1", "100", "1600521939766", None, "#include <iostream>\nusing namespace std;\nint main()\n{\n    int x, y;\n    cin >> x >> y;\n    cout << x + y << \"\\n\";}")
    print(get_code(4))
    print(get_similarity([1,2,3,4]))
    exit()

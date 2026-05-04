import mysql.connector
import json
from datetime import datetime
from datasketch import MinHash, MinHashLSH
import re
from flask import Flask, request

CONFIG_PATH = 'config.json'
TABLE = 'solutions'
ACCEPTED = '100'
API_ROOT = ''

app = Flask(__name__)

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

def clean_code(code: str):
    code = re.sub(r"//.*", " ", code)
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    code = re.sub(r"\s+", "", code)  # REMOVE ALL whitespace
    return code


def char_shingles(text: str, k: int = 5):
    # character k-grams
    return {text[i:i+k] for i in range(max(0, len(text) - k + 1))}

def get_minhash(shingles, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for s in shingles:
        m.update(s.encode("utf8"))
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
    try:#           int     , string , string    ,string, string   , float / None, string
        sql_timestamp = datetime.fromtimestamp(int(timestamp) / 1000) #transformam timpu in sql
        sql = "INSERT INTO " + TABLE + " (solution_id, user_id, problem_id, score, timestamp, weird_percent, text) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (solution_id, user_id, problem_id, score, sql_timestamp, weird_percent, text)

        mydb = connect_mysql()
        mycursor = mydb.cursor()

        mycursor.execute(sql, val)
        mydb.commit()

        mydb.close()
        return True
    except Exception as e:
        print(e)
        return False

def get_code(solution_id):
    try:
        sql = "SELECT text FROM " + TABLE +" WHERE solution_id = %s" #luam dupa id
        val = (solution_id,)

        mydb = connect_mysql()
        mycursor = mydb.cursor()

        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

        mydb.close()

        return myresult[0][0]
    except Exception as e:
        return None

def get_latest(user, problem_id, score):
    try:# ultima solutie cu scorul score de la useru user la problema problem_id
        sql = "SELECT solution_id FROM " + TABLE + " WHERE user_id = %s AND problem_id = %s AND score = %s ORDER BY timestamp DESC LIMIT 1"
        val = (user, problem_id, score)

        mydb = connect_mysql()
        mycursor = mydb.cursor()

        mycursor.execute(sql, val)

        myresult = mycursor.fetchall()

        mydb.close()

        return myresult[0][0]
    except Exception as e:
        #print(e)
        return None


def get_similarity(solution_ids, threshold=0.5, k = 2):#sa ma joc cu k
    """
    Returns: list where result[i] = max similarity of solution i with any other solution
    -1 => nu am gasit submisie acceptata
    """
    solutions =[]

    for id in solution_ids:
        solution = get_code(id)
        if(solution != None):
            solutions.append(solution)
        else:
            solutions.append('')


    n = len(solutions)

    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    minhashes = []

    for i, code in enumerate(solutions):
        code = clean_code(code)
        shingles = char_shingles(code, k=k)

        m = get_minhash(shingles)
        minhashes.append(m)

        lsh.insert(str(i), m)

    max_sim = [0.0] * n

    for i in range(n):
        candidates = lsh.query(minhashes[i])

        for c in candidates:
            j = int(c)
            if i == j:
                continue

            sim = minhashes[i].jaccard(minhashes[j])
            max_sim[i] = max(max_sim[i], sim)

    for i in range(n):
        if(solutions[i] == ''):
            max_sim[i] = -1
    
    return max_sim 

def check_homework(users, problems):
    table = []
    for problem in problems:
        ids = []
        for user in users:
            id = get_latest(user, problem, ACCEPTED)
            if(id == None):
                id = 0
            ids.append(id)
        
        current = get_similarity(ids)
        table.append(current)
    return table



@app.route(API_ROOT + '/check_similarity', methods=['POST'])
def check_similarity_api():
    if request.method == 'POST':
        data = request.json 
        return get_similarity(data), 200
    else:
        return 'Method Not Allowed', 405

@app.route(API_ROOT + '/check_homework', methods=['POST'])
def check_homework_api():
    if request.method == 'POST':
        data = request.json 
        return check_homework(data['users'], data['problems']), 200
    else:
        return 'Method Not Allowed', 405


if __name__ == "__main__":
    #add_solution(9, "eric.mester", "/problems/1", "100", "1600521959766", None, "#include <iostream>\nusing namespace std;\nint main()\n{\n    int a, b;\n    cin >> a >> b;\n    cout << a + b << endl;\n}")
    #add_solution(5, "AlexVasiluta", "/problems/3", "100", "1600595318080", None ,"#include <bits/stdc++.h>\n#define DAU  ios::sync_with_stdio(false); fin.tie(0); fout.tie(0);\n#define PLEC fin.close(); fout.close(); exit(0);\nusing namespace std;\nusing VI  = vector<int>;\nusing PII = pair<int, int>;\nusing VP  = vector<PII>;\nusing VVP = vector<VP>;\nconst string task(\"chromosome\");\nifstream fin(task + \".in\");\nofstream fout(task + \".out\");\nint ind1, ind2;\nclass Path {\npublic:\n    Path() {}\n    Path(const int& _w, const vector<int>& _path)\n        : w(_w), path(_path) {}\n    inline bool operator > (const Path& P) const {\n        if (w != P.w)\n            return w > P.w;\n        ind1 = static_cast<int>(path.size());\n        ind2 = static_cast<int>(P.path.size());\n        while (ind1 > 0 && ind2 > 0) {\n            --ind1, --ind2;\n            if (path[ind1] != P.path[ind2])\n                return path[ind1] > P.path[ind2];\n        }\n        return path.size() > P.path.size();\n    }\n    inline bool operator < (const Path& P) const {\n        return P > *this;\n    }\n    inline void Tie(int& _w, vector<int>& _path) const {\n        _w = w, _path = path;\n    }\nprivate:\n    int w;\n    vector<int> path;\n};\nvector<Path> res;\nVVP g;\nVI path, fq;\npriority_queue<Path, vector<Path>, greater<Path>> q;\nint n, m, k, x, y, z, t, w, last;\nint main() {\n    DAU\n    fin >> n >> m >> k >> x >> y;\n    g = VVP(n + 1);\n    while (m--) {\n        fin >> z >> t >> w;\n        g[z].emplace_back(t, w);\n    }\n    fq = VI(n + 1);\n    path.emplace_back(x);\n    q.emplace(0, path);\n    while (!q.empty() && fq[y] < k) {\n        q.top().Tie(w, path);\n        q.pop();\n        last = path.back();\n        if (last == y)\n            res.emplace_back(w, path);\n        ++fq[last];\n        if (fq[last] <= k)\n            for (const PII& P : g[last])\n                if (find(path.begin(), path.end(), P.first) == path.end()) {\n                    path.emplace_back(P.first);\n                    q.emplace(w + P.second, path);\n                    path.pop_back();\n                }\n    }\n    sort(res.begin(), res.end());\n    fout << res.size() << '\\n';\n    for (const Path& P : res) {\n        P.Tie(w, path);\n        fout << w << ' ' << path.size() << '\\n';\n        for (const int& x : path)\n            fout << x << ' ';\n        fout << '\\n';\n    }\n    PLEC\n}")
    #add_solution(6 , "eric.mester", "/problems/3", "100", "1601108375386", None , "#include <bits/stdc++.h>\n\nusing namespace std;\nusing pi = pair<int, int>;\nusing pv = pair<int, vector<int>>;\n\nint main() {\n    ifstream cin(\"chromosome.in\");\n    ofstream cout(\"chromosome.out\");\n    int n, m, k, u, v, x, y, z;\n    cin >> n >> m >> k >> u >> v;\n    vector<vector<pi>> G(n + 1);\n    while (m--) {\n        cin >> x >> y >> z;\n        G[x].emplace_back(y, z);\n    }\n    vector<pv> ans;\n    vector<int> c(n + 1);\n    auto comp = [&](const pv& a, const pv& b) {return a.first > b.first; };\n    priority_queue<pv, vector<pv>, decltype(comp)> Q(comp);\n    Q.emplace(0, vector<int>{u});\n    while (!Q.empty() && c[v] < k) {\n        int cost, last;\n        vector<int> path;\n        tie(cost, path) = Q.top(), Q.pop();\n        last = path.back();\n        ++c[last];\n        if (last == v)\n            ans.emplace_back(cost, path);\n        if (c[last] <= k)\n            for (const auto& x : G[last])\n                if (find(path.begin(), path.end(), x.first) == path.end()) {\n                    path.emplace_back(x.first);\n                    Q.emplace(cost + x.second, path);\n                    path.pop_back();\n                }\n    }\n    sort(ans.begin(), ans.end(), [&](const pv& a, const pv& b) {\n        if (a.first != b.first)\n            return a.first < b.first;\n        auto it1 = a.second.rbegin(), it2 = b.second.rbegin();\n        for (; it1 != a.second.rend(), it2 != b.second.rend() && *it1 == *it2; ++it1, ++it2);\n        if (it1 == a.second.rend())\n            return false;\n        if (it2 == b.second.rend())\n            return true;\n        return(*it1 < *it2);\n        });\n    cout << ans.size() << '\\n';\n    for (const auto& x : ans) {\n        cout << x.first << ' ' << x.second.size() << '\\n';\n        for (const auto& y : x.second)\n            cout << y << ' ';\n        cout << '\\n';\n    }\n} ")
    #print(get_code(9))
    #print(get_code(-1))
    #print(get_similarity([9,8]))
    #print(check_homework(['eric.mester', 'AlexVasiluta', 'TREYWAY', 'atodo'], ['/problems/1', '/problems/3']))
    app.run(debug=True)
    exit()

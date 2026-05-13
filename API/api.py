from flask import Flask, request
from AI.CodeGuard_AI import CodeGuard
from API.CodeGuard_Similarity import *
from API.CodeGuard_Database import *

CONFIG_PATH = 'API/config.json'
TABLE = 'solutions'     #tabelul in care CodeGuard va memora solutiile si datele despre ele
ACCEPTED = '100'        #ce inseamna o solutie acceptata
API_ROOT = ''       #prefixul pentru api
API_PORT = 5000         #portul pe care va rula api-ul

'''
example API/config.json:
{
    "mysql-host" : "127.0.0.1",
    "mysql-user" : "myuser",
    "mysql-pass" : "mypass",
    "mysql-database" : "mydb"
}
'''

app = Flask(__name__)

guard = CodeGuard() # initalizam AI-ul
database = CodeGuard_Database(TABLE = TABLE , ACCEPTED = ACCEPTED , CONFIG_PATH = CONFIG_PATH)

def check_homework(users, problems):
    table = [] # creem tabelul in care table[i][j] = nivelul maxim de similaritate al solutiei copilului j la problema i
    for problem in problems:
        solutions = [] 
        for user in users:
            id = database.get_latest(user, problem, ACCEPTED) #gasim idul ultimei solutii corecte
            if(id == None):
                id = 0
            solution = database.get_code(id) #apoi ii luam codul
            if solution == None:
                solution = ''
            
            solutions.append(solution) #si o aduagam in lista

        current = get_similarity(solutions) #verificam similaritatea pe problema curenta
        table.append(current)
    return table


@app.route(API_ROOT + '/check_similarity', methods=['POST'])
def check_similarity_api():
    '''
    json pentru /check_similarity:
    {'solution_ids' : [id1, id2, id3, ...]}
    '''
    if request.method == 'POST':
        data = request.json 
        solution_ids = data['solution_ids']
        solutions = []

        for id in solution_ids:         #convertim din id-uri in text
            solution = database.get_code(id)
            if(solution != None):
                solutions.append(solution)
            else:
                solutions.append('')
        
        return get_similarity(solutions), 200 #returnam similaritatea
    else:
        return 'Method Not Allowed', 405

@app.route(API_ROOT + '/check_homework', methods=['POST'])
def check_homework_api():
    '''
    json pentru /check_homework:
    {
     'user_ids' : [user_id1, user_id2, user_id3, ...],
     'problem_ids' : [problem_id1, problem_id2, problem_id3, ...]
    }
    '''
    if request.method == 'POST':
        data = request.json 
        return check_homework(data['user_ids'], data['problem_ids']), 200
    else:
        return 'Method Not Allowed', 405

@app.route(API_ROOT + '/submit_and_check', methods=['POST'])
def submit_and_check_api():
    '''
    json pentru /submit_and_check:
    {
     'previous_submissions' : [solution_id1, solution_id2, solution_id3, ...],
     'current_submission' : {
            'solution_id' : (int),
            'user_id' : (string),
            'problem_id': (string),
            'score': (string),
            'text': (string)
     }
    }
    '''
    if request.method == 'POST':
        data = request.json
        previous_submissions_text = []
        for id in data['previous_submissions']:
            previous_submissions_text.append(database.get_code(id)) # ia codul de la fiecare solutie anterioara

        weird_percent = 0
        if(len(previous_submissions_text) != 0):
            weird_percent = 100 - guard.checkSubmission(previous_submissions_text, data['current_submission']['text']) # verifica solutia curenta
        database.add_solution(int(data['current_submission']['solution_id']), # apoi o aduaga in baza de date
                     data['current_submission']['user_id'],
                     data['current_submission']['problem_id'],
                     data['current_submission']['score'],
                     data['current_submission']['timestamp'],
                     weird_percent,                                     # cu "dubiosenia" verificata
                     data['current_submission']['text'])
        return str(weird_percent)
    else:
        return 'Method Not Allowed', 405

@app.route(API_ROOT + '/get_weird_percent', methods=['POST'])
def get_weird_percent_api():
    '''
    json pentru /get_weird_percent:
    {'solution_id': (int)}
    '''
    if request.method == 'POST':
        data = request.json
        weird_percent = database.get_weird_percent(data['solution_id'])
        return str(weird_percent)
    else:
        return 'Method Not Allowed', 405

@app.route(API_ROOT + '/recheck_weird_percent', methods=['POST'])
def recheck_weird_percent_api():
    '''
    json pentru /get_weird_percent:
    {
     'previous_submissions' : [(int), (int), (int), ...],
     'current_submission' : (int)
    }
    '''
    if request.method == 'POST':
        data = request.json
        previous_submissions_text = []

        for id in data['previous_submissions']:#luam codul submisilor trecute
            previous_submissions_text.append(database.get_code(id))
        current_submission_text = database.get_code(data['current_submission']) # luam codul submisiei curente

        weird_percent = 100 - guard.checkSubmission(previous_submissions_text, current_submission_text) # ii calculam diferenta

        weird_percent = database.update_weird_percent(data['current_submission'], weird_percent) # si ii dam update in baza de date

        return str(weird_percent)
    else:
        return 'Method Not Allowed', 405


if __name__ == "__main__":
    app.run(port = API_PORT, debug= True)
    exit()

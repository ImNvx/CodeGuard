from bs4 import BeautifulSoup
from lxml import etree
import requests
from CGinfo.CGinfo_ds import Clasa, Elev, Submisie, Contest
from CGinfo.database import *
from threading import Thread
from AI.CodeGuard_AI import CodeGuard
import time
from tinydb import TinyDB, Query

guard = CodeGuard() # initalizam AI-ul

CONTEXT_LENGTH = 10 # cate submisi ne intereseaza

def get_clasa(nivel, nume):
    db = TinyDB("db_clase.json")
    q = Query()
    res = db.search((q.nivel == nivel) & (q.nume == nume))
    if res:
        return Clasa(**res[0])

def get_kn_id(user): #returneaza un int, idul userurlui daca acest user exista, sau -1 daca intampina vreo eroare
    try:
        url = "https://kilonova.ro/profile/" + user

        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Convert to etree for XPath
        dom = etree.HTML(str(soup))

        
        tag = dom.xpath('/html/body/main/div[1]/div/div/a')[0]
        return int(tag.attrib['href'][22:])
    except Exception as e:
        print(e)
        return -1

def add_to_db(kn_submision_id, time_stamp, source_code, problem_id, score, user_id):
    print([kn_submision_id, time_stamp, source_code, problem_id, score, user_id])
    return

def kn_get_submission(submission):
    data = {"id" : None,
            "user" : None,
            "problem" : None,
            "timestamp" : None,
            "score" : None,
            "code" : None}

    r = requests.get('https://kilonova.ro/submissions/' + str(submission))
    dom = etree.HTML(r.content)

    data["id"] = submission
    data["user"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[1]/td[2]/a")[0].text
    data["problem"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[2]/td[2]/a/@href")[0]
    data["timestamp"] = int(dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[3]/td[2]/server-timestamp/@timestamp")[0])
    data["score"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[4]/td[2]/span")[0].text
    data["code"] = requests.get('https://kilonova.ro/submissions/' + str(submission) + '/download').text

    return data

def kn_get_submissions(elev, problema, strat_time, end_time):
    try:
        #url = "https://kilonova.ro/submissions/?problem_id=" + str(problema) + '&user_id=' + str(elev.id) 
        url = "https://kilonova.ro/submissions/"

        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Convert to etree for XPath
        dom = etree.HTML(str(soup))

        last_id = dom.xpath('/html/body/main/div/div/div[2]/table/tbody/tr[1]/th')[0].text

        #am putea optimiza sa cautam binar first_id si last_id:-))))
        id = int(last_id)

        submissions = []

        while True:
            submision = kn_get_submission(id)
            #print(submision) 
            if strat_time > submision['timestamp']:
                break
            if end_time >= submision['timestamp']:
                #print(submision['timestamp'])
                submissions.append(submision)
            id = id - 1
    except Exception as e:
        print(e)
        return []
    return submissions

def end_contest(strat_time, end_time, clasa : Clasa, probleme, contest_id):
    for elev in clasa.elevi:
        for problema in probleme:
            data = kn_get_submissions(elev, problema, strat_time, end_time)
            for submission in data:
                weird_percent = 0
                history = get_submissions_for_elev(elev, CONTEXT_LENGHT)

                if(len(history) != 0):
                    weird_percent = 100 - guard.checkSubmission(history, submission['source_code']) # verifica solutia curenta

                add_submission(submission['id'], submission['time_stamp'], submission['source_code'], submission['problem_id'], submission['score'], submission['user_id'], contest_id, weird_percent)

def get_time():
    t = int(time.time() * 1000) # ne trb in ms
    return t

def start_contest_handler():
    while True:
        contests = get_unfetched_finished_contests(get_time())
        for contest in contests:
            clasa = get_clasa(contest.nivel_clasa, contest.nume_clasa)
            end_contest(contest.start_time, contest.end_time, clasa, contest.lista_probleme, contest.id)
            update_contest_fetched(contest.id , True)

### !!!!!!!!!!! ceva e putred cu timpu pe kn cred ca ii UTC+2 sau ceva

if __name__ == "__main__":
    print(get_time())

'''
nu am test start_contest_handler si mai nimic de la contesturi, nici partea cu AI
'''
'''
Documentatie:
functii: 
    -get_clasa(nivel : int, nume : str):
        -returneaza clasa care se potriveste descrierii
        -type Clasa
    -get_kn_id(user : str):
        -returneaza idul userurlui cu username-ul user, sau -1 daca intampina o eroare
        -type int
    -kn_get_submission(submission : int)
        -returneaza submisia cu submission_idul = submission
        -type Submisie
    -kn_get_submissions(elev : Elev, problema : int, strat_time : int, end_time : int)
        -returneaza toate submissile elevului Elev de la problema problema(id), facute intre start_time(unix_ms) si end_time(unix_ms)
        -type [Submisie, Submisie, ...]
    -
'''
from bs4 import BeautifulSoup
from lxml import etree
import requests
from CGinfo.CGinfo_ds import Clasa, Elev, Submisie, Contest
from CGinfo.database import *
from threading import Thread
from datetime import datetime
from zoneinfo import ZoneInfo
from AI.CodeGuard_AI import CodeGuard # trebuie mutat pe alt thread
from API.CodeGuard_Similarity import get_similarity_2
import time
from tinydb import TinyDB, Query
import asyncio

import sys # pentru get_clasa
from pathlib import Path # pentru get_clasa


guard = CodeGuard() # initalizam AI-ul - trebuie mutat pe alt thread

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "kilonova.ro",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-GPC": "1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0",
}

CONTEXT_LENGTH = 10 # cate submisi ne intereseaza
KN_LIMIT = 20 #cate submisii furam o data(punem 20 ca suntem baieti)


# ----- get_clasa -----
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

def get_db_tinydb():
    exe_path = get_base_dir()
    path = exe_path / 'db_clase.json'
    return TinyDB(path)

def get_clasa(nivel : int, nume : str):
    db = get_db_tinydb()
    q = Query()
    res = db.search((q.nivel == nivel) & (q.nume == nume))

    if res:
        f = res[0]
        f['elevi'] = [Elev(**i) for i in f['elevi']]
        return Clasa(**res[0])
# ----- get_clasa -----

def get_kn_id(user : str): #returneaza un int, idul userurlui daca acest user exista, sau -1 daca intampina vreo eroare
    try:
        url = "https://kilonova.ro/api/user/byName/" + user

        res = requests.get(url, headers = headers)
        data = json.loads(res.text)

        return int(data['data']['id'])
    except Exception as e:
        print(e)
        return -1

def kn_get_submission(submission : int): # submission id
    data = {"id" : None,
            "user" : None,
            "problem" : None,
            "timestamp" : None,
            "score" : None,
            "code" : None}

    r = requests.get('https://kilonova.ro/submissions/' + str(submission))
    dom = etree.HTML(r.content)

    #folosim metoda veche pentru a lua datele submisiei, am putea modifica pe viitor sa folosim api-ul

    data["id"] = submission
    data["user"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[1]/td[2]/a")[0].text
    data["problem"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[2]/td[2]/a/@href")[0]
    data["timestamp"] = int(dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[3]/td[2]/server-timestamp/@timestamp")[0])
    data["score"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[4]/td[2]/span")[0].text
    data["code"] = requests.get('https://kilonova.ro/submissions/' + str(submission) + '/download').text

    return Submisie(data['id'], data['timestamp'], data['code'], 0, data['score'], 0, 0, 0, 0)

def kn_get_submissions(elev : Elev, problema : int, strat_time : int, end_time : int):
    submissions = []
    try:
        offset = 0 #pentru edge case ul in care un utilizator are mai mult de KN_LIMIT de submisii la o pb
        while True:
            payload = { #https://github.com/KiloProjects/Kilonova/blob/master/submission.go#L95
                "user_id": elev.id,
                "problem_id": problema,
                "offset": offset,
                "limit": KN_LIMIT
            }
            r = requests.get("https://kilonova.ro/api/submissions/get", headers= headers, json = payload)
            data = json.loads(r.text) #aici ne folosim de api-ul de pe kn

            for sub_json in data['data']['submissions']:
                dt = datetime.fromisoformat(sub_json['created_at'])
                unix_ms = int(dt.timestamp()) * 1000 # ne trb in ms

                #kilnova are timezone de +1, dar tot afiseaza timpul corect, ii foarte dubios

                if(end_time >= unix_ms and strat_time <= unix_ms): #concursul inca ruleaza
                    submission = kn_get_submission(sub_json['id']) 

                    submission.user_id = elev.id #umplem fielduri aditionale
                    submission.problem_id = problema

                    submissions.append(submission)
                elif(strat_time > unix_ms):
                    break #caput

            if(data['data']['count'] == KN_LIMIT): #daca am verificat toate KN_LIMIT si inca nu am ajuns la inceputul contestului
                offset = offset + KN_LIMIT
            else:
                break
    except Exception as e:
        print(e)
        return []
    return submissions

def end_contest(strat_time : int, end_time : int, clasa : Clasa, probleme : list, contest_id : int):
    for elev in clasa.elevi:
        for problema in probleme:
            data = kn_get_submissions(elev, problema, strat_time, end_time)
            for submission in data:
                submission.contest_id = contest_id
                weird_percent = 0
                history = get_batch_for_ai(elev, CONTEXT_LENGTH)
                history_text = []
                for item in history:
                    history_text.append(item.content)

                if(len(history_text) != 0):
                    submission.weird_percent = 100 - guard.checkSubmission(history_text, submission.content) # verifica solutia curenta

                submission.weird_percent = round(submission.weird_percent, 2)

                add_submission(submission)

    for elev in clasa.elevi:
        for problema in probleme:
            batch_self = get_batch_for_jaccard_self(elev, problema, contest_id, CONTEXT_LENGTH)
            batch_other = get_batch_for_jaccard_other(elev, problema, contest_id, CONTEXT_LENGTH)

            self_text = []
            for submission in batch_self:
                self_text.append(submission.content)

            other_text = []
            for submission in batch_other:
                other_text.append(submission.content)

            similarity_percent = get_similarity_2(other_text , self_text)

            for i in range(len(batch_self)):
                submission = batch_self[i]
                sim = similarity_percent[i]
                update_submission_similarity(submission.id, submission.contest_id, sim)
            

def get_time():
    t = int(time.time() * 1000) # ne trb in ms
    return t

async def start_contest_handler():
    while True:
        contests = get_unfetched_finished_contests(get_time())
        for contest in contests:
            clasa = get_clasa(contest.nivel_clasa, contest.nume_clasa)
            end_contest(contest.start_time, contest.end_time, clasa, contest.lista_probleme, contest.id)
            update_contest_fetched(contest.id , True)
        await asyncio.sleep(0.5) # pare ok cu 0.5 dar cred ca merge si cu 1

if __name__ == "__main__":
    initialize_database()
    if(False):
        contest_id = add_contest(
            name="ONI 2026",
            start_time=get_time(),
            end_time=0,
            nume_clasa="AB",
            nivel_clasa=11,
            lista_probleme=[2506,23],
            fetched=False
        )
        print(contest_id)
    elev1 = Elev("Eric Mester", 'eric.mester', get_kn_id('eric.mester'))
    elev2 = Elev("David Busoi", 'Involve_X', get_kn_id('Involve_X'))
    clasa = Clasa(11, nume="AB", nr_elevi=2, elevi=[elev1,elev2])
    end_contest(0, get_time(), clasa, [2506,23],2)
    print(get_submissions_for_elev(elev1))
    print(get_submissions_for_elev(elev2))
    exit()
    payload = {
        "id": None,
        "ids": [1129601],
        "user_id": None,
        "problem_id": None,
        "problem_list_id": None,
        "contest_id": None,
    }
    t("https://kilonova.ro/api/submissions/get", headers = headers, json = payload)
    print(json.loads(r.text))

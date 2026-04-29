import json
import pandas as pd
from io import StringIO
from random import randint
import requests
from lxml import etree

#USERS = ['eric.mester', 'buzdi', 'EricTiberiuFrancu', 'LucaLucaM ', 'ASN49K', 'laura', 'atodo']
USERS = []
PREFIX = "https://kilonova.ro/submissions/"
SUFIX = "/download"

def get_data(submission):
    data = {"id" : None,
            "user" : None,
            "problem" : None,
            "timestamp" : None,
            "score" : None,
            "code" : None}

    r = requests.get(PREFIX + str(submission))
    dom = etree.HTML(r.content)

    data["id"] = submission
    data["user"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[1]/td[2]/a")[0].text
    data["problem"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[2]/td[2]/a/@href")[0]
    data["timestamp"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[3]/td[2]/server-timestamp/@timestamp")[0]
    data["score"] = dom.xpath("/html/body/main/div/div[1]/aside/div[1]/table/tbody/tr[4]/td[2]/span")[0].text
    data["code"] = requests.get(PREFIX + str(submission) + SUFIX).text

    return data

def get_users(le, ri, cnt = 50):
    ret = []
    for i in range(cnt):
        id = randint(le, ri)
        try:
            pb = get_data(id)
            ret.append(pb['user'])
        except Exception as e:
            print(e)
    return ret
    
def read_first_n(file_path, le, ri):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i > ri:
                break
            if i >= le:
                x = json.loads(line)
                if(len(x['code']) <= 50 or not('#include' in x['code'])):
                    continue
                if(len(data) == 0 and x['user'] in USERS and x['score'] == '100') :
                    data.append(x)
                elif(x['user'] in USERS and x['score'] == '100' and x['code'] != data[-1]['code']):
                    data.append(x)
    return data

def goy(text):
    return ' '.join(text.replace('\\n', '\n').split())

le = 1
ri = 1000000
cnt = 50

USERS = get_users(le, ri, cnt)

data_json = json.dumps(read_first_n('kilonova.json', 1, 1000000))

df = pd.read_json(StringIO(data_json))
df['code'] = df['code'].apply(goy)

data_csv = df.to_csv(index=False)

with open('kilonova.csv', 'w', encoding='utf-8') as f:
    f.write(data_csv)

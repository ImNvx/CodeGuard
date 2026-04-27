import requests
from bs4 import BeautifulSoup
import json
from lxml import etree

RATELIMIT = 1000
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

def write(data):
    with open('kilonova.json', 'a', encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

start = int(input("last scraped:")) + 1
end_str = input("end:")
end = 0

if(end_str == ''):
    end = 1094895
else:
    end = int(end_str)

end = end + 1

for i in range(start, end):
    try:
        print("\n" + str(i) + " : ", end = "")
        write(get_data(i))
    except Exception as e:
        print(e, end = '')
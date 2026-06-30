from bs4 import BeautifulSoup
from lxml import etree
import requests

def get_kn_id(user):
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


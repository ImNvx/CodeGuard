import json
import pandas as pd
from io import StringIO

USER = 'BatinCatalin'

def read_first_n(file_path, le, ri):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i > ri:
                break
            if i >= le:
                x = json.loads(line)
                if(len(data) == 0 and x['user'] == USER and x['score'] == '100') :
                    data.append(x)
                elif(x['user'] == USER and x['score'] == '100' and x['code'] != data[-1]['code']):
                    data.append(x)
    return data

def goy(text):
    return text.replace('\n',  ' ')

data_json = json.dumps(read_first_n('kilonova.json', 1, 50000))

df = pd.read_json(StringIO(data_json))
df['code'] = df['code'].apply(goy)

data_csv = df.to_csv(index=False)

with open('kilonova.csv', 'w') as f:
    f.write(data_csv)

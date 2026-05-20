import pandas as pd
from random import randint
import json

IN_FILE = 'kilonova.csv'
OUT_FILE = 'train.jsonl'

FIRST_COUNT = 100
EXTRA_COUNT = 5000

df = pd.read_csv(IN_FILE)

records = df.to_dict('records')
LINE_COUNT = len(records)

train = []

def get_data(i, j):
    row1 = records[i]
    row2 = records[j]
    
    val = 1 if row1['user'] == row2['user'] else 0
    return {
        "cod1": row1['code'],
        "cod2": row2['code'],
        "autor1": row1['user'],
        "autor2": row2['user'],
        "problema1": row1['problem'],
        "problema2": row2['problem'],
        "label": val
    }

for i in range(min(FIRST_COUNT, LINE_COUNT)):
    for j in range(i + 1, min(FIRST_COUNT, LINE_COUNT)):
        train.append(get_data(i, j))

for _ in range(EXTRA_COUNT):
    i = randint(0, LINE_COUNT - 1)
    j = randint(0, LINE_COUNT - 1)
    train.append(get_data(i, j))

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    for item in train:
        f.write(json.dumps(item) + '\n')

print("gata")
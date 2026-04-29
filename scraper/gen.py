import pandas as pd
from random import randint

IN_FILE = 'kilonova.csv'
OUT_FILE = 'train.csv'
LINE_COUNT = 0

with open(IN_FILE, 'r') as fp:
    LINE_COUNT = sum(1 for line in fp)

LINE_COUNT = LINE_COUNT - 1

FIRST_COUNT = 100
EXTRA_COUNT = 5000

df = pd.read_csv(IN_FILE)

train =[]

def get_data(i , j):
    val = 0
    if(df['user'].loc[df.index[i]] == df['user'].loc[df.index[j]]):
        val = 1
    return [df['code'].loc[df.index[i]] , df['code'].loc[df.index[j]] , df['problem'].loc[df.index[i]] , df['problem'].loc[df.index[j]] , val]

for i in range(FIRST_COUNT):
    for j in range(i + 1, FIRST_COUNT):
        train.append(get_data(i,j))

for x in range(EXTRA_COUNT):
    i = randint(0 , LINE_COUNT - 1)
    j = randint(0 , LINE_COUNT - 1)
    train.append(get_data(i,j))

dff = pd.DataFrame(train, columns=['cod1', 'cod2', 'problema1', 'problema2','label'])

train_csv = dff.to_csv()

with open( OUT_FILE, 'w', encoding='utf-8') as f:
    f.write(train_csv)

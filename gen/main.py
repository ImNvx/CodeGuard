import json

def read_first_n(file_path, n):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            data.append(json.loads(line))
    return data



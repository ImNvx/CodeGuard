from API.CodeGuard_Database import *
from datasketch import MinHash, MinHashLSH
import re

def clean_code(code: str):
    code = re.sub(r"//.*", " ", code)
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    code = re.sub(r"\s+", "", code)  # REMOVE ALL whitespace
    return code


def char_shingles(text: str, k: int = 5):
    # character k-grams
    return {text[i:i+k] for i in range(max(0, len(text) - k + 1))}

def get_minhash(shingles, num_perm=128):
    m = MinHash(num_perm=num_perm)
    for s in shingles:
        m.update(s.encode("utf8"))
    return m

def get_similarity(solutions, threshold=0.5, k = 2):#sa ma joc cu k
    """
    Returns: list where result[i] = max similarity of solution i with any other solution
    -1 => nu am gasit submisie acceptata
    """
    n = len(solutions)

    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    minhashes = []

    for i, code in enumerate(solutions):
        code = clean_code(code)
        shingles = char_shingles(code, k=k)

        m = get_minhash(shingles)
        minhashes.append(m)

        lsh.insert(str(i), m)

    max_sim = [0.0] * n

    for i in range(n):
        candidates = lsh.query(minhashes[i])

        for c in candidates:
            j = int(c)
            if i == j:
                continue

            sim = minhashes[i].jaccard(minhashes[j])
            max_sim[i] = max(max_sim[i], sim)

    for i in range(n):
        if(solutions[i] == ''):
            max_sim[i] = -1
        else:
            max_sim[i] = max_sim[i] * 100
    
    return max_sim 
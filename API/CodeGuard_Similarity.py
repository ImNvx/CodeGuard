import re
from collections import Counter

def clean_code(code: str) -> str:
    code = re.sub(r"//.*?$", " ", code, flags=re.M)
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    code = re.sub(r"#.*?$", " ", code, flags=re.M)
    return code


def normalize_tokens(code: str):
    """
    Replace identifiers with VAR to preserve structure
    """
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|[^\s]", code)

    normalized = []
    for t in tokens:
        if re.match(r"[A-Za-z_]\w*", t) and t not in {
            "for", "while", "if", "else", "return",
            "def", "class", "in", "range", "True", "False"
        }:
            normalized.append("VAR")
        else:
            normalized.append(t)

    return normalized


def shingles(tokens, k=3):
    if len(tokens) < k:
        return {" ".join(tokens)}
    return {
        " ".join(tokens[i:i+k])
        for i in range(len(tokens) - k + 1)
    }


def jaccard(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def preprocess(code, k=3):
    code = clean_code(code)
    tokens = normalize_tokens(code)
    return shingles(tokens, k)


def get_similarity(solutions, k=3):
    n = len(solutions)

    processed = []
    for code in solutions:
        if not code:
            processed.append(set())
        else:
            processed.append(preprocess(code, k))

    max_sim = [0.0] * n

    for i in range(n):
        for j in range(i + 1, n):
            sim = jaccard(processed[i], processed[j])

            # boost small similarities slightly (important fix)
            sim = sim ** 0.7   # nonlinear scaling

            max_sim[i] = max(max_sim[i], sim)
            max_sim[j] = max(max_sim[j], sim)

    for i in range(n):
        if not solutions[i]:
            max_sim[i] = -1
        else:
            max_sim[i] *= 100

    return max_sim
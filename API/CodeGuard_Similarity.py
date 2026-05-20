import re
from collections import Counter

def clean_code(code: str) -> str:
    # sterge comentariile de tip //
    code = re.sub(r"//.*?$", " ", code, flags=re.M)

    # sterge comentariile de tip /* */
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)

    return code


def normalize_tokens(code: str):
    """
    Inlocuieste numele variabilelor cu VAR
    ca sa pastreze structura codului
    """

    # separa codul in token-uri
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|[^\s]", code)

    normalized = []

    for t in tokens:
        # verifica daca token-ul este identificator
        if re.match(r"[A-Za-z_]\w*", t) and t not in {
            "for", "while", "if", "else", "return",
            "def", "class", "in", "range", "True", "False"
        }:
            normalized.append("VAR")
        else:
            normalized.append(t)

    return normalized


def shingles(tokens, k=3):
    # daca sunt prea putine token-uri
    if len(tokens) < k:
        return {" ".join(tokens)}

    # creeaza grupuri de cate k token-uri
    return {
        " ".join(tokens[i:i+k])
        for i in range(len(tokens) - k + 1)
    }


def jaccard(a, b):
    # cazul in care ambele seturi sunt goale
    if not a and not b:
        return 1.0

    # formula Jaccard
    return len(a & b) / len(a | b)


def preprocess(code, k=3):
    # elimina comentariile
    code = clean_code(code)

    # normalizeaza token-urile
    tokens = normalize_tokens(code)

    # genereaza shingles
    return shingles(tokens, k)


def get_similarity(solutions, k=3):
    n = len(solutions)

    processed = []

    # prelucreaza fiecare solutie
    for code in solutions:
        if not code:
            processed.append(set())
        else:
            processed.append(preprocess(code, k))

    # tine minte similaritatea maxima
    max_sim = [0.0] * n

    # compara fiecare pereche
    for i in range(n):
        for j in range(i + 1, n):

            sim = jaccard(processed[i], processed[j])

            # mareste putin valorile mici
            sim = sim ** 0.7

            max_sim[i] = max(max_sim[i], sim)
            max_sim[j] = max(max_sim[j], sim)

    # transforma in procente
    for i in range(n):
        if not solutions[i]:
            max_sim[i] = -1
        else:
            max_sim[i] *= 100

    return max_sim
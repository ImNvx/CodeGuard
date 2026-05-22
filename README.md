<img width="2560" height="1440" alt="CodeGuard_logo" src="https://github.com/user-attachments/assets/eb2374aa-bc22-4c22-aa10-14b34e202f3a" />

> *"Copie detectată, media afectată."*
> *"Variabile schimbate, restanțe asigurate."*
> *"Ai schimbat un i cu j, Să treci testul cu curaj. Dar rețeaua mea e smart, Și te prinde la plagiat!"*
> *"Datasetu-i de cinci giga, Procesorul stă și strigă. Placa video s-a prăjit, Dar modelul a ieșit!"*

## Ce este CodeGuard?
CodeGuard este un sistem inteligent de analiză a codului sursă, conceput pentru a detecta plagiatul și a evalua autenticitatea soluțiilor încărcate de utilizatori. Sistemul îmbină tehnici clasice de analiză a similarității textuale (Jaccard similarity) cu metode avansate de Inteligență Artificială (Transformer + MLP) pentru a evalua un "grad de dubioșenie" (weird percent) bazat pe stilul de programare al fiecărui utilizator.

## Instalare (Librarii Necesare)
Dependințele necesare rularii proiectului pot fi instalate folosind `pip`:

```bash
pip install -r requirments.txt
```

Un set de comenzi pentru a descarca proiectul si dependentele sale este urmatorul:
```bash
git clone https://github.com/ImNvx/CodeGuard.git
cd CodeGuard
pip install -r requirments.txt
```

Pachetele folosite includ: `mysql-connector-python`, `DateTime`, `regex`, `Flask`, `torch` și `transformers`.

## Configuratie

Fisier: `API/config.json`

```json
{
  "mysql-host": "127.0.0.1",
  "mysql-user": "myuser",
  "mysql-pass": "mypass",
  "mysql-database": "mydb"
}
```

In fisierul `API/api.py` se mai pot configura urmatoarele
```python
TABLE = 'solutions'     #tabelul in care CodeGuard va memora solutiile si datele despre ele
ACCEPTED = '100'        #ce inseamna o solutie acceptata
API_ROOT = ''           #prefixul pentru api (ex: daca API_ROOT = 'api' pentru a accesa endpointul 'submit_and_check' adresa web va fi: http://example.com:5000/api/submit_and_check )
API_PORT = 5000         #portul pe care va rula api-ul
```

## Utilizare

Pentru a porni API-ul rulati urmatoarea comanda din folderul principal al proiectului
```bash
python3 -m API.api
```

Pentru a rula check_folder pe alt sistem de operare decat Windows rulati urmatoarea comanda din folderul principal al proiectului
```bash
python3 -m OFFLINE.check_folder
```

---

## Structura Proiectului

Proiectul este împărțit în patru module principale:
1. **API** - Interfața de comunicare web (Flask) și gestiunea bazei de date.
2. **AI** - Modelele de inteligență artificială pentru generarea amprentelor de cod.
3. **OFFLINE** - Scripturi pentru verificarea similarității locale pe sisteme de fișiere.
4. **POC (Proof of Concept)** - O aplicație demonstrativă de tip web pentru a testa si demonstra API-ul.

---

## 1. Modulul API

Acest modul expune funcționalitățile de bază ale CodeGuard prin intermediul unor endpoint-uri REST.

### `api.py`
Aplicația principală Flask care expune endpoint-urile:
- `POST /check_similarity`: Primește o listă de ID-uri de soluții și returnează un tabel cu similaritățile (procentaje) între toate perechile de soluții, folosind metode clasice (Jaccard).
- `POST /check_homework`: Verifică tema pentru mai mulți utilizatori și probleme, găsind ultima soluție acceptată a fiecăruia și comparându-le.
- `POST /submit_and_check`: Adaugă o nouă soluție în baza de date. Dacă există submisii anterioare, sistemul AI evaluează gradul de "dubioșenie" (`weird_percent`) comparând soluția curentă cu amprentele stilului anterior al utilizatorului.
- `POST /get_weird_percent`: Returnează procentul calculat pentru un anumit `solution_id`.
- `POST /recheck_weird_percent`: Recalculează procentajul de autenticitate folosind submisiile trecute specificate și dă update în baza de date.

### `CodeGuard_Database.py`
Gestionează conexiunea și interogările la baza de date MySQL.
- Baza de date memorează detaliile submisiei (`solution_id`, `user_id`, `problem_id`, `score`, `timestamp`, `weird_percent`, `text`).
- Funcții de bază: `add_solution`, `get_code`, `get_weird_percent`, `update_weird_percent`, `get_latest`.
- Fișierul de configurare necesar: `API/config.json`.

### `CodeGuard_Similarity.py`
Implementează analiza algoritmică a similarității codului:
- `clean_code(code)`: Elimină comentariile (`//` și `/* */`).
- `normalize_tokens(code)`: Păstrează cuvintele cheie structurale (`for`, `while`, `if`, etc.) dar înlocuiește numele variabilelor și funcțiilor utilizatorului cu tokenul generic `VAR`.
- `shingles(tokens, k=3)`: Grupează codul normalizat în secvențe de lungime `k`.
- `jaccard(a, b)`: Calculează similaritatea Jaccard între două seturi de shingles. Procentele rezultate sunt ajustate exponențial (puterea 0.7) pentru a amplifica vizibilitatea scorurilor mici/medii.

---
## 2. Modulul AI

Responsabil pentru detectarea deviațiilor de la stilul obișnuit al unui programator.

### `CodeGuardEncoder.py`
Arhitectura modelului și antrenarea:
- Funcția `getFeatures(code)`: Extrage 10 caracteristici de stil din cod (ex. camelCase, snake_case, pascalCase, K&R braces, Allman braces, distanțarea operatorilor, gradul de indentare, raportul de comentarii).
- `CodeGuardHybrid`: O arhitectură neuronală hibridă PyTorch. Include:
  - O componentă **Transformer Encoder** care primește codul tokenizat, adaugă Positional Encoding și generează un `mean_pooled` vector.
  - Un **MLP (Multi-Layer Perceptron)** simplu pentru trăsăturile de stil extrase de `getFeatures`.
  - Combinarea celor două rezultând un "fingerprint" (o amprentă a codului) de ieșire normalizată.
- Scriptul include logica de antrenare folosind PyTorch, dataset-uri HuggingFace, și `CosineEmbeddingLoss` pentru a apropia amprentele scrise de același utilizator.

### `CodeGuard_AI.py`
Interfața de inferență a modelului:
- Clasa `CodeGuard` încarcă modelul (`CodeGuard_encoder_v2.pth`) și tokenizatorul la inițializare.
- Funcția `checkSubmission`: Codifică submisiile anterioare ale utilizatorului pentru a calcula un centroid (media amprentelor). Apoi calculează `cosine_similarity` între centroid și vectorul submisiei curente.
- Transformă rezultatul într-un `weird_percent`, scalând intervalul de similaritate a modelului pentru a reprezenta probabilitatea de cod străin/plagiat.

---
## 3. Modulul OFFLINE

Oferă posibilitatea de a verifica offline, din linia de comandă, o structură de directoare.

### `check_folder.py` (și executabilul `check_folder.exe`)
- Analizează recursiv un folder (ex: lucrările unor elevi, separate prin foldere).
- Pentru fiecare folder, compară similaritatea între toate fișierele conținute, folosind funcțiile clasice de la `CodeGuard_Similarity.py`.
- Afișează în terminal o structură arborescentă ("tree"), semnalizând cu roșu similaritățile mari (peste 70%), simplu pentru scoruri medii și cu verde pentru scoruri mici, ajutând profesorii sau asistenții să identifice rapid sursele copiate local.
- check_folder.exe este un executabil "stand-alone"

---

## 4. Modulul POC (Proof of Concept)

### `proof_of_concept.py`
Aplicație de frontend/demonstrație care consumă API-ul de bază:
- Folosește Flask pentru a servi `poc_index.html` (din `templates/`).
- Include un API proxy integrat (`/poc/<path>`) care redirecționează cu ușurință cererile din browser (care pot avea probleme de CORS) către instanța locală a API-ului principal (portul `5000`).
- poate fi rulat din folderul principal cu `python3 -m POC.proof_of_concept`

### `CGinfo/app.py`
O aplicație secundară Flask izolată, destinată testării directe a funcționalităților AI:
- Rulează pe portul `5001` și expune o interfață de bază (`index.html`).
- `POST /check`: Un endpoint care importă și folosește direct modulul `CodeGuard_AI` (fără a interacționa cu baza de date MySQL). Compară codul curent cu o listă de submisii anterioare furnizate prin JSON și returnează gradul de "dubioșenie" (`weird_percent`). Funcționează ca un mediu de testare rapidă, dedicat strict inferențelor rețelei neuronale.
- poate fi rulat din folderul principal cu `python3 -m POC.CGinfo.app`
  
---


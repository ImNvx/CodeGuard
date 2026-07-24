<img width="2560" height="1440" alt="CodeGuard_logo" src="https://github.com/user-attachments/assets/eb2374aa-bc22-4c22-aa10-14b34e202f3a" />

> *"Copie detectată, media afectată."*
> *"Variabile schimbate, restanțe asigurate."*
> *"Ai schimbat un i cu j, Să treci testul cu curaj. Dar rețeaua mea e smart, Și te prinde la plagiat!"*
> *"Datasetu-i de cinci giga, Procesorul stă și strigă. Placa video s-a prăjit, Dar modelul a ieșit!"*

# CodeGuard

**O suita de aplicatii software pentru detectarea plagiatului din codul sursa.**

CodeGuard este o platforma de analiza a codului sursa. Sistemul combina tehnici clasice de similaritate textuala (Jaccard similarity cu normalizare structurala) cu un model de inteligenta artificiala antrenat de noi cu o arhitectura de tip hibrid (Transformer si Multi-Layer Perceptron), pentru a genera amprente de stil unice fiecarui utilizator si a evalua autenticitatea submisiilor.

Componenta principala, **CGinfo Dashboard**, ofera o interfata grafica pentru gestionarea claselor, elevilor si a concursurilor, integrata cu platforma [Kilonova.ro](https://kilonova.ro) pentru colectarea automata a submisiilor.

---

## Instalare

Pentru Windows oferim si optiunea de a rula ```CGinfo_dashboard``` si ```verificarea offline``` doar cu niste executabile disponibile in sectiunea **Releases**

### Cerinte preliminare

- Python 3.10 sau mai nou
- pip

### Instalarea dependentelor

```bash
git clone https://github.com/ImNvx/CodeGuard.git
cd CodeGuard
python3 -m pip install -r requirements.txt
```

Pachetele principale: `torch`, `transformers`, `Flask`, `flet`, `flet-code-editor`, `tinydb`, `beautifulsoup4`, `lxml`, `requests`, `mysql-connector-python`, `sqlite3`.

---

## Utilizare

*Urmatoarele comenzi trebuie rulate din radacina repo-ului.*
*Note: Mentionam ca la prima rulare a CGinfo_Dashboard/API va dura mai mult pana se vor initializa baza de date si ai-ul*

### CGinfo Dashboard (aplicatia principala)

```bash
python3 -m CGinfo.CGinfo_dashboard
```
*(Sau prin rularea executabilului disponibil in sectiunea **Releases**)*

### API REST

```bash
python3 -m API.api
```

### Verificare offline (linia de comanda)

```bash
python3 -m OFFLINE.check_folder
```

*(Sau prin rularea executabilului disponibil in sectiunea **Releases**)*

---


## Cuprins

- [CGinfo Dashboard](#cginfo-dashboard)
  - [Prezentare generala](#prezentare-generala)
  - [Functionalitati principale](#functionalitati-principale)
  - [Arhitectura](#arhitectura-proiectului)
  - [Captarea si procesarea submisiilor](#captarea-si-procesarea-submisiilor)
- [Module suport](#module-suport)
  - [Modulul API](#modulul-api)
  - [Modulul AI](#modulul-ai)
  - [Modulul OFFLINE](#modulul-offline)
- [Configuratie (modulul API)](#configuratie)

---

## CGinfo Dashboard

### Prezentare generala

CGinfo Dashboard este o aplicatie cross-platform construita cu [Flet](https://flet.dev/). Am ales Flet deoarece este un framework lightweight, iar faptul ca integreaza Material 3 Expressive si Cupertino Design Framework a fost un mare plus. Aplicatia se conecteaza la platforma kilonova.ro, colecteaza automat submisiile elevilor la finalul fiecarui concurs si le analizeaza prin doua metode complementare:

| Metrica | Metoda | Scop |
|---|---|---|
| **Similaritate Jaccard** | Analiza structurala clasica | Detecteaza copierea directa intre submisii prin compararea shingle-urilor normalizate |
| **Nesimilaritate de stil (weird percent)** | Retea neuronala hibrida | Evalueaza daca o submisie se abate de la stilul de programare istoric al utilizatorului |

### Functionalitati principale

**Gestionare clase si elevi**
- Crearea si administrarea claselor
- Adaugarea si eliminarea elevilor cu validare automata a existentei utilizatorului pe Kilonova.

**Gestionare concursuri**
- Crearea concursurilor cu nume, lista de probleme si interval orar
- Monitorizare a concursurilor active
- Istoric complet al concursurilor anterioare per clasa

**Analiza submisiilor**
- Colectare automata a submisiilor de pe Kilonova la finalul concursului
- Calcul automat al metricilor de similaritate si autenticitate
- Vizualizare detaliata a fiecarei submisii, incluzand:
  - Scorul obtinut pe submisia respectiva
  - Procentul de similaritate Jaccard fata de celelalte submisii
  - Procentul de nesimilaritate de stil (AI) fata de istoricul utilizatorului
  - Codul sursa complet

### Arhitectura proiectului

```
CGinfo Dashboard
├── CGinfo_dashboard.py      Punctul de intrare
├── CGinfo_methods.py        Componente UI si logica de navigare
├── CGinfo_ds.py             Structuri de date (Clasa, Elev, Submisie, Contest)
├── database.py              Operatii SQLite (submisii, concursuri)
└── kn.py                    Integrare API Kilonova si handler concursuri
```

Aplicatia utilizeaza doua baze de date:

- **TinyDB** (`db_clase.json`) pentru stocarea claselor si a elevilor asociati. Am ales TinyDB deoarece este foarte usor de lucrat cu el in Python si nu aveam nevoie de o baza de date complexa la aceste date.
- **SQLite** (`Userdata/CGinfo.db`) pentru stocarea submisiilor si a concursurilor. A fost nevoie de SQLite aici, deoarece codul sursa poate sa ajunga sa ocupe mult spatiu si vrem ca interogarile sa fie facute cat mai rapid si eficient. Faptul ca este serverless a fost o caracteristica importanta.

### Captarea si procesarea submisiilor

La finalul fiecarui concurs, un handler asincron ruleaza automat urmatorul flux:

```
Concurs incheiat
    │
    ├── Pentru fiecare elev si problema:
    │       │
    │       ├── Interogare API Kilonova (submisii in intervalul de timp al concursului)
    │       ├── Descarcare cod sursa
    │       ├── Calcul weird_percent (AI) pe baza istoricului elevului
    │       └── Salvare in baza de date SQLite
    │
    └── Pentru fiecare elev si problema (a doua trecere):
            │
            ├── Calcul similaritate Jaccard intre submisiile proprii si cele ale celorlalti
            └── Actualizare similarity_percent in baza de date
```

Handler-ul verifica periodic daca exista concursuri incheiate care nu au fost inca procesate, si asigura colectarea automata a submisiilor.

---

## Module suport

### Modulul API

Modulul API expune functionalitatile CodeGuard prin endpoint-uri REST, bazate pe Flask. Acesta opereaza independent de CGinfo Dashboard si poate fi utilizat pentru integrarea cu platforme externe, precum website-uri de programare competitiva.

**Endpoint-uri disponibile:**

| Endpoint | Metoda | Descriere |
|---|---|---|
| `/check_similarity` | POST | Compara similaritatea intre o lista de solutii existente (Jaccard) |
| `/check_homework` | POST | Verifica temele pentru mai multi utilizatori si probleme |
| `/submit_and_check` | POST | Adauga o solutie si evalueaza gradul de nesimilaritate de stil |
| `/get_weird_percent` | POST | Returneaza procentul calculat pentru un `solution_id` |
| `/recheck_weird_percent` | POST | Recalculeaza procentul cu submisii actualizate |

**Fisiere componente:**

- `api.py` — Aplicatia Flask cu definitiile endpoint-urilor
- `CodeGuard_Database.py` — Gestiunea conexiunii si interogarilor MySQL
- `CodeGuard_Similarity.py` — Implementarea analizei de similaritate (curatare cod, normalizare tokenuri, shingle-uri, Jaccard cu ajustare exponentiala)

**Nota:** Modulul API utilizeaza MySQL ca baza de date, spre deosebire de CGinfo Dashboard care foloseste SQLite. Fisierul de configurare necesar este `API/config.json`.

---

### Modulul AI

Modulul de inteligenta artificiala este responsabil pentru generarea amprentelor de stil si detectarea deviatiilor de la comportamentul obisnuit al unui programator.

**Arhitectura modelului (`CodeGuardHybrid`):**

Modelul este o retea neuronala hibrida creata cu ajutorul PyTorch, compusa din doua ramuri:

1. **Transformer Encoder** — Proceseaza codul tokenizat folosindu-se de Positional Encoding din celebra lucrare stiintifica "Attention is all you need" si genereaza un vector prin mean pooling. Aceasta ramura extrage particularitatile sintactice si lexicale (denumirea variabilelor, etc.)

2. **MLP (Multi-Layer Perceptron)** — Proceseaza 10 caracteristici de stil extrase explicit din cod:
   - Conventii de denumire (camelCase, snake_case, PascalCase, etc.)
   - Stilul de plasare a acoladelor
   - Distantarea operatorilor
   - Gradul de indentare
   - Raportul de comentarii

Cele doua ramuri sunt concatenate si proiectate intr-un vector de amprenta normalizat.

**Inferenta (`CodeGuard_AI.py`):**

Procesul de evaluare a unei submisii noi:
1. Se tokenizeaza submisiile anterioare ale utilizatorului pentru a calcula un centroid (media amprentelor), cu cat avem mai multe submisii anterioare, cu atat modelul este mai precis.
2. Se calculeaza `cosine_similarity` intre centroid si vectorul rezultat din submisia curenta
3. Rezultatul este transformat intr-un `weird_percent` — o valoare scalata care indica probabilitatea ca submisia nu apartine utilizatorului

---

### Modulul OFFLINE

Modulul OFFLINE ofera posibilitatea de verificare a similaritatii codului direct din linia de comanda, fara a necesita o baza de date sau conexiune la internet.

**`check_folder.py`** (disponibil si ca executabil standalone `check_folder.exe`):

- Analizeaza recursiv un director cu structura `folder/elev/fisiere`
- Compara similaritatea intre toate fisierele din fiecare subdirector
- Afiseaza rezultatele intr-o structura arborescenta cu codificare cromatica:
  - **Rosu** — Similaritate ridicata (peste 70%), necesita verificare
  - **Standard** — Similaritate moderata
  - **Verde** — Similaritate scazuta, fara indicii de copiere

---

## Configuratie

### Modulul API (MySQL) *(Doar pentru utilizatorii care vor sa integreze CodeGuard in website-ul lor)*

Fisier: `API/config.json`

```json
{
  "mysql-host": "127.0.0.1",
  "mysql-user": "myuser",
  "mysql-pass": "mypass",
  "mysql-database": "mydb"
}
```

Parametri configurabili in `API/api.py`:

```python
TABLE = 'solutions'     # Tabelul pentru stocarea solutiilor
ACCEPTED = '100'        # Valoarea care defineste o solutie acceptata
API_ROOT = ''           # Prefixul URL pentru toate endpoint-urile
API_PORT = 5000         # Portul pe care ruleaza serverul Flask
```

### CGinfo Dashboard

Baza de date SQLite (`Userdata/CGinfo.db`) este creata automat la prima rulare. Datele claselor si elevilor sunt stocate in `CGinfo/db_clase.json`, si pot fi gestionate exclusiv prin interfata grafica.

---

## Mentiuni Info-Educatie

Contributie Bușoi David:
- Model AI
- Frontend CGinfo_Dashboard
- Logo CodeGuard

Contributie Meștereagă Eric:
- Similaritatea cu Jaccard
- API
- Backend CGinfo_Dashboard
- Modulul OFFLINE

Pentru acest proiect **NU** am folosit LLM-uri pentru a scrie cod.

## Licenta

CodeGuard — A source code plagiarism detection suite.
Copyright (C) 2026 Bușoi David, Meștereagă Eric

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

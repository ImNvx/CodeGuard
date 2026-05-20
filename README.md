<img width="2560" height="1440" alt="CodeGuard_logo" src="https://github.com/user-attachments/assets/eb2374aa-bc22-4c22-aa10-14b34e202f3a" />

> *"Copie detectată, media afectată."*
> *"Variabile schimbate, restanțe asigurate."*
> *"Ai schimbat un i cu j, Să treci testul cu curaj. Dar rețeaua mea e smart, Și te prinde la plagiat!"*
> *"Datasetu-i de cinci giga, Procesorul stă și strigă. Placa video s-a prăjit, Dar modelul a ieșit!"*

## Ce este CodeGuard?
CodeGuard este o soluție dedicată platformelor de algoritmică și profesorilor, creată pentru a identifica rapid temele copiate, prin compararea automată a codului sursă și detectarea asemănărilor dintre soluții.

## Funcții
Aplicația pune la dispoziție o serie de endpoint-uri de API și un utilitar offline pentru a simplifica fluxul de lucru:
* Verifică similaritatea între două sau mai multe soluții (`/check_similarity`)
* Semnalizează soluțiile asemănătoare dintr-o temă de casă (`/check_homework`)
* Adaugă o soluție în baza de date și verifică probabilitatea de a nu fi originală (`/submit_and_check`)
* Permite unui profesor să verifice rapid similaritatea a mai multor soluții offline folosind utilitarul dedicat (`check_folder.exe`).

## Tehnologii folosite
Proiectul este scris în limbajul de programare **Python**.

### Partea de Inteligență Artificială (AI)
* **PyTorch**
* **Hugging Face Hub** - CodeBERT tokenizer, datasets

### Partea de Backend / API
* **Flask** - pentru a rula endpointurile web
* **MySQL** - pentru baza de date


## Instalare (Librării Necesare)
Dependințele necesare rulării proiectului pot fi instalate folosind `pip`:

```bash
pip install -r requirments.txt
```

Pachetele folosite includ: `mysql-connector-python`, `DateTime`, `regex`, `Flask`, `torch` și `transformers`.

## Utilizare

Pentru a porni API-ul rulati urmatoarea comanda din folderul principal al proiectului
```bash
python3 -m API.api
```

Pentru a rula check_folder pe alt sistem de operare decat Windows rulati urmatoarea comanda din folderul principal al proiectului
```bash
python3 -m OFFLINE.check_folder
```

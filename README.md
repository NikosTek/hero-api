# Secure Hero Missions API

REST API με FastAPI, SQLModel και SQLite για έναν οργανισμό υπερηρώων
που διαχειρίζεται χρήστες, ήρωες και αποστολές. 

## Τι κάνει

Auth: εγγραφή, σύνδεση, JWT access tokens, GET /auth/me

Heroes: CRUD με validation, name/power τουλάχιστον 3 χαρακτήρες,
level από 1 έως 100

Missions: CRUD, το hero_id πρέπει να αντιστοιχεί σε υπαρκτό ήρωα,
difficulty 1 έως 10, title τουλάχιστον 5 χαρακτήρες

Πρόσβαση ανά ρόλο:
GET endpoints είναι public, δεν χρειάζονται token.
POST/PATCH χρειάζονται συνδεδεμένο χρήστη.
DELETE μόνο για admins.

Business rules:
Δεν δημιουργείται αποστολή για ανύπαρκτο ήρωα, επιστρέφει 404.
Δεν διαγράφεται ήρωας που έχει ενεργές αποστολές.
Μόνο admin διαγράφει ήρωες και αποστολές.

status codes: 201 στη δημιουργία, 204 στη διαγραφή, 401/403/404/422
ανάλογα με την περίπτωση.

## Δομή project

hero_api/
  app/
    main.py            δημιουργία FastAPI app, include routers, lifespan
    db.py              engine, create_all, get_session
    security.py        password hashing και JWT
    models.py          SQLModel models και schemas create/update/response
    dependencies.py    get_current_user, get_current_admin
    routers/
      auth.py           /auth/register, /auth/login, /auth/me
      heroes.py         CRUD για /heroes
      missions.py       CRUD για /missions
  tests/
    test_api.py         pytest και TestClient, προσωρινή in-memory DB
  requirements.txt
  README.md

## Πώς τρέχει

python -m venv venv
source venv/Scripts/activate    (Windows, Git Bash)
venv\Scripts\Activate.ps1       (PowerShell)
source venv/bin/activate        (Linux/macOS)

pip install -r requirements.txt

uvicorn app.main:app --reload

Τρέχει στο http://127.0.0.1:8000. Docs στο /docs (Swagger).


## Endpoints

POST   /auth/register            Public          δημιουργία χρήστη
POST   /auth/login                Public          επιστρέφει access_token
GET    /auth/me                     Authenticated   ο τρέχων χρήστης

POST   /heroes                      Authenticated   δημιουργία ήρωα
GET    /heroes                      Public          λίστα ηρώων
GET    /heroes/{hero_id}            Public          ήρωας με βάση id
PATCH  /heroes/{hero_id}            Authenticated   μερική ενημέρωση
DELETE /heroes/{hero_id}            Admin           διαγραφή, αν δεν έχει ενεργές missions

POST   /missions                    Authenticated   δημιουργία αποστολής
GET    /missions                    Public          λίστα αποστολών
GET    /missions/{mission_id}       Public          αποστολή με βάση id
PATCH  /missions/{mission_id}       Authenticated   μερική ενημέρωση
DELETE /missions/{mission_id}       Admin           διαγραφή


## Tests

pytest -v

7 test cases: register, login, έλεγχος authentication, δημιουργία
ήρωα, ο κανόνας "αποστολή για ανύπαρκτο ήρωα επιστρέφει 404", έλεγχος
ρόλου στη διαγραφή, διαγραφή από admin. 


## Πιθανές βελτιώσεις

PostgreSQL και Alembic migrations αντί για SQLite και create_all.
Rate limiting στο /auth/login.

from unittest.mock import patch
from web_app import app

def test_uspesna_registracija():
    app.config["TESTING"] = True

    with patch("web_app.napravi_tabelu_korisnika"), \
         patch("web_app.registruj_korisnika", return_value=True):

        with app.test_client() as client:
            odgovor = client.post("/register", json={
                "korisnicko_ime": "test_korisnik",
                "lozinka": "test12345"
            })

        assert odgovor.status_code == 201
        assert odgovor.get_json()["odgovor"] == "Registracija je uspešna."

def test_postojeci_korisnik():
    app.config["TESTING"] = True

    with patch("web_app.napravi_tabelu_korisnika"), \
         patch("web_app.registruj_korisnika", return_value=False):

        with app.test_client() as client:
            odgovor = client.post("/register", json={
                "korisnicko_ime": "test_korisnik",
                "lozinka": "test12345"
            })

    assert odgovor.status_code == 409

def test_kratka_lozinka():
    app.config["TESTING"] = True

    with app.test_client() as client:
        odgovor = client.post("/register", json={
            "korisnicko_ime": "test_korisnik",
            "lozinka": "123"
        })

    assert odgovor.status_code == 400

def test_uspesna_prijava():
    app.config["TESTING"] = True

    with patch("web_app.prijavi_korisnika", return_value=1):
        with app.test_client() as client:
            odgovor = client.post("/login", json={
                "korisnicko_ime": "test_korisnik",
                "lozinka": "test12345"
            })

            assert odgovor.status_code == 200

            with client.session_transaction() as sesija:
                assert sesija["user_id"] == 1

def test_pogresna_lozinka():
    app.config["TESTING"] = True

    with patch("web_app.prijavi_korisnika", return_value=None):
        with app.test_client() as client:
            odgovor = client.post("/login", json={
                "korisnicko_ime": "test_korisnik",
                "lozinka": "pogresna123"
            })

        assert odgovor.status_code == 401

def test_odjava():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with client.session_transaction() as sesija:
            sesija["user_id"] = 1

        odgovor = client.post("/logout")

        assert odgovor.status_code == 200

        with client.session_transaction() as sesija:
            assert "user_id" not in sesija

def test_chat_bez_prijave():
    app.config["TESTING"] = True

    with app.test_client() as client:
        odgovor = client.post("/chat", json={
            "poruka": "Kakvo je vreme danas?"
        })

    assert odgovor.status_code == 401

def test_pocetna_bez_prijave():
    app.config["TESTING"] = True

    with app.test_client() as client:
        odgovor = client.get("/")

    assert odgovor.status_code == 302
    assert odgovor.headers["Location"].endswith("/login")

def test_login_rate_limiter():
    app.config["TESTING"] = True

    with patch("web_app.proveri_ogranicenje", return_value=False):
        with app.test_client() as client:
            odgovor = client.post("/login", json={
                "korisnicko_ime": "test_korisnik",
                "lozinka": "test12345"
            })

        assert odgovor.status_code == 429
        assert "greska" in odgovor.get_json()

def test_register_rate_limit():
    app.config["TESTING"] = True

    with patch("web_app.proveri_ogranicenje", return_value=False):
        with app.test_client() as client:
            odgovor = client.post("/register", json={
                "Korisnicko_ime": "test_korisnik",
                "lozinka": "test12345"
            })

    assert odgovor.status_code == 429
    assert "greska" in odgovor.get_json()
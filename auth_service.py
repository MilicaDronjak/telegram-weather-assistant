import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BAZA = Path(__file__).resolve().parent / "users.db"


def napravi_tabelu_korisnika():
    with sqlite3.connect(BAZA) as konekcija:
        konekcija.execute("""
            CREATE TABLE IF NOT EXISTS korisnici (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                korisnicko_ime TEXT NOT NULL UNIQUE,
                lozinka_hash TEXT NOT NULL
            )
        """)

def registruj_korisnika(korisnicko_ime, lozinka):
    lozinka_hash = generate_password_hash(lozinka)

    try:
        with sqlite3.connect(BAZA) as konekcija:
            konekcija.execute(
                """
                INSERT INTO korisnici (korisnicko_ime, lozinka_hash)
                VALUES (?, ?)
                """,
                (korisnicko_ime, lozinka_hash)
            )
        return True

    except sqlite3.IntegrityError:
        return False

def prijavi_korisnika(korisnicko_ime, lozinka):
    with sqlite3.connect(BAZA) as konekcija:
        korisnik = konekcija.execute(
           """
            SELECT id, lozinka_hash
            FROM korisnici
            WHERE korisnicko_ime = ?
            """,
            (korisnicko_ime,) 
        ).fetchone()

    if korisnik is None:
        return None

    korisnik_id, lozinka_hash = korisnik

    if check_password_hash(lozinka_hash, lozinka):
        return korisnik_id

    return None




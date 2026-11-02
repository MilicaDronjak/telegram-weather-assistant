import time
import sqlite3
from pathlib import Path

max_zahteva = 10
period = 60

BAZA = Path(__file__).resolve().parent / "rate_limiter.db"

def napravi_tabelu():
    with sqlite3.connect(BAZA) as konekcija:
        konekcija.execute("""
            CREATE TABLE IF NOT EXISTS zahtevi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                korisnik TEXT NOT NULL,
                vreme REAL NOT NULL
            )
        """)

def obrisi_stare_zahteve(konekcija, sada):
    konekcija.execute(
        "DELETE FROM zahtevi WHERE vreme <= ?",
        (sada - period,)
    )

def prebroj_zahteve(konekcija, korisnik):
    rezultat = konekcija.execute(
        "SELECT COUNT(*) FROM zahtevi WHERE korisnik = ?",
        (korisnik,)
    )

    return rezultat.fetchone()[0]

def sacuvaj_zahtev(konekcija, korisnik, sada):
    konekcija.execute(
        "INSERT INTO zahtevi (korisnik, vreme) VALUES (?, ?)",
        (korisnik, sada)
    )


def proveri_ogranicenje(korisnik, vreme_funkcija=time.time):
    sada = vreme_funkcija()

    with sqlite3.connect(BAZA, timeout=10) as konekcija:
        konekcija.execute("BEGIN IMMEDIATE")

        obrisi_stare_zahteve(konekcija, sada)

        broj_zahteva = prebroj_zahteve(konekcija, korisnik)

        if broj_zahteva >= max_zahteva:
            return False

        sacuvaj_zahtev(konekcija, korisnik, sada)

        return True

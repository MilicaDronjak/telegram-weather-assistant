import time
import sqlite3
from pathlib import Path

max_zahteva = 5
period = 120

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

def proveri_ogranicenje(korisnik):
    sada = time.time()

    with sqlite3.connect(BAZA, timeout=10) as konekcija:
        konekcija.execute("BEGIN IMMEDIATE")

        konekcija.execute(
            "DELETE FROM zahtevi WHERE vreme <= ?",
            (sada - period,)
        )

        rezultat = konekcija.execute(
            "SELECT COUNT(*) FROM zahtevi WHERE korisnik = ?",
            (korisnik,)
        )

        broj_zahteva = rezultat.fetchone()[0]

        if broj_zahteva >= max_zahteva:
            return False

        konekcija.execute(
            "INSERT INTO zahtevi (korisnik, vreme) VALUES (?, ?)",
            (korisnik, sada)
        )

        return True

napravi_tabelu()
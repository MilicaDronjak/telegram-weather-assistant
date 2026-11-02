import rate_limiter

def test_prvi_zahtev(tmp_path, monkeypatch):
    test_baza = tmp_path / "test_rate_limiter.db" #privremeni folder u kojem se cuva testrna baza

    monkeypatch.setattr(rate_limiter, "BAZA", test_baza)

    rate_limiter.napravi_tabelu()

    rezultat = rate_limiter.proveri_ogranicenje(
        "korisnik123",
        vreme_funkcija=lambda: 1000
    )

    assert rezultat is True

def test_ogranicenje_broja_zahteva(tmp_path, monkeypatch):
    test_baza = tmp_path / "test_rate_limiter.db"

    monkeypatch.setattr(rate_limiter, "BAZA", test_baza)

    rate_limiter.napravi_tabelu()

    for i in range(10):
        rezultat = rate_limiter.proveri_ogranicenje(
            "korisnik123",
            vreme_funkcija=lambda: 1000
        )

        assert rezultat is True


def test_istek_vremenskog_ogranicenja(tmp_path, monkeypatch):
    test_baza = tmp_path / "test_rate_limiter.db"

    monkeypatch.setattr(rate_limiter, "BAZA", test_baza)

    rate_limiter.napravi_tabelu()

    for i in range(10):
        rate_limiter.proveri_ogranicenje(
            "korisnik123",
            vreme_funkcija=lambda: 1000
        )

    rezultat = rate_limiter.proveri_ogranicenje(
        "korisnik123",
        vreme_funkcija=lambda: 1000
    )

    assert rezultat is False

    rezultat = rate_limiter.proveri_ogranicenje(
        "korisnik123",
        vreme_funkcija=lambda: 1060
    )

    assert rezultat is True


def test_razliciti_korisnici(tmp_path, monkeypatch):
    test_baza = tmp_path / "test_rate_limiter.db"

    monkeypatch.setattr(rate_limiter, "BAZA", test_baza)

    rate_limiter.napravi_tabelu()

    for i in range(10):
        rate_limiter.proveri_ogranicenje(
            "korisnik123",
            vreme_funkcija=lambda: 1000
        )

    rezultat_prvi = rate_limiter.proveri_ogranicenje(
        "korisnik123",
        vreme_funkcija=lambda: 1000
    )

    rezultat_drugi = rate_limiter.proveri_ogranicenje(
        "korisnik456",
        vreme_funkcija=lambda: 1000
    )

    assert rezultat_prvi is False
    assert rezultat_drugi is True

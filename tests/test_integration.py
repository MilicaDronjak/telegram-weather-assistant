from unittest.mock import patch
from web_app import app

def prijavi_test_korisnika(client):
    with client.session_transaction() as sesija:
        sesija["user_id"] = 1

def test_prazna_poruka():
    app.config["TESTING"] = True

    with patch("web_app.proveri_ogranicenje", return_value=True):
        with app.test_client() as client:
            prijavi_test_korisnika(client)

            odgovor = client.post(
                "/chat",
                json={"poruka": ""}
            )

    assert odgovor.status_code == 200
    assert odgovor.get_json()["odgovor"] == (
        "Unesi pitanje o vremenu ili kalendaru."
    )

def test_blokiran_zahtev():
    app.config["TESTING"] = True

    with patch("web_app.proveri_ogranicenje", return_value=False):
        with app.test_client() as client:
            prijavi_test_korisnika(client)

            odvogor = client.post(
                "/chat",
                json={"poruka": "Kakvo je vreme danas?"}
            )

    assert odvogor.status_code == 429
    assert odvogor.get_json()["odgovor"] == (
        "Poslali ste previše poruka. Pokušajte ponovo kasnije."
    )


def test_pregled_kalendara():
    app.config["TESTING"] = True

    namera = {
        "namera": "kalendar",
        "akcija": "pregled",
        "datum": "2026-10-31"
    }

    dogadjaji = [
        {"summary": "Sastanak"},
        {"summary": "Predavanje"}
    ]

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru", return_value=namera), \
         patch("web_app.pretvori_datum", return_value="2026-10-31"), \
         patch("web_app.povezi_kalendar"), \
         patch("web_app.dogadjaji_za_dan", return_value=dogadjaji):

        with app.test_client() as client:
            prijavi_test_korisnika(client)
            
            odgovor = client.post(
                "/chat",
                json={"poruka": "Šta imam u kalendaru sutra?"}
            )

    assert odgovor.status_code == 200
    assert "Sastanak" in odgovor.get_json()["odgovor"]
    assert "Predavanje" in odgovor.get_json()["odgovor"]

def test_dodavanje_dogadjaja_sa_potvrdom():
    app.config["TESTING"] = True

    namera = {
        "namera": "kalendar",
        "akcija": "dodavanje",
        "naziv": "Sastanak",
        "datum": "2026-11-05",
        "vreme": "10:00"
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru",return_value=namera), \
         patch("web_app.pretvori_datum", return_value="2026-11-05"), \
         patch("web_app.povezi_kalendar"), \
         patch("web_app.dodaj_dogadjaj") as mock_dodaj:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            prvi_odgovor = client.post(
                "/chat",
                json={"poruka": "Dodaj sastanal 5. novembra u 10"}
            )

            drugi_odgovor = client.post(
                "/chat",
                json={"poruka": "da"}
            )

    assert prvi_odgovor.status_code == 200
    assert "Da li želiš da dodam događaj" in prvi_odgovor.get_json()["odgovor"]

    assert drugi_odgovor.status_code == 200
    assert drugi_odgovor.get_json()["odgovor"] == (
        "Događaj je uspešno dodat u kalendar."
    )

    mock_dodaj.assert_called_once()

def test_otkazivanje_dodavanja_dogadjaja():
    app.config["TESTING"] = True

    namera = {
        "namera": "kalendar",
        "akcija": "dodavanje",
        "naziv": "Sastanak",
        "datum": "2026-11-05",
        "vreme": "10:00"
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru", return_value=namera), \
         patch("web_app.pretvori_datum", return_value="2026-11-05"), \
         patch("web_app.dodaj_dogadjaj") as mock_dodaj:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            prvi_odgovor = client.post(
                "/chat",
                json={"poruka": "Dodaj sastanak 5. novembra u 10"}
            )

            drugi_odgovor = client.post(
                "/chat",
                json={"poruka": "ne"}
            )

        assert prvi_odgovor.status_code == 200
        assert drugi_odgovor.status_code == 200

        assert drugi_odgovor.get_json()["odgovor"] == (
            "Dodavanje događaja je otkazano."
        )

        mock_dodaj.assert_not_called()

def test_neispravna_potvrda_dodavanja():
    app.config["TESTING"] = True

    namera = {
        "namera": "kalendar",
        "akcija": "dodavanje",
        "naziv": "Sastanak",
        "datum": "2026-11-05",
        "vreme": "10:00"
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru", return_value=namera), \
         patch("web_app.pretvori_datum", return_value="2026-11-05"), \
         patch("web_app.dodaj_dogadjaj") as mock_dodaj:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            client.post(
                "/chat",
                json={"poruka": "Dodaj sastanak 5. novembra u 10"}
            )

            odgovor = client.post(
                "/chat",
                json={"poruka": "možda"}
            )

        assert odgovor.status_code == 200
        assert odgovor.get_json()["odgovor"] == (
            "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
        )

        mock_dodaj.assert_not_called


def test_vremenska_prognoza():
    app.config["TESTING"] = True

    analiza = {
        "lokacija": "Novi Sad",
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("web_app.analiziraj_pitanje", return_value=analiza), \
         patch("web_app.preuzmi_prognozu",
               return_value="Prognoza za Novi Sad: 15°C.") as mock_prognoza:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            odgovor = client.post(
                "/chat",
                json={"poruka": "Kakvo će vreme biti sutra u Novom Sadu?"}
            )

    assert odgovor.status_code == 200
    assert odgovor.get_json()["odgovor"] == (
        "Prognoza za Novi Sad: 15°C."
    )

    mock_prognoza.assert_called_once_with(
        "Novi Sad", "2026-11-03", "dnevno", None
    )

def test_vremenska_prognoza_bez_lokacije():
    app.config["TESTING"] = True

    analiza = {
        "lokacija": None,
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru", return_value={"namera": "vreme"}), \
         patch("web_app.analiziraj_pitanje", return_value=analiza), \
         patch("web_app.preuzmi_prognozu") as mock_prognoza:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            odgovor = client.post(
                "/chat",
                json={"poruka": "Kakvo će vreme biti sutra?"}
            )

    assert odgovor.status_code == 200
    assert "grad" in odgovor.get_json()["odgovor"].lower()

    mock_prognoza.assert_not_called()


def test_nastavak_razgovora_za_prognozu():
    app.config["TESTING"] = True

    prva_analiza = {
        "lokacija": None,
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    druga_analiza = {
        "lokacija": "Novi Sad",
        "datum": None,
        "tip": "dnevno",
        "sat": None
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("web_app.analiziraj_pitanje",
               side_effect=[prva_analiza, druga_analiza]), \
         patch("web_app.preuzmi_prognozu",
               return_value="Prognoza za Novi Sad.") as mock_prognoza:

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            prvi_odgovor = client.post(
                "/chat",
                json={"poruka": "Kakvo će vreme biti sutra?"}
            )

            drugi_odgovor = client.post(
                "/chat",
                json={"poruka": "Novi Sad"}
            )

    assert prvi_odgovor.status_code == 200
    assert "grad" in prvi_odgovor.get_json()["odgovor"].lower()

    assert drugi_odgovor.status_code == 200
    assert drugi_odgovor.get_json()["odgovor"] == "Prognoza za Novi Sad."

    mock_prognoza.assert_called_once_with(
        "Novi Sad", "2026-11-03", "dnevno", None
    )


def test_brisanje_sesije_nakon_prognoze():
    app.config["TESTING"] = True

    analiza = {
        "lokacija": "Novi Sad",
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    with patch("web_app.proveri_ogranicenje", return_value=True), \
         patch("web_app.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("web_app.analiziraj_pitanje", return_value=analiza), \
         patch("web_app.preuzmi_prognozu",
               return_value="Prognoza za Novi Sad."):

        with app.test_client() as client:
            prijavi_test_korisnika(client)

            odgovor = client.post(
                "/chat",
                json={"poruka": "Kakvo je vreme sutra u Novom Sadu?"}
            )

            with client.session_transaction() as sesija:
                assert "lokacija" not in sesija
                assert "datum" not in sesija
                assert "tip" not in sesija
                assert "sat" not in sesija

    assert odgovor.status_code == 200

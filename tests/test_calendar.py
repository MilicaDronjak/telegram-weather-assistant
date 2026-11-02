from calendar_service import( 
    pretvori_datum,
    dogadjaji_za_dan,
    proveri_slobodan_termin,
    dodaj_dogadjaj,
    izmeni_dogadjaj,
    obrisi_dogadjaj
    )
from datetime import date, datetime ,timedelta
from unittest.mock import MagicMock

def test_pretvori_datum_sutra():
    ocekivani_datum = (date.today() + timedelta(days=1)).isoformat()

    rezultat = pretvori_datum("sutra")

    assert rezultat == ocekivani_datum

def test_pretvori_datum_danas():
    ocekivani_datum = date.today().isoformat()

    rezultat = pretvori_datum("danas")

    assert rezultat == ocekivani_datum

def test_pretvori_dan_u_nedelji():
    danas = date.today()

    razlika = (0 - danas.weekday()) % 7

    if razlika == 0:
        razlika = 7

        ocekivani_datum = (danas + timedelta(days=razlika)).isoformat()

        rezultat = pretvori_datum("ponedeljak")

        assert rezultat == ocekivani_datum


def test_dogadjaji_za_dan():
    mock_service = MagicMock()

    mock_service.events().list().execute.return_value = {
        "items": [
            {
                "id": "123",
                "summary": "Sastanak"
            },
            {
                "id": "456",
                "summary": "Predavanje"
            }
        ]
    }

    rezultat = dogadjaji_za_dan(
        mock_service, "2026-10-30"
    )

    assert len(rezultat) == 2
    assert rezultat[0]["summary"] == "Sastanak"
    assert rezultat[1]["summary"] == "Predavanje"

def test_slobodan_termin():
    mock_service = MagicMock()

    mock_service.events().list().execute.return_value = {
        "items": []
    }

    pocetak = datetime.fromisoformat("2026-11-02T10:00:00")
    kraj = datetime.fromisoformat("2026-11-02T11:00:00")

    rezultat = proveri_slobodan_termin(
        mock_service, pocetak, kraj
    )

    assert rezultat is True

def test_zauzet_termin():
    mock_service = MagicMock()

    mock_service.events().list().execute.return_value = {
        "items": [
            {
                "id": "123",
                "summary": "Sastanak",
                "status": "confirmed"
            }
        ]
    }

    pocetak = datetime.fromisoformat("2026-11-02T10:00:00")
    kraj = datetime.fromisoformat("2026-11-02T11:00:00")

    rezultat = proveri_slobodan_termin(
        mock_service, pocetak, kraj
    )

    assert rezultat is False


def test_dodaj_dogadjaj():
    mock_service = MagicMock()

    mock_service.events().insert().execute.return_value = {
        "id": "123",
        "summary": "Sastanak"
    }

    rezultat = dodaj_dogadjaj(
        mock_service,
        "Sastanak",
        "2026-11-02",
        "10:00"
    )

    assert rezultat["id"] == "123"
    assert rezultat["summary"] == "Sastanak"

    poslati_podaci = mock_service.events().insert.call_args.kwargs

    assert poslati_podaci["calendarId"] == "primary"
    assert poslati_podaci["body"]["summary"] == "Sastanak"
    assert poslati_podaci["body"]["start"]["dateTime"][11:16] == "10:00"
    assert poslati_podaci["body"]["end"]["dateTime"][11:16] == "11:00"


def test_izmeni_dogadjaj():
    mock_service = MagicMock()

    mock_service.events().patch.return_value.execute.return_value = {
        "id": "123",
        "summary": "Novi sastanak"
    }

    novi_podaci = {
        "summary": "Novi sastanak"
    }

    rezultat = izmeni_dogadjaj(
        mock_service,
        "123",
        novi_podaci
    )

    assert rezultat["id"] == "123"
    assert rezultat["summary"] == "Novi sastanak"

    mock_service.events().patch.assert_called_once_with(
        calendarId="primary",
        eventId="123",
        body=novi_podaci
    )

def test_obrisi_dogadjaj():
    mock_service = MagicMock()

    obrisi_dogadjaj(mock_service, "123")

    mock_service.events().delete.assert_called_once_with(
        calendarId="primary",
        eventId="123"
    )

    mock_service.events().delete.return_value.execute.assert_called_once()
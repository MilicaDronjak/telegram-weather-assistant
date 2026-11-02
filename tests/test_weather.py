from weather_service import (
    proveri_nedostajuce_podatke,
    spoji_podatke,
    analiziraj_pitanje,
    preuzmi_prognozu,
)
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
import pytest
import json

def test_nedostaje_lokacija():
    rezultat = proveri_nedostajuce_podatke(
        None, "sutra", "dnevna", None
    )

    assert rezultat == "Za koji grad želiš vremensku prognozu?"

def test_nedostaje_datum():
    rezultat = proveri_nedostajuce_podatke(
        "Novi Sad", None, "dnevna", None
    )

    assert rezultat == "Za koji datum želiš vremensku prognozu?"

def test_nedostaje_sat():
    rezultat = proveri_nedostajuce_podatke(
        "Novi Sad", "sutra", "satna_temperatura", None
    )

    assert rezultat == "Za koji sat želiš vremensku prognozu?"

def test_svi_podaci_uneti():
    rezultat = proveri_nedostajuce_podatke(
        "Novi Sad", "sutra", "satna_temperatura", 15
    )

    assert rezultat is None

def test_spoji_podatke():
    stari_podaci = {
        "lokacija": None,
        "datum": "sutra",
        "tip": "dnevno",
        "sat": None,
    }

    novi_podaci = {
        "lokacija": "Novi Sad",
        "datum": None,
        "tip": None,
        "sat": None,
    }


def test_spoji_podatke_satna_temperatura():
    stari_podaci = {
        "lokacija": None,
        "datum": "sutra",
        "tip": "satna_temperatura",
        "sat": 15
    }

    novi_podaci = {
        "lokacija": "Novi Sad",
        "datum": None,
        "tip": "dnevno",
        "sat": None
    }

    rezultat = spoji_podatke(novi_podaci, stari_podaci)

    assert rezultat["lokacija"] == "Novi Sad"
    assert rezultat["datum"] == "sutra"
    assert rezultat["tip"] == "satna_temperatura"
    assert rezultat["sat"] == 15

#unit test za LLM
def test_analiziraj_pitanje():
    mock_klijent = MagicMock()

    mock_klijent.chat.completions.create.return_value.choices[
        0
    ].message.content = (
        '{"lokacija": "Novi Sad", '
        '"datum": "2026-10-30", '
        '"tip": "dnevno", '
        '"sat": null}'
    )

    rezultat = analiziraj_pitanje(
        "Kakvo će vreme biti sutra u Novom Sadu?",
        klijent=mock_klijent
    )

    assert rezultat["lokacija"] == "Novi Sad"
    assert rezultat["datum"] == "2026-10-30"
    assert rezultat["tip"] == "dnevno"
    assert rezultat["sat"] is None

def test_neispravan_datum():
    rezultat = preuzmi_prognozu(
        "Novi Sad", "pogresan-datum", "dnevno"
    )

    assert rezultat == "Datum nije ispravan. Pokušaj sa formatom YYYY-MM-DD."

def test_datum_u_proslosti():
    rezultat = preuzmi_prognozu(
        "Novi Sad", "2020-01-01", "dnevno"
    )

    assert rezultat == "Ne mogu da prikažem prognozu za datum koji je prošao."

def test_datum_predaleko():
    rezultat = preuzmi_prognozu(
        "Novi Sad", "2030-01-15", "dnevno"
    )

    assert rezultat == (
        "Prognoza za taj datum još nije dostupna. "
        "Mogu da prikažem prognozu za narednih 16 dana."
    )

def test_trenutna_prognoza():
    with patch("weather_service.pronadji_grad") as mock_grad, \
        patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        mock_podaci.return_value = {
            "current": {
                "temperature_2m": 15,
                "apparent_temperature": 13,
                "relative_humidity_2m": 65,
                "precipitation": 0
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", None, "trenutno"
        )

        assert "Temperatura: 15°C" in rezultat
        assert "Subjektivni osećaj: 13°C" in rezultat
        assert "Vlažnost vazduha: 65%" in rezultat
        assert "Padavine: 0 mm" in rezultat


def test_dnevna_prognoza():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        mock_podaci.return_value = {
            "daily": {
                "temperature_2m_max": [20],
                "temperature_2m_min": [10],
                "precipitation_probability_max": [30]
            }
        }

        datum = (date.today() + timedelta(days=1)).isoformat()

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "dnevno"
        )

        assert "Maksimalna temperatura: 20°C" in rezultat
        assert "Minimalna temperatura: 10°C" in rezultat
        assert "Verovatnoca padavina: 30%" in rezultat

def test_satna_prognoza():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        datum = (date.today() + timedelta(days=1)).isoformat()

        mock_podaci.return_value = {
            "hourly": {
                "time": [
                    f"{datum}T14:00",
                    f"{datum}T15:00",
                    f"{datum}T16:00"
                ],
                "temperature_2m": [18, 20, 17]
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "satna_temperatura", 15
        )

        assert "Vreme: 15:00" in rezultat
        assert "Temperatura: 20°C" in rezultat   


def test_dnevne_padavine():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        mock_podaci.return_value = {
            "daily": {
                "precipitation_probability_max": [40],
                "precipitation_sum": [2.5]
            }
        }

        datum = (date.today() + timedelta(days=1)).isoformat()

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "kisa"
        )

        assert "Najveća verovatnoća padavina: 40%" in rezultat
        assert "Očekivana ukupna količina padavina: 2.5 mm" in rezultat


def test_satne_padavine():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        datum = (date.today() + timedelta(days=1)).isoformat()

        mock_podaci.return_value = {
            "hourly": {
                "time": [
                    f"{datum}T14:00",
                    f"{datum}T15:00",
                    f"{datum}T16:00"
                ],
                "precipitation_probability": [10, 60, 20],
                "precipitation": [0.0, 1.5, 0.2]
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "kisa", 15
        )

        assert "Vreme: 15:00" in rezultat
        assert "Verovatnoća padavina: 60%" in rezultat
        assert "Očekivana količina padavina: 1.5 mm" in rezultat


def test_nepoznat_grad():
    with patch("weather_service.pronadji_grad") as mock_grad:
        mock_grad.return_value = None

        datum = (date.today() + timedelta(days=1)).isoformat()

        rezultat = preuzmi_prognozu(
            "GGGGG", datum, "dnevno"
        )

        assert rezultat == "Nisam uspeo da pronađem taj grad"


def test_nedostupna_satna_prognoza():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        datum = (date.today() + timedelta(days=1)).isoformat()

        mock_podaci.return_value = {
            "hourly": {
                "time": [
                    f"{datum}T14:00",
                    f"{datum}T15:00"
                ],
                "temperature_2m": [18, 20]
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "satna_temperatura", 18
        )

        assert rezultat == "Prognoza za traženi sat nije dostupna."


def test_nedostupne_satne_padavine():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        datum = (date.today() + timedelta(days=1)).isoformat()

        mock_podaci.return_value = {
            "hourly": {
                "time": [
                    f"{datum}T14:00",
                    f"{datum}T15:00"
                ],
                "precipitation_probability": [10, 60],
                "precipitation": [0.0, 1.5]
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "kisa", 18
        )

        assert rezultat == "Prognoza padavina za traženi sat nije dostupna."



def test_satna_prognoza_bez_sata():
    with patch("weather_service.pronadji_grad") as mock_grad, \
         patch("weather_service.preuzmi_podatke") as mock_podaci:

        mock_grad.return_value = (45.2671, 19.8335)

        datum = (date.today() + timedelta(days=1)).isoformat()

        mock_podaci.return_value = {
            "hourly": {
                "time": [f"{datum}T15:00"],
                "temperature_2m": [20]
            }
        }

        rezultat = preuzmi_prognozu(
            "Novi Sad", datum, "satna_temperatura"
        )

        assert rezultat == "Napiši za koliko sati želiš prognozu."


#LLM testovi
def test_llm_neispravan_json():
    mock_klijent = MagicMock()

    mock_klijent.chat.completions.create.return_value.choices[
        0
    ].message.content = "Ovo nije JSON"

    with pytest.raises(json.JSONDecodeError):
        analiziraj_pitanje(
            "Kakvo je vreme sutra u Novom Sadu?",
            klijent=mock_klijent
        )


def test_llm_nepotpun_json():
    mock_klijent = MagicMock()

    mock_klijent.chat.completions.create.return_value.choices[
        0
    ].message.content = '{"lokacija": "Novi Sad", "datum": "2026-11-03"}'

    rezultat = analiziraj_pitanje(
        "Kakvo je vreme sutra u Novom Sadu?",
        klijent=mock_klijent
    )

    assert rezultat["lokacija"] == "Novi Sad"
    assert rezultat["datum"] == "2026-11-03"
    assert "tip" not in rezultat
    assert "sat" not in rezultat
    

def test_llm_greska_api_ja():
    mock_klijent = MagicMock()

    mock_klijent.chat.completions.create.side_effect = Exception(
        "Groq API nije dostupan"
    )

    with pytest.raises(Exception, match="Groq API nije dostupan"):
        analiziraj_pitanje(
            "Kakvo je vreme sutra u Novom Sadu?",
            klijent=mock_klijent
        )





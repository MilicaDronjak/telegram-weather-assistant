import os
import json
import requests

from datetime import date, timedelta
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API kljuc nije pronadjen u .env fajlu!")

groq_client = Groq(api_key=GROQ_API_KEY)

def analiziraj_pitanje(poruka):
    danas=date.today().isoformat()

    odgovor=groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ti analiziras pitanja o vremenskoj prognozi. "
                    f"Danasnji datum je {danas}. "

                    "Iz poruke izdvoji lokaciju, datum, tip i sat. "
                    "Lokaciju vrati u nominativu, npr. "
                    "'u Novom Sadu' -> 'Novi Sad', "
                    "'u Beogradu' -> 'Beograd'. "
                
                    "Tip moze biti: 'trenutno', 'dnevno', 'satna_temperatura' ili 'kisa'. "
                
                    "Ako korisnik pita za vreme sada ili trenutno, tip je 'trenutno', a datum je danas. "
                
                    "Ako pita za prognozu za ceo dan, ukljucujuci koliko ce stepeni biti danas, tip je 'dnevno'. "
                
                    "Ako pita za temperaturu u tacnom satu, tip je 'satna_temperatura'. "
                    "Ako pita za temperaturu ujutru, popodne ili veceras bez tacnog sata, tip je 'satna_temperatura', a sat je null. "
                
                    "Ako pita za kisu ili padavine, tip je 'kisa', cak i kada navede tacan sat. "
                
                    "Ako pita za danas, datum je danas. "
                    "Ako pita za sutra, datum je sutra. "
                    "Ako navede dan u nedelji, izracunaj odgovarajuci datum na osnovu danasnjeg datuma. "
                
                    "Ako tacan sat nije naveden, vrati null za sat. "
                    "Ako lokacija ili datum nisu navedeni, vrati null za njih. "
                    "Za ostala pitanja o prognozi tip je 'dnevno'. "
                
                    "Vrati samo JSON sa poljima 'lokacija', 'datum', 'tip' i 'sat'. "
                    "Datum mora biti YYYY-MM-DD, a sat broj od 0 do 23 ili null. "
                    "Ne izmisljaj podatke."
                )
            },
            {
                "role": "user",
                "content": poruka
            }
        ],
        response_format={"type": "json_object"}
    )

    podaci=json.loads(odgovor.choices[0].message.content)

    return podaci

def preuzmi_prognozu(lokacija, datum, tip, sat=None): 
    
    if tip != "trenutno":
        try:
            trazeni_datum = date.fromisoformat(datum)
        except (ValueError, TypeError):
            return "Datum nije ispravan. Pokusaj sa formatom YYYY-MM-DD."

        danas = date.today()
        poslednji_datum = danas + timedelta(days=15)

        if trazeni_datum < danas:
            return "Ne mogu da prikazem prognozu za datum koji je prosao."

        if trazeni_datum > poslednji_datum:
            return (
                "Prognoza za taj datum jos nije dostupna. "
                "Mogu da prikazem prognozu za narednih 16 dana."
            )

    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_odgovor = requests.get(
        geo_url,
        params={
            "name": lokacija,
            "count": 1,
            "language": "sr"
        },
        timeout=10
    )
    geo_odgovor.raise_for_status()

    gradovi = geo_odgovor.json().get("results", [])

    if not gradovi:
        return "Nisam uspeo da pronadjem taj grad."

    latitude = gradovi[0]["latitude"]
    longitude = gradovi[0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    if tip == "trenutno":
        parametri = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation",
            "timezone": "auto"
        }

        odgovor = requests.get(
            weather_url,
            params=parametri,
            timeout=10
        )
        odgovor.raise_for_status()

        trenutno = odgovor.json()["current"]

        temperatura = trenutno["temperature_2m"]
        osecaj = trenutno["apparent_temperature"]
        vlaznost = trenutno["relative_humidity_2m"]
        padavine = trenutno["precipitation"]

        return (
            f"Trenutno vreme – {lokacija}\n"
            f"Temperatura: {temperatura}°C\n"
            f"Subjektivni osećaj: {osecaj}°C\n"
            f"Vlažnost vazduha: {vlaznost}%\n"
            f"Padavine: {padavine} mm"
        )
    elif tip == "satna_temperatura":
        parametri = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "timezone": "auto",
            "start_date": datum,
            "end_date": datum
        }

        odgovor = requests.get(
            weather_url,
            params=parametri,
            timeout=10
        )
        odgovor.raise_for_status()

        satni = odgovor.json()["hourly"]
        if sat is None:
            return "Napiši za koliko sati želiš prognozu."

        trazeni_sat = f"{datum}T{sat:02d}:00"

        if trazeni_sat not in satni["time"]:
            return "Prognoza za trazeni sat nije dostupna."

        indeks = satni["time"].index(trazeni_sat)
        temperatura = satni["temperature_2m"][indeks]


        return (
            f"Prognoza po satima – {lokacija}\n"
            f"Datum: {datum}\n"
            f"Vreme: {sat:02d}:00\n"
            f"Temperatura: {temperatura}°C"
        )
    
    elif tip == "kisa":
        if sat is not None:
            parametri = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "precipitation_probability,precipitation",
                "timezone": "auto",
                "start_date": datum,
                "end_date": datum
            }

            odgovor = requests.get(
                weather_url,
                params=parametri,
                timeout=10
            )
            odgovor.raise_for_status()

            satni = odgovor.json()["hourly"]

            trazeni_sat = f"{datum}T{sat:02d}:00"

            if trazeni_sat not in satni["time"]:
                return "Prognoza padavina za trazeni sat nije dostupna."

            indeks = satni["time"].index(trazeni_sat)

            verovatnoca = satni["precipitation_probability"][indeks]
            kolicina = satni["precipitation"][indeks]

            return (
                f"Prognoza padavina po satima – {lokacija}\n"
                f"Datum: {datum}\n"
                f"Vreme: {sat:02d}:00\n"
                f"Verovatnoća padavina: {verovatnoca}%\n"
                f"Očekivana količina padavina: {kolicina} mm"
            )

        else:
            parametri = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": "precipitation_probability_max,precipitation_sum",
                "timezone": "auto",
                "start_date": datum,
                "end_date": datum
            }

            odgovor = requests.get(
                weather_url,
                params=parametri,
                timeout=10
            )
            odgovor.raise_for_status()

            dnevni = odgovor.json()["daily"]

            verovatnoca = dnevni["precipitation_probability_max"][0]
            kolicina = dnevni["precipitation_sum"][0]

            return (
                f"Prognoza padavina – {lokacija}\n"
                f"Datum: {datum}\n"
                f"Najveća verovatnoća padavina: {verovatnoca}%\n"
                f"Očekivana ukupna količina padavina: {kolicina} mm"
            )
        
    else:
        parametri = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "start_date": datum,
            "end_date": datum
        }

        odgovor = requests.get(
            weather_url,
            params=parametri,
            timeout=10
        )
        odgovor.raise_for_status()

        dnevni = odgovor.json()["daily"]

        max_temp = dnevni["temperature_2m_max"][0]
        min_temp = dnevni["temperature_2m_min"][0]
        kisa = dnevni["precipitation_probability_max"][0]

        return (
            f"Vremenska prognoza – {lokacija}\n"
            f"Datum: {datum}\n"
            f"Maksimalna temperatura: {max_temp}°C\n"
            f"Minimalna temperatura: {min_temp}°C\n"
            f"Verovatnoca padavina: {kisa}%"
        )

            
        


        

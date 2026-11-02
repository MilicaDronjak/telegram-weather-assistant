import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone
from datetime import timedelta
from intent_service import prepoznaj_nameru


SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def povezi_kalendar():
    credentials = None #cuvamo podatke za autorizaciju

    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    service = build("calendar", "v3", credentials=credentials)

    return service

def prikazi_dogadjaje(service):
    sada = datetime.now(timezone.utc).isoformat()

    dogadjaji = service.events().list(
        calendarId="primary",
        timeMin=sada,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return dogadjaji.get("items", [])

def dogadjaji_za_dan(service, datum): #prima service (pristup google calendar api-ju)
    pocetak = datetime.fromisoformat(datum).astimezone()
    kraj = pocetak + timedelta(days=1)

    rezultat = service.events().list(
        calendarId="primary",
        timeMin=pocetak.isoformat(),
        timeMax=kraj.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    return rezultat.get("items", [])

def pretvori_datum(datum):
    danas = datetime.now().date()

    if datum == "danas":
        return danas.isoformat()

    elif datum == "sutra":
        return (danas + timedelta(days=1)).isoformat()

    dani = {
        "ponedeljak": 0,
        "utorak": 1,
        "sreda": 2,
        "četvrtak": 3,
        "petak": 4,
        "subota": 5,
        "nedelja": 6
    }

    if datum in dani:
        trazeni_dan = dani[datum]
        razlika = (trazeni_dan - danas.weekday()) % 7

        if razlika == 0:
            razlika = 7

        return (danas + timedelta(days=razlika)).isoformat()

    return datum

def prikazi_vreme_dogadjaja(dogadjaj):
    pocetak = dogadjaj.get("start", {})
    kraj = dogadjaj.get("end", {})

    if "dateTime" in pocetak and "dateTime" in kraj:
        vreme_pocetka = datetime.fromisoformat(
            pocetak["dateTime"]
        ).strftime("%H:%M")

        vreme_kraja = datetime.fromisoformat(
            kraj["dateTime"]
        ).strftime("%H:%M")

        return f"{vreme_pocetka} - {vreme_kraja}"

    return "Ceo dan"

def proveri_slobodan_termin(service, pocetak, kraj):
    rezultat = service.events().list(
        calendarId="primary",
        timeMin=pocetak.isoformat(),
        timeMax=kraj.isoformat(),
        singleEvents=True
    ).execute()

    dogadjaji = rezultat.get("items", [])

    return len(dogadjaji) == 0

def dodaj_dogadjaj(service, naziv, datum, vreme, trajanje=60):
    pocetak = datetime.fromisoformat(f"{datum}T{vreme}").astimezone()
    kraj = pocetak + timedelta(minutes=trajanje)

    dogadjaj = {
        "summary": naziv,
        "start": {
            "dateTime": pocetak.isoformat()
        },
        "end": {
            "dateTime": kraj.isoformat()
        }
    }

    rezultat = service.events().insert(
        calendarId="primary",
        body=dogadjaj
    ).execute()

    return rezultat

def izmeni_dogadjaj(service, event_id, novi_podaci):
    rezultat = service.events().patch(
        calendarId="primary",
        eventId=event_id,
        body=novi_podaci
    ).execute()

    return rezultat

def obrisi_dogadjaj(service, event_id):
    service.events().delete(
        calendarId="primary",
        eventId=event_id
    ).execute()

def pronadji_dogadjaje(service, naziv):
    rezultat = service.events().list(
        calendarId="primary",
        q=naziv, #pretraga u kalendaru
        singleEvents=True,
        maxResults=50
    ).execute()

    return rezultat.get("items", [])

def pronadji_tacan_dogadjaj(service, naziv, datum, vreme):
    dogadjaji = pronadji_dogadjaje(service, naziv)

    pronadjeni = []

    for dogadjaj in dogadjaji:
        pocetak = dogadjaj.get("start", {})

        if "dateTime" not in pocetak:
            continue

        datum_vreme = datetime.fromisoformat(
            pocetak["dateTime"]
        ).astimezone()

        datum_dogadjaja = datum_vreme.date().isoformat()
        vreme_dogadjaja = datum_vreme.strftime("%H:%M")

        if (
            dogadjaj.get("summary", "").casefold() == naziv.casefold()
            and datum_dogadjaja == datum
            and vreme_dogadjaja == vreme
        ):
            pronadjeni.append(dogadjaj)

    return pronadjeni
    
if __name__ == "__main__":
    service = povezi_kalendar()

    dogadjaji = pronadji_tacan_dogadjaj(
        service, 
        "test događaj",
        "2026-10-27",
        "16:00"
    )

    print ("Broj pronađenih događaja:", len(dogadjaji))

    for dogadjaj in dogadjaji:
        print("Naziv:", dogadjaj.get("summary"))
        print("ID:", dogadjaj.get("id"))
        print("Početak:", dogadjaj.get("start"))
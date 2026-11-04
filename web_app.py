import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect
from weather_service import analiziraj_pitanje, preuzmi_prognozu, proveri_nedostajuce_podatke, spoji_podatke
from rate_limiter import proveri_ogranicenje
from intent_service import prepoznaj_nameru
from calendar_service import (
    povezi_kalendar,
    dogadjaji_za_dan,
    pretvori_datum,
    proveri_slobodan_termin,
    dodaj_dogadjaj,
    pronadji_tacan_dogadjaj,
    izmeni_dogadjaj,
    obrisi_dogadjaj
)
from auth_service import napravi_tabelu_korisnika, registruj_korisnika, prijavi_korisnika

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config["SESSION_COOKIE_HTTPONLY"] = True #sprecava direktno citanje sesijskih kolacica
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" #ogranicava slanje kolacica uz zahteve sa drugih sajtova i smanjuje rizik od CSRF napada

@app.route("/")
def pocetna():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login_stranica():
    if "user_id" in session:
        return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET"])
def registracija_stranica():
    if "user_id" in session:
        return redirect("/")
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def registracija():
    korisnik = f"register:{request.remote_addr}"

    if not proveri_ogranicenje(korisnik):
        return jsonify({
            "greska": "Previše pokušaja registracije. Pokušajte ponovo za minut."
        }), 429
    
    podaci = request.get_json(silent=True) or {}

    korisnicko_ime = podaci.get("korisnicko_ime", "").strip()
    lozinka = podaci.get("lozinka", "")

    if not korisnicko_ime or len(lozinka) < 8:
        return jsonify({
            "greska": "Unesite korisničko ime i lozinku od najmanje 8 karaktera."
        }), 400

    napravi_tabelu_korisnika()

    uspeh = registruj_korisnika(korisnicko_ime, lozinka)

    if not uspeh:
        return jsonify({
            "greska": "Korisničko ime već postoji."
        }), 409

    return jsonify({
        "odgovor": "Registracija je uspešna."
    }), 201

@app.route("/login", methods=["POST"])
def login():
    korisnik = f"login:{request.remote_addr}"

    if not proveri_ogranicenje(korisnik):
        return jsonify ({
            "greska": "Previše pokušaja prijave. Pokušajte ponovo za koji minut."
        }), 429

    podaci = request.get_json(silent=True) or {}

    korisnicko_ime = podaci.get("korisnicko_ime", "").strip()
    lozinka = podaci.get("lozinka", "")

    if not korisnicko_ime or not lozinka:
        return jsonify({
            "greska": "Unesite korisničko ime i lozinku."
        }), 400

    korisnik_id = prijavi_korisnika(korisnicko_ime, lozinka)

    if korisnik_id is None:
        return jsonify({
            "greska": "Pogrešno korisničko ime ili lozinka."
        }), 401

    session.clear()
    session["user_id"] = korisnik_id

    return jsonify({
        "odgovor": "Uspešno ste se prijavili."
    }), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "odgovor": "Uspešno ste se odjavili."
    }), 200

def sacuvaj_podatke(lokacija, datum, tip, sat):
    session["lokacija"] = lokacija
    session["datum"] = datum
    session["tip"] = tip
    session["sat"] = sat

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({
            "greska": "Morate biti prijavljeni da biste koristili chat."
        }), 401
    try:
        korisnik = f"web:{request.remote_addr}"

        dozvoljeno = proveri_ogranicenje(korisnik)

        if not dozvoljeno:
            return jsonify ({
                "odgovor": "Poslali ste previše poruka. Pokušajte ponovo kasnije."
                }), 429

        podaci = request.get_json()
        poruka = podaci.get("poruka", "").strip()
        
        # 1. Obrada potvrda za kalendar
        #potvrda za brisanje dogadjaja
        if session.get("ceka_potvrdu_brisanja"):
            odgovor_korisnika = poruka.strip().lower()

            if odgovor_korisnika in ["da", "potvrdi"]:
                podaci_brisanja = session["brisanje_dogadjaja"]

                try:
                    service = povezi_kalendar()

                    obrisi_dogadjaj(
                        service,
                        podaci_brisanja["event_id"]
                    )

                    return jsonify ({
                        "odgovor": "Događaj je uspešno obrisan iz kalendara."
                    })

                except Exception as e:
                    print("Greška pri brisanju događaja:", e)

                    return jsonify({
                        "odgovor": "Brisanje događaja nije uspelo."
                    })

                finally:
                    session.pop("ceka_potvrdu_brisanja", None)
                    session.pop("brisanje_dogadjaja", None)

            if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
                session.pop("ceka_potvrdu_brisanja", None)
                session.pop("brisanje_dogadjaja", None)

                return jsonify({
                    "odgovor": "Brisanje događaja je otkazano."
                })

            return jsonify({
                "odgovor": "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
            })

        #potvrda za izmenu dogadjaja
        if session.get("ceka_potvrdu_izmene"):

            odgovor_korisnika = poruka.strip().lower()

            if odgovor_korisnika in ["da", "potvrdi"]:
                podaci = session["izmena_dogadjaja"]

                try:
                    novi_pocetak = datetime.fromisoformat(
                        f"{podaci['novi_datum']}T{podaci['novo_vreme']}"
                    ).astimezone()

                    trajanje = timedelta(
                        seconds=podaci["trajanje_sekunde"]
                    )

                    novi_kraj = novi_pocetak + trajanje

                    novi_podaci = {
                        "start": {
                            "dateTime": novi_pocetak.isoformat()
                        },
                        "end": {
                            "dateTime": novi_kraj.isoformat()
                        }
                    }

                    service = povezi_kalendar()

                    izmeni_dogadjaj(
                        service,
                        podaci["event_id"],
                        novi_podaci
                    )

                    return jsonify({
                        "odgovor": "Događaj je uspešno izmenjen."
                    })

                except Exception as e:
                    print("Greška pri izmeni događaja:", e)

                    return jsonify({
                        "odgovor": "Nije uspela izmena događaja."
                    })

                finally:
                    session.pop("ceka_potvrdu_izmene", None)
                    session.pop("izmena_dogadjaja", None)

            if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
                session.pop("ceka_potvrdu_izmene", None)
                session.pop("izmena_dogadjaja", None)

                return jsonify({
                    "odgovor": "Izmena događaja je otkazana."
                })

            return jsonify({
                "odgovor": "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
            })

        #potvrda za dodavanje dogadjaja
        if session.get("ceka_potvrdu_dogadjaja"):

            odgovor_korisnika = poruka.lower()

            if odgovor_korisnika in ["da", "potvrdi"]:
                podaci_dogadjaja = session["novi_dogadjaj"]

                service = povezi_kalendar()

                dodaj_dogadjaj(
                    service,
                    podaci_dogadjaja["naziv"],
                    podaci_dogadjaja["datum"],
                    podaci_dogadjaja["vreme"]
                )

                session.pop("ceka_potvrdu_dogadjaja", None)
                session.pop("novi_dogadjaj", None)

                return jsonify({
                    "odgovor": "Događaj je uspešno dodat u kalendar."
                })

            if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
                session.pop("ceka_potvrdu_dogadjaja", None)
                session.pop("novi_dogadjaj", None)

                return jsonify({
                    "odgovor": "Dodavanje događaja je otkazano."
                })

            return jsonify({
                "odgovor": "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
            })

        if not poruka:
            return jsonify({"odgovor": "Unesi pitanje o vremenu ili kalendaru."})

        namera = prepoznaj_nameru(poruka)

        # 2. Obrada novih zahteva za kalendar
        if namera["namera"] == "kalendar":

            # Pregled događaja
            if namera["akcija"] == "pregled":

                if namera["datum"] is None:
                    return jsonify({
                        "odgovor": "Za koji datum želiš da proverim kalendar?"
                    })

                datum = pretvori_datum(namera["datum"])

                service = povezi_kalendar()
                dogadjaji = dogadjaji_za_dan(service, datum)

                if dogadjaji:
                    odgovor = f"Događaji za {datum}:\n"

                    for dogadjaj in dogadjaji:
                        naziv = dogadjaj.get("summary", "Bez naziva")
                        odgovor += f"- {naziv}\n"
                else:
                    odgovor = "Nema događaja za taj dan."

                return jsonify({"odgovor": odgovor})

            # Provera slobodnog termina
            if namera["akcija"] == "provera_termina":

                if not all([
                    namera.get("datum"),
                    namera.get("vreme"),
                    namera.get("vreme_kraja")
                ]):
                    return jsonify({
                        "odgovor": "Navedi datum, početak i kraj termina koji želiš da proverim."
                    })

                datum = pretvori_datum(namera["datum"])

                pocetak = datetime.fromisoformat(
                    f"{datum}T{namera['vreme']}"
                ).astimezone()

                kraj = datetime.fromisoformat(
                    f"{datum}T{namera['vreme_kraja']}"
                ).astimezone()

                if kraj <= pocetak:
                    return jsonify({
                        "odgovor": "Kraj termina mora biti posle početka."
                    })

                service = povezi_kalendar()

                slobodno = proveri_slobodan_termin(
                    service, pocetak, kraj
                )

                if slobodno:
                    odgovor = f"Slobodna si {datum} od {namera['vreme']} do {namera['vreme_kraja']}."
                else:
                    odgovor = f"Zauzeta si {datum} od {namera['vreme']} do {namera['vreme_kraja']}."

                return jsonify({"odgovor": odgovor})

            # Dodavanje događaja
            if namera["akcija"] == "dodavanje":

                if not all([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme")
                ]):
                    return jsonify({
                        "odgovor": "Navedi naziv događaja, datum i vreme početka."
                    })

                datum = pretvori_datum(namera["datum"])

                try:
                    datetime.fromisoformat(f"{datum}T{namera['vreme']}")
                except ValueError:
                    return jsonify({
                        "odgovor": "Datum ili vreme nisu ispravni."
                    })

                session["novi_dogadjaj"] = {
                    "naziv": namera["naziv"],
                    "datum": datum,
                    "vreme": namera["vreme"]
                }

                session["ceka_potvrdu_dogadjaja"] = True

                return jsonify({
                    "odgovor": (
                        f"Da li želiš da dodam događaj '{namera['naziv']}' "
                        f"za {datum} u {namera['vreme']}? "
                        "Podrazumevano trajanje je jedan sat. "
                        "Odgovori sa 'da' ili 'ne'."
                    )
                })

            # Izmena događaja
            if namera["akcija"] == "izmena":

                if not all ([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme"),
                    namera.get("novi_datum"),
                    namera.get("novo_vreme"),
                ]):
                    return jsonify({
                        "odgovor": "Navedi naziv događaja, postojeći datum i vreme, kao i novi datum i vreme."
                    })

                stari_datum = pretvori_datum(namera["datum"])
                novi_datum = pretvori_datum(namera["novi_datum"])

                try: 
                    datetime.fromisoformat(
                        f"{stari_datum}T{namera['vreme']}"
                    )
                    datetime.fromisoformat(
                        f"{novi_datum}T{namera['novo_vreme']}"
                    )
                except (ValueError, TypeError):
                    return jsonify({
                        "odgovor": "Datum ili vreme nisu ispravni."
                    })

                service = povezi_kalendar()

                dogadjaji = pronadji_tacan_dogadjaj(
                    service,
                    namera["naziv"],
                    stari_datum,
                    namera["vreme"]
                )

                if len(dogadjaji) == 0:
                    return jsonify({
                        "odgovor": "Nisam pronašao događaj sa tim podacima."
                    })

                if len (dogadjaji) > 1:
                    return jsonify({
                        "odgovor": "Pronađeno je više događaja sa istim podacima."
                    })

                dogadjaj = dogadjaji[0]

                pocetak = datetime.fromisoformat(
                    dogadjaj["start"]["dateTime"]
                )

                kraj = datetime.fromisoformat(
                    dogadjaj["end"]["dateTime"]
                )

                trajanje = kraj - pocetak

                session["izmena_dogadjaja"] = {
                    "event_id": dogadjaj["id"],
                    "naziv": dogadjaj["summary"],
                    "novi_datum": novi_datum,
                    "novo_vreme": namera["novo_vreme"],
                    "trajanje_sekunde": trajanje.total_seconds()
                }

                session["ceka_potvrdu_izmene"] = True

                return jsonify({
                    "odgovor": (
                        f"Da li želiš da promenim događaj '{dogadjaj['summary']}' "
                        f"sa {stari_datum} u {namera['vreme']} "
                        f"na {novi_datum} u {namera['novo_vreme']}? "
                        "Odgovori sa 'da' ili 'ne'."
                    )
                })

            #Brisanje dogadjaja
            if namera["akcija"] == "brisanje":
                if not all([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme")
                ]):
                    return jsonify({
                        "odgovor": "Navedi naziv događaja, natum ivreme događaja koji želiš da obrišes."
                    })

                datum = pretvori_datum(namera["datum"])

                try:
                    datetime.fromisoformat(f"{datum}T{namera['vreme']}")
                except (ValueError, TypeError):
                    return jsonify({
                        "odgovor": "Datum ili vreme nisu ispravni."
                    })

                service = povezi_kalendar()

                dogadjaji = pronadji_tacan_dogadjaj(
                    service,
                    namera["naziv"],
                    datum,
                    namera["vreme"]
                )

                if len(dogadjaji) == 0:
                    return jsonify({
                        "odgovor": "Nisam pronašao događaj sa tim podacima."
                    })

                if len(dogadjaji) > 1:
                    return jsonify({
                        "odgovor": "Pronađeno je više događaja sa istim podacima."
                    })

                dogadjaj = dogadjaji[0]

                session["brisanje_dogadjaja"] = {
                    "event_id": dogadjaj["id"],
                    "naziv": dogadjaj["summary"],
                    "datum": datum,
                    "vreme": namera["vreme"]
                }

                session["ceka_potvrdu_brisanja"] = True

                return jsonify({
                    "odgovor": (
                        f"Da li želiš da obrišem događaj '{dogadjaj['summary']}' "
                        f"za {datum} u {namera['vreme']}? "
                        "Odgovori sa 'da' ili 'ne'."
                    )
                })

            return jsonify({
                "odgovor": "Ta akcija kalendara još nije podržana."
            })


        # 3. Obrada zahteva za vremensku prognozu
        analiza = analiziraj_pitanje(poruka)

        podaci = spoji_podatke(analiza, session)

        lokacija = podaci["lokacija"]
        datum = podaci["datum"]
        tip = podaci["tip"]
        sat = podaci["sat"]

        sacuvaj_podatke(lokacija, datum, tip, sat)

        odgovor = proveri_nedostajuce_podatke(lokacija, datum, tip, sat)

        if odgovor is None:
            odgovor = preuzmi_prognozu(lokacija, datum, tip, sat)

            for kljuc in ("lokacija", "datum", "tip", "sat"):
                session.pop(kljuc, None)

            return jsonify({"odgovor": odgovor})

        return jsonify({"odgovor": odgovor})

    except Exception as e:
        print("Greška:", e)
        return jsonify({"odgovor": "Došlo je do greške pri obradi pitanja."}), 500

if __name__ == "__main__":
    app.run(debug=False)
        
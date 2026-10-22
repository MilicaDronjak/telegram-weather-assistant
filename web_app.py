import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from weather_service import analiziraj_pitanje, preuzmi_prognozu, proveri_nedostajuce_podatke, spoji_podatke
from rate_limiter import proveri_ogranicenje

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.route("/")
def pocetna():
    return render_template("index.html")

def sacuvaj_podatke(lokacija, datum, tip, sat):
    session["lokacija"] = lokacija
    session["datum"] = datum
    session["tip"] = tip
    session["sat"] = sat

@app.route("/chat", methods=["POST"])
def chat():
    try:
        korisnik = f"web:{request.remote_addr}"

        dozvoljeno = proveri_ogranicenje(korisnik)

        if not dozvoljeno:
            return jsonify ({
                "odgovor": "Poslali ste previše poruka. Pokušajte ponovo kasnije."
                }), 429

        podaci = request.get_json()
        poruka = podaci.get("poruka", "").strip()

        if not poruka:
            return jsonify({"odgovor": "Unesi pitanje o vremenu."})

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
            session.clear()

        return jsonify({"odgovor": odgovor})

    except Exception as e:
        print("Greška:", e)
        return jsonify({"odgovor": "Došlo je do greške pri obradi pitanja."}), 500

if __name__ == "__main__":
    app.run(debug=True)
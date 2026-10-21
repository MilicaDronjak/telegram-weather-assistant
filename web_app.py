import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from weather_service import analiziraj_pitanje, preuzmi_prognozu

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ["FLASK_SECRET_KEY"]

@app.route("/")
def pocetna():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        podaci = request.get_json()
        poruka = podaci.get("poruka", "").strip()

        if not poruka:
            return jsonify({"odgovor": "Unesi pitanje o vremenu."})

        analiza = analiziraj_pitanje(poruka)

        lokacija = analiza.get("lokacija") or session.get("lokacija")
        datum = analiza.get("datum") or session.get("datum")
        tip = analiza.get("tip", "dnevno") or session.get("tip") or "dnevno"
        sat = analiza.get("sat") or session.get("sat")

        if sat is None:
            sat = session.get("sat")

        session["lokacija"] = lokacija
        session["datum"] = datum
        session["tip"] = tip
        session["sat"] = sat

        if not lokacija:
            odgovor = "Za koji grad želiš vremensku prognozu?"
        elif not datum:
            odgovor = "Za koji datum želiš vremensku prognozu?"
        elif tip == "satna_temperatura" and sat is None:
            odgovor = "Za koji sat želiš vremensku prognozu?"
        else:
            odgovor = preuzmi_prognozu(lokacija, datum, tip, sat)
            session.clear()

        return jsonify({"odgovor": odgovor})

    except Exception as e:
        print("Greška:", e)
        return jsonify({"odgovor": "Došlo je do greške pri obradi pitanja."}), 500


if __name__ == "__main__":
    app.run(debug=True)
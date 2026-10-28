from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def prepoznaj_nameru(poruka):
    odgovor = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
                    Analiziraj korisničku poruku.

                    Prepoznaj nameru:
                    - vreme
                    - kalendar
                    - nepoznato

                    Ako je namera kalendar, prepoznaj akciju:
                    - pregled
                    - provera_termina
                    - dodavanje
                    - izmena
                    - brisanje

                    Za kalendarske zahteve izdvoji:
                    - naziv: naziv događaja, ako postoji
                    - datum: traženi datum ili dan
                    - vreme: traženo vreme u formatu HH:MM

                    Za akciju "izmena":
                    - datum: postojeći datum događaja, ako je naveden
                    - vreme: postojeće vreme početka, ako je navedeno
                    - novi_datum: datum na koji korisnik želi da pomeri događaj
                    - novo_vreme: novo vreme početka događaja
                    - Ako korisnik želi da promeni samo vreme, novi_datum je null.
                    - Ako korisnik želi da promeni samo datum, novo_vreme je null.
                    - Ne pretpostavljaj postojeći datum ili vreme ako nisu navedeni.

                    Pravila za datum:
                    - Uvek izdvoji datum ako ga korisnik pomene.
                    - Ako korisnik kaže "danas", vrati "danas".
                    - Ako korisnik kaže "sutra", vrati "sutra".
                    - Dane u nedelji uvek vrati na srpskom jeziku, malim slovima.
                    - Ako korisnik navede konkretan datum, vrati ga u formatu YYYY-MM-DD.
                    - Ako datum nije naveden, vrati null.

                    Ako korisnik želi da obriše, ukloni ili otkaže postojeći događaj iz kalendara, akcija je "brisanje".

                    Za brisanje izdvoji:
                    - naziv: naziv postojećeg događaja
                    - datum: datum događaja
                    - vreme: vreme početka događaja

                    Ako korisnik pita da li je slobodan ili zauzet u određenom periodu, akcija je "provera_termina".

                    Za proveru termina izdvoji:
                    - datum
                    -vreme: početak traženog termina u formatu HH:MM
                    -vreme_kraja: kraj traženog termina u formatu HH:MM

                    Ako korisnik ne navede kraj termina, koristi null.

                    Ako neki podatak nedostaje, koristi null.
                    Ako je namera vreme ili nepoznato, akcija je null.

                    Vrati samo JSON sa poljima:
                    namera, akcija, naziv, datum, vreme, vreme_kraja, novi_datum, novo_vreme.

                    Ne izmišljaj podatke koje korisnik nije naveo.
                """
            },
            {
                "role": "user",
                "content": poruka
            }
        ],
        response_format={"type": "json_object"}
    )

    podaci = json.loads(odgovor.choices[0].message.content)

    return podaci

if __name__ == "__main__":
    poruka = (
        "Pomeri test događaj sa 27. oktobra u 16h na 28. oktobar u 17h."
    )

    rezultat = prepoznaj_nameru(poruka)

    print("Rezultat:", rezultat)

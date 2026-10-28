import os
from dotenv import load_dotenv
from telegram import Update
from datetime import datetime, timedelta
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from weather_service import analiziraj_pitanje, preuzmi_prognozu, proveri_nedostajuce_podatke, spoji_podatke
from rate_limiter import proveri_ogranicenje
from intent_service import prepoznaj_nameru
from calendar_service import povezi_kalendar, dogadjaji_za_dan, pretvori_datum, proveri_slobodan_termin, dodaj_dogadjaj, pronadji_tacan_dogadjaj, izmeni_dogadjaj, obrisi_dogadjaj

# Učitava telegram token i api key iz .env fajla
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Šalje poruku kada se klikne start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Zdravo! Ja sam Weather Assistant bot. \n"
        "Pitaj me kakvo je vreme u nekom gradu!"
    )

def sacuvaj_podatke(stanje, lokacija, datum, tip, sat):
    stanje["lokacija"] = lokacija
    stanje["datum"] = datum
    stanje["tip"] = tip
    stanje["sat"] = sat

#Kada korisnik posalje poruku ovde se obrađuje
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    korisnik = f"telegram:{update.effective_user.id}"

    dozvoljeno = proveri_ogranicenje(korisnik)

    if not dozvoljeno:
        await update.message.reply_text(
            "Poslali ste previše poruka. Pokušajte ponovo kasnije."
        )
        return

    korisnicka_poruka = update.message.text

    # 1. Obrada potvrda za kalendar
    #potvrda za brisanje dogadjaja
    if context.user_data.get("ceka_potvrdu_brisanja"):
        odgovor_korisnika = korisnicka_poruka.strip().lower()

        if odgovor_korisnika in ["da", "potvrdi"]:
            podaci_brisanja = context.user_data["brisanje_dogadjaja"]

            try:
                service = povezi_kalendar()

                obrisi_dogadjaj(
                    service,
                    podaci_brisanja["event_id"]
                )

                await update.message.reply_text(
                    "Događaj je uspešno obrisan iz kalendara."
                )

            except Exception as e:
                print("Greška pri brisanju događaja:", e)

                await update.message.reply_text(
                    "Brisanje događaja nije uspelo."
                )

            finally:
                context.user_data.pop("ceka_potvrdu_brisanja", None)
                context.user_data.pop("brisanje_dogadjaja", None)

            return

        if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
            context.user_data.pop("ceka_potvrdu_brisanja", None)
            context.user_data.pop("brisanje_dogadjaja", None)

            await update.message.reply_text(
                "Brisanje događaja je otkazano."
            )
            return

        await update.message.reply_text(
            "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
        )
        return
    
    #potvrda za izmenu dogadjaja
    if context.user_data.get("ceka_potvrdu_izmene"):
        odgovor_korisnika = korisnicka_poruka.strip().lower()

        if odgovor_korisnika in ["da", "potvrdi"]:
            podaci = context.user_data["izmena_dogadjaja"]

            try:
                novi_pocetak = datetime.fromisoformat(
                    f"{podaci['novi_datum']}T{podaci['novo_vreme']}"
                ).astimezone()

                trajanje = timedelta (
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

                await update.message.reply_text(
                    "Događaj je uspešno izmenjen."
                )

            except Exception as e:
                print("Greška pri izmeni događaja:", e)
                await update.message.reply_text(
                    "Nije uspela izmena događaja."
                )

            finally:
                context.user_data.pop("ceka_potvrdu_izmene", None)
                context.user_data.pop("izmena_dogadjaja", None)

            return

        if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
            context.user_data.pop("ceka_potvrdu_izmene", None)
            context.user_data.pop("izmena_dogadjaja", None)

            await update.message.reply_text(
                "Izmena događaja je otkazana."
            )
            return

        await update.message.reply_text(
            "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
        )
        return
    
    #potvrda za dodavanje dogadjaja    
    if context.user_data.get("ceka_potvrdu_dogadjaja"):
        odgovor_korisnika = korisnicka_poruka.strip().lower()

        if odgovor_korisnika in ["da", "potvrdi"]:
            podaci = context.user_data["novi_dogadjaj"]

            try:
                service = povezi_kalendar()

                dodaj_dogadjaj(
                    service,
                    podaci["naziv"],
                    podaci["datum"],
                    podaci["vreme"]
                )

                await update.message.reply_text(
                    "Događaj je uspešno dodat u kalendar."
                )

            except Exception as e:
                print("Greška pri dodavanju događaja:", e)
                await update.message.reply_text(
                    "Nije uspelo dodavanje događaja u kalendar."
                )

            finally:
                context.user_data.pop("ceka_potvrdu_dogadjaja", None)
                context.user_data.pop("novi_dogadjaj", None)

            return

        if odgovor_korisnika in ["ne", "otkaži", "otkazi"]:
            context.user_data.pop("ceka_potvrdu_dogadjaja", None)
            context.user_data.pop("novi_dogadjaj", None)

            await update.message.reply_text(
                "Dodavanje događaja je otkazano."
            )
            return

        await update.message.reply_text(
            "Odgovori sa 'da' za potvrdu ili 'ne' za otkazivanje."
        )
        return
    try:
        namera = prepoznaj_nameru(korisnicka_poruka)

        if namera["namera"] == "kalendar":

            #brisanje dogadjaja
            if namera["akcija"] == "brisanje":

                if not all([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme")
                ]):
                    
                    await update.message.reply_text(
                        "Navedi naziv događaja, datum i vreme događaja koji želiš da obrišeš."
                    )
                    return

                datum = pretvori_datum(namera["datum"])

                try:
                    datetime.fromisoformat(
                        f"{datum}T{namera['vreme']}"
                    )
                except (ValueError, TypeError):
                    await update.message.reply_text(
                        "Datum ili vreme nisu ispravni."
                    )
                    return

                service = povezi_kalendar()

                dogadjaji = pronadji_tacan_dogadjaj(
                    service,
                    namera["naziv"],
                    datum,
                    namera["vreme"]
                )

                if len(dogadjaji) == 0:
                    await update.message.reply_text(
                        "Nisam pronašao događaj sa tim podacima."
                    )
                    return

                if len(dogadjaji) > 1:
                    await update.message.reply_text(
                        "Pronađeno je više događaja sa istim podacima."
                    )
                    return

                dogadjaj = dogadjaji[0]

                context.user_data["brisanje_dogadjaja"] = {
                    "event_id": dogadjaj["id"],
                    "naziv": dogadjaj["summary"],
                    "datum": datum,
                    "vreme": namera["vreme"]
                }

                context.user_data["ceka_potvrdu_brisanja"] = True

                await update.message.reply_text(
                    f"Da li želiš da obrišem događaj '{dogadjaj['summary']}' "
                    f"za {datum} u {namera['vreme']}? "
                    "Odgovori sa 'da' ili 'ne'."
                )
                return

            #izmena dogadjaja
            if namera["akcija"] == "izmena":

                if not all([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme"),
                    namera.get("novi_datum"),
                    namera.get("novo_vreme")
                ]):
                    await update.message.reply_text(
                        "Navedi naziv događaja, postojeći datum i vreme, kao i novi datum i vreme."
                    )
                    return

                stari_datum = pretvori_datum(namera["datum"])
                novi_datum = pretvori_datum(namera["novi_datum"])

                try:
                    datetime.fromisoformat(
                        f"{stari_datum}T{namera['vreme']}"
                    )
                except (ValueError, TypeError):
                    await update.message.reply_text(
                        "Datum ili vreme nisu ispravni."
                        "Proveri postojeći i novi datum."
                    )
                    return

                service = povezi_kalendar()

                dogadjaji = pronadji_tacan_dogadjaj(
                    service,
                    namera["naziv"],
                    stari_datum,
                    namera["vreme"]
                )

                if len(dogadjaji) == 0:
                    await update.message.reply_text(
                        "Nisam pronašla događaj sa tim nazivom, datumom i vremenom."
                    )
                    return

                if len(dogadjaji) > 1:
                    await update.message.reply_text(
                        "Pronašla sam više događaja sa istim podacima. "
                        "Potrebno je da preciziraš koji želiš da izmeniš."
                    )
                    return

                dogadjaj = dogadjaji[0]

                pocetak_dogadjaja = datetime.fromisoformat(
                    dogadjaj["start"]["dateTime"]
                )

                kraj_dogadjaja = datetime.fromisoformat(
                    dogadjaj["end"]["dateTime"]
                )

                trajanje = kraj_dogadjaja - pocetak_dogadjaja

                context.user_data["izmena_dogadjaja"] = {
                    "event_id": dogadjaj["id"],
                    "naziv": dogadjaj["summary"],
                    "stari_datum": stari_datum,
                    "staro_vreme": namera["vreme"],
                    "novi_datum": novi_datum,
                    "novo_vreme": namera["novo_vreme"],
                    "trajanje_sekunde": trajanje.total_seconds(),
                }

                context.user_data["ceka_potvrdu_izmene"] = True

                await update.message.reply_text(
                    f"Da li želiš da pomerim događaj '{dogadjaj['summary']}' "
                    f"sa {stari_datum} u {namera['vreme']} "
                    f"na {novi_datum} u {namera['novo_vreme']}? "
                    "Odgovori sa 'da' ili 'ne'."
                )
                return

            #dodavanje dogadjaja
            if namera["akcija"] == "dodavanje":

                if not all([
                    namera.get("naziv"),
                    namera.get("datum"),
                    namera.get("vreme")
                ]):
                    await update.message.reply_text(
                        "Navedi naziv događaja, datum i vreme početka."
                    )
                    return

                datum = pretvori_datum(namera["datum"])

                try:
                    datetime.fromisoformat(
                        f"{datum}T{namera['vreme']}"
                    )
                except ValueError:
                    await update.message.reply_text(
                        "Datum ili vreme nisu ispravni."
                    )
                    return

                context.user_data["novi_dogadjaj"] = {
                    "naziv": namera["naziv"],
                    "datum": datum,
                    "vreme": namera["vreme"]
                }

                context.user_data["ceka_potvrdu_dogadjaja"] = True

                await update.message.reply_text(
                    f"Da li želiš da dodam događaj "
                    f"'{namera['naziv']}' za {datum} "
                    f"u {namera['vreme']}? "
                    f"Podrazumevano trajanje je jedan sat. "
                    f"Odgovori sa 'da' ili 'ne'."
                )
                return

            #provera slobodnog termina
            if namera["akcija"] == "provera_termina":

                if not all([
                    namera.get("datum"),
                    namera.get("vreme"),
                    namera.get("vreme_kraja")
                ]):
                    await update.message.reply_text(
                        "Navedi datum, početak i kraj termina koji želiš da proverim."
                    )
                    return

                datum = pretvori_datum(namera["datum"])

                pocetak = datetime.fromisoformat(
                    f"{datum}T{namera['vreme']}"
                ).astimezone()

                kraj = datetime.fromisoformat(
                    f"{datum}T{namera['vreme_kraja']}"
                ).astimezone()

                if kraj <= pocetak:
                    await update.message.reply_text(
                        "Kraj termina mora biti posle početka."
                    )
                    return

                service = povezi_kalendar()

                slobodno = proveri_slobodan_termin(
                    service, pocetak, kraj
                )

                if slobodno:
                    odgovor = f"Slobodna si {datum} od {namera['vreme']} do {namera['vreme_kraja']}."
                else:
                    odgovor = f"Zauzeta si {datum} od {namera['vreme']} do {namera['vreme_kraja']}."

                await update.message.reply_text(odgovor)
                return

            #pregled dogadjaja
            if namera["akcija"] == "pregled":
            
                if namera["datum"] is None:
                    await update.message.reply_text(
                        "Za koji datum želiš da proverim kalendar?"
                    )
                    return

                datum = pretvori_datum(namera["datum"])

                service = povezi_kalendar()
                dogadjaji = dogadjaji_za_dan(service, datum)

                if dogadjaji:
                    odgovor = "Događaji za " + datum + ":\n"

                    for dogadjaj in dogadjaji:
                        naziv = dogadjaj.get("summary", "Bez naziva")
                        odgovor += f"- {naziv}\n"

                else:
                    odgovor = "Nema događaja za taj dan."

                await update.message.reply_text(odgovor)
                return

            await update.message.reply_text(
                "Za sada je podržan samo pregled kalendara."
            )
            return
        #dobijanje vremenske prognoze
        podaci = analiziraj_pitanje(korisnicka_poruka)

        stari_podaci = context.user_data

        podaci = spoji_podatke(podaci, stari_podaci)

        lokacija = podaci["lokacija"]
        datum = podaci["datum"]
        tip = podaci["tip"]
        sat = podaci["sat"]

        sacuvaj_podatke(context.user_data, lokacija, datum, tip, sat)

        odgovor = proveri_nedostajuce_podatke(lokacija, datum, tip, sat)

        if odgovor is not None:
            await update.message.reply_text(odgovor)
            return

        prognoza = preuzmi_prognozu(lokacija, datum, tip, sat)

        await update.message.reply_text(prognoza)

        context.user_data.clear()

    except Exception as e:
        print("Greska:", e)
        await update.message.reply_text(
            "Doslo je do greske pri obradi pitanja."
        )

# Povezuje bota sa telegramom i pokrece ga
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("Telegram token nije pronadjen u .env fajlu!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot je pokrenut!")
    app.run_polling() 

if __name__ == "__main__":
    main()

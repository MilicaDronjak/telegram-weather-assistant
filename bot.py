import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from weather_service import analiziraj_pitanje, preuzmi_prognozu, proveri_nedostajuce_podatke, spoji_podatke
from rate_limiter import proveri_ogranicenje

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

    try:
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

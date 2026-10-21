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
from weather_service import analiziraj_pitanje, preuzmi_prognozu
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

        lokacija = context.user_data.get("lokacija")
        datum = context.user_data.get("datum")
        tip = context.user_data.get("tip")
        sat = context.user_data.get("sat")

        if podaci.get("lokacija") is not None:
            lokacija = podaci["lokacija"]

        if podaci.get("datum") is not None:
            datum = podaci["datum"]

        if not tip:
            tip = podaci.get("tip", "dnevno")

        if podaci.get("sat") is not None:
            sat = podaci["sat"]

        context.user_data["lokacija"] = lokacija
        context.user_data["datum"] = datum
        context.user_data["tip"] = tip
        context.user_data["sat"] = sat

        if not lokacija:
            await update.message.reply_text(
                "Za koji grad zelis vremensku prognozu?"
            )
            return

        if not datum:
            await update.message.reply_text(
                "Za koji datum zelis vremensku prognozu?"
            )
            return
        
        if tip == "satna_temperatura" and sat is None:
            await update.message.reply_text(
                "Za koji sat želiš vremensku prognozu?"
            )
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

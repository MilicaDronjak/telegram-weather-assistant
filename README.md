
# Telegram Weather Assistant

Telegram bot koji koristi vestačku inteligenciju za razumevanje korisničkih pitanja i prikaz vremenske prognoze. Korisnik može da komunicira sa asistentom putem Telegram bota ili veb-chata.

## Funkcionalnosti

- Prikaz trenutne temperature i vremenskih uslova
- Dnevna vremenska prognoza
- Prognoza temperature za određene sate
- Verovatnoća i očekivana količina padavina
- Prepoznavanje grada, datuma i sata iz prirodnog jezika
- Pamćenje podataka kroz vise poruka
- Obrada nepoznatih gradova i nedostupnih datuma
- Komunikacija sa asistentom putem Telegram bota i veb-chata 

## Koriscene tehnologije

- Python
- Telegram Bot API
- Groq API (LLM)
- Open-Meteo API
- python-telegram-bot
- requests
- python-dotenv
- Flask
- HTML
- CSS
- JavaScript

## Pokretanje projekta

1. Preuzeti projekat.
2. Napraviti virtuelno okruzenje:
   python -m venv .venv
3. Aktivirati virtuelno okruzenje.
   Windows:
   .venv\Scripts\activate
4. Instalirati biblioteke:
   pip install -r requirements.txt
5. Napraviti `.env` fajl i uneti:
   TELEGRAM_BOT_TOKEN=telegram_token
   GROQ_API_KEY=groq_api_kljuc
   FLASK_SECRET_KEY=tajni_kljuc
6. Za pokretanje Telegram bota:
   python bot.py
7. Za pokretanje veb-chata:
   python web_app.py
8. Adresa web-chat-a
   http://127.0.0.1:5000

## Primeri pitanja

- Kakvo je vreme trenutno u Novom Sadu?
- Kakvo će vreme biti sutra u Beogradu?
- Da li će u subotu padati kiša na Zlatiboru?
- Kolika će biti temperatura večeras u Somboru?

## Nacin rada

1. Korisnik postavlja pitanje putem Telegram bota ili veb-chata.
2. Groq AI analizira pitanje i izdvaja lokaciju, datu, tip pitanja i sat.
3. Ako neki podatak nedostaje, bot traži dopunu i pamti prethodne unete podatke.
4. Pomoću Open-Meteo Geocoding API-ja bot pronalazi geografske koordinate lokacije.
5. Open-Meteo Forecast API vraća tražene vremenske podatke.
6. Bot obrađuje podatke i šalje odgovor korisniku.
7. Nakon slanja odgovora, sačuvani podaci se brišu kako bi naredno pitanje moglo da se orađuje nezavisno.

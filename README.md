
# Telegram Weather Assistant

Telegram bot i veb-aplikacija koji koriste veštačku inteligenciju za razumevanje korisničkih pitanja i izvršavanje različitih zadataka. Aplikacija omogućava korisniku da dobije informacije o vremenskoj prognozi, kao i da upravlja obavezama u Google kalendaru kroz pregled događaja, proveru slobodnih termina, dodavanje, izmenu i brisanje događaja.
Korisnik može da komunicira sa asistentom putem Telegram bota ili web_chat-a, koristeći prirodan jezik.

## Funkcionalnosti

**Vremenska prognoza**
- Prikaz trenutne temperature i vremenskih uslova
- Dnevna vremenska prognoza
- Prognoza temperature za određene sate
- Prikaz verovatnoće i očekivane količine padavina
- Prepoznavanje grada, datuma i vremena iz prirodnog jezika
- Pamćenje podataka kroz više poruka
- Obrada nepoznatih gradova i datuma za koje prognoza nije dostupna

**Google kalendar**
- Pregled predstojećih događaja i obaveza za određeni datum
- Provera slobodnih i zauzetih termina
- Dodavanje novih događaja u kalendar
- Izmena datuma i vremena postojećih događaja
- Brisanje događaja iz kalendara
- Potvrđivanje i otkazivanje dodavanja, izmene i brisanja događaja
- Prepoznavanje zahteva za rad sa kalendarom iz prirodnog jezika

**Komunikacija**
- Komunikacija sa asistentom putem Telegram bota i web_chat-a
- Automatsko prepoznavanje da li se korisnički zahtev odnosi na vremensku prognozu ili Google kalendar

## Korišćene tehnologije

- Python
- Telegram Bot API
- Groq API (LLM)
- Open-Meteo API
- Google Calendar API
- Google OAuth 2.0
- python-telegram-bot
- google-api-python-client
- google-auth-oauthlib
- google-auth-httplib2
- requests
- python-dotenv
- Flask
- HTML
- CSS
- JavaScript

## Pokretanje projekta

1. Preuzeti projekat.

2. Napraviti virtuelno okruženje:
   python -m venv .venv

3. Aktivirati virtuelno okruženje.
   Windows (Git Bash):
   source .venv/Scripts/activate

4. Instalirati potrebne biblioteke:
   pip install -r requirements.txt

5. Napraviti `.env` fajl u glavnom direktorijumu projekta i uneti:
   TELEGRAM_BOT_TOKEN=telegram_token
   GROQ_API_KEY=groq_api_kljuc
   FLASK_SECRET_KEY=tajni_kljuc

6. Podesiti pristup Google kalendaru:
   - U Google Cloud Console kreirati projekat i omogućiti Google Calendar API.
   - Podesiti OAuth consent screen i kreirati OAuth klijenta tipa Desktop app.
   - Preuzeti OAuth podatke i sačuvati ih u fajlu `credentials.json` u glavnom direktorijumu projekta.
   - Prilikom prvog povezivanja sa kalendarom otvoriti Google stranicu za autorizaciju i odobriti pristup.
   - Nakon uspešne autorizacije aplikacija automatski kreira `token.json`, koji koristi za naredna povezivanja.

7. Pokrenuti Telegram bota:
   python bot.py

8. Pokrenuti web_chat u drugom terminalu:
   python web_app.py

9. Otvoriti web_chat u pregledaču na adresi:
   http://127.0.0.1:5000

## Primeri pitanja

Vremenska prognoza
- Kakvo je vreme trenutno u Novom Sadu?
- Kakvo će vreme biti sutra u Beogradu?
- Da li će u subotu padati kiša na Zlatiboru?
- Kolika će biti temperatura večeras u Somboru?

Google kalendar
- Šta imam 4. novembra u kalendaru?
- Koje obaveze imam sutra?
- Da li sam slobodna 4. novembra od 10 do 11h?
- Zakaži sastanak za 6. novembar u 12h.
- Pomeri sastanak sa 6. novembra u 12h na 7. novembar u 14h.
- Obriši sastanak za 7. novembar u 14h.

Prilikom dodavanja, izmene i brisanja događaja, asistent traži potvrdu korisnika. Korisnik može da potvrdi operaciju odgovorom „da“ ili da je otkaže odgovorom „ne“.

## Način rada

1. Korisnik šalje poruku putem Telegram bota ili web_chat-a.
2. Groq AI analizira poruku i prepoznaje da li se zahtev odnosi na vremensku prognozu ili Google kalendar.
3. Na osnovu prepoznate namere, aplikacija obrađuje zahtev.

**Vremenska prognoza**

4. Groq AI izdvaja potrebne podatke iz poruke, kao što su lokacija, datum, vreme i tip vremenske prognoze.
5. Ako neki podatak nedostaje, asistent traži dopunu i pamti prethodno unete podatke.
6. Pomoću Open-Meteo Geocoding API-ja aplikacija pronalazi geografske koordinate tražene lokacije.
7. Open-Meteo Forecast API vraća odgovarajuće vremenske podatke.
8. Aplikacija obrađuje dobijene podatke i šalje odgovor korisniku.
9. Nakon završetka zahteva, sačuvani podaci se uklanjaju kako bi naredno pitanje moglo nezavisno da se obradi.

**Google kalendar**

4. Groq AI prepoznaje traženu akciju: pregled događaja, proveru slobodnog termina, dodavanje, izmenu ili brisanje događaja.
5. Iz korisničke poruke izdvajaju se potrebni podaci, kao što su naziv događaja, datum, vreme početka i vreme kraja.
6. Aplikacija uspostavlja vezu sa Google Calendar API-jem pomoću OAuth 2.0 autorizacije.
7. U zavisnosti od zahteva, aplikacija preuzima događaje, proverava zauzetost termina ili priprema dodavanje, izmenu ili brisanje događaja.
8. Prilikom dodavanja, izmene i brisanja događaja, aplikacija traži potvrdu korisnika. Odgovorom „da“ korisnik potvrđuje operaciju, a odgovorom „ne“ je otkazuje.
9. Nakon potvrde, aplikacija izvršava odgovarajuću operaciju preko Google Calendar API-ja i obaveštava korisnika o rezultatu.
10. Nakon završetka ili otkazivanja operacije, privremeno sačuvani podaci o zahtevu se uklanjaju.
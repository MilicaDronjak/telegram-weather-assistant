
# Smart Assistant

Smart Assistant je aplikacija koja koristi veštačku inteligenciju za razumevanje korisničkih pitanja i izvršavanje različitih zadataka. Omogućava dobijanje informacija o vremenskoj prognozi, kao i upravljanje obavezama u Google kalendaru kroz pregled događaja, proveru slobodnih termina, dodavanje, izmenu i brisanje događaja.

Korisnik može da komunicira sa asistentom putem Telegram bota ili web aplikacije, koristeći prirodan jezik. Web aplikacija dodatno omogućava registraciju i prijavu korisnika, čime se obezbeđuje kontrolisan pristup njenim funkcionalnostima.

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
- Pregled događaja i obaveza za određeni datum
- Provera slobodnih i zauzetih termina
- Dodavanje novih događaja u kalendar
- Izmena datuma i vremena postojećih događaja
- Brisanje događaja iz kalendara
- Potvrđivanje i otkazivanje dodavanja, izmene i brisanja događaja
- Prepoznavanje zahteva za rad sa kalendarom iz prirodnog jezika

**Registracija i autentifikacija korisnika**
- Registracija novih korisnika putem web aplikacije
- Prijava i odjava korisnika
- Bezbedno čuvanje lozinki u obliku hash vrednosti
- Čuvanje korisničkih naloga u SQLite bazi podataka
- Upravljanje korisničkim sesijama
- Ograničavanje pristupa web chatu neprijavljenim korisnicima

**Ograničenje zahteva**
- Ograničenje broja zahteva radi zaštite aplikacije od prekomernog korišćenja
- Čuvanje podataka o zahtevima u SQLite bazi
- Ograničavanje pokušaja prijave i registracije
- Prikaz odgovarajuće poruke kada korisnik prekorači dozvoljeni broj zahteva

**Komunikacija**
- Komunikacija sa asistentom putem Telegram bota i web aplikacije
- Automatsko prepoznavanje da li se korisnički zahtev odnosi na vremensku prognozu ili Google kalendar
- Razumevanje korisničkih zahteva napisanih prirodnim jezikom
- Postavljanje dodatnih pitanja kada nedostaju podaci potrebni za izvršavanje zahteva
- Nastavak razgovora uz korišćenje prethodno unetihinformacija

## Korišćene tehnologije
Backend i web aplikacija
- Python
- Flask
- SQLite
- Werkzeug (hashiranje i provera lozinki)

Veštačka inteligencija i ekstremni servisi
- Telegram Bot API
- Groq API (LLM)
- Open-Meteo API
- Google Calendar API
- Google OAuth 2.0

Python biblioteke
- python-telegram-bot
- google-api-python-client
- google-auth-oauthlib
- google-auth-httplib2
- requests
- python-dotenv

Frontend
- HTML
- CSS
- JavaScript

Testiranje
- pytest

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
   (Prilikom prvog pristupa web aplikaciji potrebno je registrovati korisnički nalog. Nakon uspešne registracije korisnik može da se prijavi i pristupi web chatu.)

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

1. Korisnik šalje poruku putem Telegram bota ili web aplikacije.
2. Za korišćenje web aplikacije potrebna je registracija i prijava korisnika.
3. Pre obrade poruke proverava se ograničenje broja zahteva(rate-limiter)
4. Groq AI analizira poruku i prepoznaje da li se zahtev odnosi na vremensku prognozu ili Google kalendar.
5. Na osnovu prepoznate namere, aplikacija obrađuje zahtev.

**Vremenska prognoza**

6. Groq AI izdvaja potrebne podatke iz poruke, kao što su lokacija, datum, vreme i tip vremenske prognoze.
7. Ako neki podatak nedostaje, asistent traži dopunu i pamti prethodno unete podatke.
8. Pomoću Open-Meteo Geocoding API-ja aplikacija pronalazi geografske koordinate tražene lokacije.
9. Open-Meteo Forecast API vraća odgovarajuće vremenske podatke.
10. Aplikacija obrađuje dobijene podatke i šalje odgovor korisniku.
11. Nakon završetka zahteva, sačuvani podaci se uklanjaju kako bi naredno pitanje moglo nezavisno da se obradi.

**Google kalendar**

6. Groq AI prepoznaje traženu akciju: pregled događaja, proveru slobodnog termina, dodavanje, izmenu ili brisanje događaja.
7. Iz korisničke poruke izdvajaju se potrebni podaci, kao što su naziv događaja, datum, vreme početka i vreme kraja.
8. Aplikacija uspostavlja vezu sa Google Calendar API-jem pomoću OAuth 2.0 autorizacije.
9. U zavisnosti od zahteva, aplikacija preuzima događaje, proverava zauzetost termina ili priprema dodavanje, izmenu ili brisanje događaja.
10. Prilikom dodavanja, izmene i brisanja događaja, aplikacija traži potvrdu korisnika. Odgovorom „da“ korisnik potvrđuje operaciju, a odgovorom „ne“ je otkazuje.
11. Nakon potvrde, aplikacija izvršava odgovarajuću operaciju preko Google Calendar API-ja i obaveštava korisnika o rezultatu.
12. Nakon završetka ili otkazivanja operacije, privremeno sačuvani podaci o zahtevu se uklanjaju.

## Testiranje

Za testiranje aplikacije koristi se biblioteka pytest. Implementirani su Unit i Integration testovi koji proveravaju ispravnost pojedinačnih funkcija i međusobnu saradnju komponenti aplikacije.

**Unit testovi**
- Testiranje funkcija za obradu vremenske prognoze i proveru potrebnih podataka.
- Testiranje funkcija za rad sa Google kalendarom.
- Testiranje Rate Limitera, uključujući ograničenje broja zahteva i istek vremenskog perioda.
- Testiranje obrade odgovora LLM-a, uključujući neispravan JSON, nepotpune podatke i greške API-ja.

**Integration testovi**
- Testiranje obrade korisničkih zahteva putem Flask web-aplikacije.
- Testiranje komunikacije sa Telegram botom.
- Testiranje pamćenja podataka kroz više poruka.
- Testiranje potvrđivanja i otkazivanja dodavanja događaja u kalendar.

**Testiranje autentifikacije**
- Testiranje uspešne registracije korisnika.
- Testiranje registracije sa prekratkom lozinkom i već postojećim korisničkim imenom.
- Testiranje uspešne i neuspešne prijave korisnika.
- Testiranje odjave korisnika.
- Testiranje zaštite web aplikacije od pristupa neprijavljenih korisnika.
- Testiranje ograničenja pokušaja prijave i registracije.

Prilikom testiranja koriste se mock objekti kako bi se simulirali odgovori spoljnih servisa, bez slanja stvarnih zahteva ka Groq, Open-Meteo i Google Calendar API-jima.

Testovi se pokreću iz glavnog direktorijuma projekta komandom: python -m pytest -v

Ukupno je implementiran **61 test**, raspoređen u šest fajlova:

- `test_weather.py` – 22 testa
- `test_calendar.py` – 9 testova
- `test_rate_limiter.py` – 4 testa
- `test_integration.py` – 10 testova
- `test_bot.py` – 6 testova
- `test_auth.py` - 10 testova


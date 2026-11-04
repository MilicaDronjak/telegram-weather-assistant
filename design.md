1. Šta bot treba da omogući korisniku?
    Bot treba da omogući korisniku da putem Telegrama postavlja pitanja o vremenskoj prognozi običnim jezikom, na primer „Kakvo će vreme biti sutra u Novom Sadu?“.Potrebno je da prepozna lokaciju i datum iz pitanja i da korisniku prikaže odgovarajuću vremensku prognozu, kao što su temperatura i padavine. Korisnik može da pita za trenutno vreme, dnevnu prognozu ili mogućnost kiše.Ukoliko korisnik ne navede sve potrebne informacije, na primer grad, bot treba da postavi dodatno pitanje kako bi mogao da prikaže odgovarajuću prognozu.

2. Koje spoljne servise koristiš i zašto baš njih?
    Telegram Bot API koristim kako bi moj Python program mogao da prima poruke korisnika i šalje odgovore preko Telegrama.
    
    Groq API koristim da bi bot mogao da razume pitanja koja korisnik postavlja običnim jezikom i da prepozna lokaciju, datum i vrstu prognoze. Izabrala sam ga zato što ima besplatan plan i jednostavan je za povezivanje sa Pythonom.

    Open-Meteo API koristim za preuzimanje stvarnih podataka o vremenskoj prognozi. Izabrala sam ga zato što je besplatan za nekomercijalnu upotrebu, ne zahteva API ključ i pruža podatke koji su mi potrebni.

3. Kako bot radi korak po korak, od poruke korisnika do odgovora?
    Korisnik prvo pošalje pitanje o vremenskoj prognozi preko Telegrama, na primer „Kakvo će vreme biti sutra u Novom Sadu?“.
    Program preuzima poruku preko Telegram Bot API-ja, a zatim je šalje Groq API-ju kako bi AI model prepoznao lokaciju, datum i vrstu prognoze koju korisnik traži.
    Nakon toga program proverava da li ima sve potrebne informacije. Ako korisnik nije naveo grad ili datum koji je potreban, bot mu postavlja dodatno pitanje.
    Kada ima potrebne podatke, program šalje zahtev Open-Meteo API-ju, koji vraća podatke o vremenskoj prognozi za traženu lokaciju i datum.
    Na kraju Python program obrađuje dobijene podatke, sastavlja odgovor i šalje ga korisniku preko Telegrama.

4. Ako koristiš LLM, za šta ga koristiš?
    LLM koristim kako bi moj bot mogao da razume pitanja koja korisnik postavlja običnim jezikom. Preko Groq API-ja koristim AI model koji iz korisnikovog pitanja prepoznaje lokaciju, datum i vrstu vremenske prognoze. Na primer, ako korisnik napiše „Kakvo će vreme biti sutra u Novom Sadu?“, model prepoznaje da se traži dnevna prognoza za Novi Sad za sutrašnji datum. LLM ne koristim za dobijanje podataka o vremenu, već samo za razumevanje pitanja. Stvarne podatke o temperaturi i padavinama preuzimam preko Open-Meteo API-ja.

5. Istraživanje hostovanja
    Za hostovanje Smart Assistant aplikacije razmatraju se platforme Render i PythonAnywhere, koje podržavaju Python i Flask aplikacije.

    **Render** omogućava povezivanje sa GitHub repozitorijumom, pokretanje Flask aplikacije pomoću Gunicorn servera i čuvanje API ključeva kroz environment variables. Prednost je jednostavno objavljivanje novih verzija aplikacije. Ograničenje predstavlja podrazumevani sistem datoteka koji nije trajan, što zahteva dodatno rešenje za SQLite baze.

    **PythonAnywhere** omogućava pokretanje Flask aplikacija preko WSGI konfiguracije i podržava rad sa SQLite bazama. Pogodan je za manje Python projekte, ali zahteva ručno podešavanje serverskog okruženja.

    Za Smart Assistant potrebno je uzeti u obzir nekoliko stvari:
    - Flask web aplikacija mora biti dostupna preko HTTPS-a.
    - SQLite baze (`users.db` i `rate_limiter.db`) zahtevaju trajno skladištenje.
    - API ključevi moraju ostati u promenljivama okruženja.
    - Google Calendar trenutno koristi zajednički `token.json`, pa je za više korisnika potrebna zasebna OAuth autorizacija.
    - Telegram bot zahteva zaseban proces koji može kontinuirano da prima poruke.

- Render predstavlja pogodniji izbor za buduće hostovanje Smart Assistant web aplikacije jer omogućava jednostavno povezivanje sa GitHub repozitorijumom i automatsko ažuriranje aplikacije nakon izmena koda, dok PythonAnywhere zahteva nešto više ručnog podešavanja. Pre javnog objavljivanja potrebno je obezbediti trajno čuvanje SQLite baza, zasebnu Google Calendar autorizaciju za svakog korisnika i dodatna bezbednosna podešavanja. Aplikacija se trenutno pokreće lokalno, a njeno hostovanje predstavlja mogućnost daljeg razvoja projekta.
        
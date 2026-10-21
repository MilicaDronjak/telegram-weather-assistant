const dugme = document.getElementById("posalji")
const unos = document.getElementById("poruka")
const chat = document.getElementById("chat")

async function posaljiporuku() {
    const poruka = unos.value.trim();

    if(!poruka){
        return
    }

const korisnik = document.createElement("p")
korisnik.classList.add("poruka", "korisnik")
korisnik.textContent = poruka;
chat.appendChild(korisnik);

unos.value = "";

try {
    const odgovor = await fetch("/chat", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ poruka: poruka })
});

    const podaci = await odgovor.json();

    const bot = document.createElement("p");
    bot.classList.add("poruka", "bot")
    const naziv = document.createElement("strong");
    naziv.textContent = "Bot: ";
    bot.appendChild(naziv);
    bot.appendChild(document.createTextNode(podaci.odgovor));    

    chat.appendChild(bot);

} catch (greska) {
    const bot = document.createElement("p");
    bot.textContent = "Bot: Došlo je do greške pri slanju poruke.";
    chat.appendChild(bot);
    console.error(greska); 
}
    chat.scrollTop = chat.scrollHeight;

}

dugme.addEventListener("click", posaljiporuku);

unos.addEventListener("keydown", function(event){
    if(event.key === "Enter") {
        posaljiporuku();
    }
})
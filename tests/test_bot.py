
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from bot import handle_message


def test_telegram_blokiran_zahtev():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.text = "Kakvo je vreme danas?"
    update.message.reply_text = AsyncMock()

    with patch("bot.proveri_ogranicenje", return_value=False):
        asyncio.run(handle_message(update, context))

    update.message.reply_text.assert_awaited_once_with(
        "Poslali ste previše poruka. Pokušajte ponovo kasnije."
    )


def test_telegram_vremenska_prognoza():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.text = "Kakvo je vreme sutra u Novom Sadu?"
    update.message.reply_text = AsyncMock()

    context.user_data = {}

    analiza = {
        "lokacija": "Novi Sad",
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    with patch("bot.proveri_ogranicenje", return_value=True), \
         patch("bot.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("bot.analiziraj_pitanje", return_value=analiza), \
         patch("bot.preuzmi_prognozu",
               return_value="Prognoza za Novi Sad: 15°C.") as mock_prognoza:

        asyncio.run(handle_message(update, context))

    update.message.reply_text.assert_awaited_once_with(
        "Prognoza za Novi Sad: 15°C."
    )

    mock_prognoza.assert_called_once_with(
        "Novi Sad", "2026-11-03", "dnevno", None
    )

    assert context.user_data == {}


def test_telegram_nedostaje_lokacija():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.text = "Kakvo će vreme biti sutra?"
    update.message.reply_text = AsyncMock()

    context.user_data = {}

    analiza = {
        "lokacija": None,
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    with patch("bot.proveri_ogranicenje", return_value=True), \
         patch("bot.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("bot.analiziraj_pitanje", return_value=analiza), \
         patch("bot.preuzmi_prognozu") as mock_prognoza:

        asyncio.run(handle_message(update, context))

    update.message.reply_text.assert_awaited_once()

    odgovor = update.message.reply_text.call_args.args[0]
    assert "grad" in odgovor.lower()

    mock_prognoza.assert_not_called()

    assert context.user_data["lokacija"] is None
    assert context.user_data["datum"] == "2026-11-03"



def test_telegram_nastavak_razgovora():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context.user_data = {}

    prva_analiza = {
        "lokacija": None,
        "datum": "2026-11-03",
        "tip": "dnevno",
        "sat": None
    }

    druga_analiza = {
        "lokacija": "Novi Sad",
        "datum": None,
        "tip": "dnevno",
        "sat": None
    }

    with patch("bot.proveri_ogranicenje", return_value=True), \
         patch("bot.prepoznaj_nameru",
               return_value={"namera": "vreme"}), \
         patch("bot.analiziraj_pitanje",
               side_effect=[prva_analiza, druga_analiza]), \
         patch("bot.preuzmi_prognozu",
               return_value="Prognoza za Novi Sad.") as mock_prognoza:

        update.message.text = "Kakvo će vreme biti sutra?"
        asyncio.run(handle_message(update, context))

        update.message.text = "Novi Sad"
        asyncio.run(handle_message(update, context))

    mock_prognoza.assert_called_once_with(
        "Novi Sad", "2026-11-03", "dnevno", None
    )

    assert update.message.reply_text.await_count == 2

    assert update.message.reply_text.await_args.args[0] == (
        "Prognoza za Novi Sad."
    )

    assert context.user_data == {}


def test_telegram_dodavanje_dogadjaja():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context.user_data = {}

    namera = {
        "namera": "kalendar",
        "akcija": "dodavanje",
        "naziv": "Sastanak",
        "datum": "2026-11-05",
        "vreme": "10:00"
    }

    with patch("bot.proveri_ogranicenje", return_value=True), \
         patch("bot.prepoznaj_nameru", return_value=namera), \
         patch("bot.pretvori_datum", return_value="2026-11-05"), \
         patch("bot.povezi_kalendar"), \
         patch("bot.dodaj_dogadjaj") as mock_dodaj:

        update.message.text = "Dodaj sastanak 5. novembra u 10"
        asyncio.run(handle_message(update, context))

        assert context.user_data["ceka_potvrdu_dogadjaja"] is True

        update.message.text = "da"
        asyncio.run(handle_message(update, context))

    update.message.reply_text.assert_any_await(
        "Događaj je uspešno dodat u kalendar."
    )

    mock_dodaj.assert_called_once()

    assert context.user_data == {}



def test_telegram_otkazivanje_dodavanja():
    update = MagicMock()
    context = MagicMock()

    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    context.user_data = {}

    namera = {
        "namera": "kalendar",
        "akcija": "dodavanje",
        "naziv": "Sastanak",
        "datum": "2026-11-05",
        "vreme": "10:00"
    }

    with patch("bot.proveri_ogranicenje", return_value=True), \
         patch("bot.prepoznaj_nameru", return_value=namera), \
         patch("bot.pretvori_datum", return_value="2026-11-05"), \
         patch("bot.dodaj_dogadjaj") as mock_dodaj:

        update.message.text = "Dodaj sastanak 5. novembra u 10"
        asyncio.run(handle_message(update, context))

        assert context.user_data["ceka_potvrdu_dogadjaja"] is True

        update.message.text = "ne"
        asyncio.run(handle_message(update, context))

    update.message.reply_text.assert_any_await(
        "Dodavanje događaja je otkazano."
    )

    mock_dodaj.assert_not_called()

    assert context.user_data == {}

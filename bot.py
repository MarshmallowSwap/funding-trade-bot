import aiohttp
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import start, status_new, funding_1h, funding_2h, short, long
from alert_logic import process_funding

BOT_TOKEN = "INSERISCI_IL_TUO_TOKEN"
CHAT_ID = "INSERISCI_IL_TUO_CHAT_ID"


async def fetch_funding():
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["result"]["list"]


async def funding_job(app):
    data = await fetch_funding()
    app.bot_data["funding_data"] = data

    for info in data:
        symbol = info.get("symbol")
        interval = info.get("fundingInterval")
        rate_raw = info.get("fundingRate")

        # Se mancano dati fondamentali, salta la coppia
        if symbol is None or interval is None or rate_raw is None:
            continue

        try:
            rate = float(rate_raw) * 100
        except:
            continue

        alert = process_funding(symbol, rate, interval)
        if alert:
            await app.bot.send_message(chat_id=CHAT_ID, text=alert)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status_new", status_new))
    app.add_handler(CommandHandler("funding_1h", funding_1h))
    app.add_handler(CommandHandler("funding_2h", funding_2h))
    app.add_handler(CommandHandler("short", short))
    app.add_handler(CommandHandler("long", long))

    # Job scheduler compatibile con Python 3.12
    app.job_queue.run_repeating(lambda ctx: funding_job(app), interval=60, first=5)

    # Modalità compatibile con Python 3.12 (senza asyncio.run)
    app.run_polling()


if __name__ == "__main__":
    main()

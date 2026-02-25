import asyncio
import aiohttp
from telegram.ext import ApplicationBuilder, CommandHandler
from commands import start, status_new, funding_1h, funding_2h, short, long
from alert_logic import process_funding

BOT_TOKEN = "INSERISCI_IL_TUO_TOKEN"
CHAT_ID = 444059323   # <-- sostituisci con il tuo chat_id Telegram


async def fetch_funding():
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["result"]["list"]


async def funding_job(context):
    data = await fetch_funding()
    context.bot_data["funding_data"] = data

    for info in data:
        symbol = info["symbol"]
        rate = float(info["fundingRate"]) * 100
        interval = info["fundingInterval"]

        alert = process_funding(symbol, rate, interval)
        if alert:
            await context.bot.send_message(chat_id=CHAT_ID, text=alert)


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi Telegram
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status_new", status_new))
    app.add_handler(CommandHandler("funding_1h", funding_1h))
    app.add_handler(CommandHandler("funding_2h", funding_2h))
    app.add_handler(CommandHandler("short", short))
    app.add_handler(CommandHandler("long", long))

    # Job ogni 60 secondi
    app.job_queue.run_repeating(funding_job, interval=60, first=5)

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())

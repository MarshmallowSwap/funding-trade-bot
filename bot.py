import os
import aiohttp
import logging
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)
from commands import (
    start,
    status_new,
    status_extreme,
    funding_1h,
    funding_2h,
    short,
    long,
    funding_all,
    funding_top,
    funding_bottom,
    funding_alerts
)
from alert_logic import process_funding

load_dotenv()

BOT_TOKEN = os.getenv("8656121150:AAF75HnH_5czbk82DEdDiihy5i3sdjjsJaI")
CHAT_ID = os.getenv("444059323")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def fetch_funding():
    url = "https://api.bybit.com/v5/market/funding/history?category=linear&limit=200"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["result"]["list"]

async def funding_job(app):
    try:
        data = await fetch_funding()
        app.bot_data["funding_data"] = data

        for item in data:
            symbol = item.get("symbol")
            rate_raw = item.get("fundingRate")

            if rate_raw is None:
                continue

            try:
                rate = float(rate_raw) * 100
            except:
                continue

            alert = process_funding(symbol, rate)
            if alert:
                await app.bot.send_message(chat_id=CHAT_ID, text=alert)

    except Exception as e:
        logging.error(f"Errore nel funding job: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status_new", status_new))
    app.add_handler(CommandHandler("status_extreme", status_extreme))
    app.add_handler(CommandHandler("funding_1h", funding_1h))
    app.add_handler(CommandHandler("funding_2h", funding_2h))
    app.add_handler(CommandHandler("short", short))
    app.add_handler(CommandHandler("long", long))
    app.add_handler(CommandHandler("funding_all", funding_all))
    app.add_handler(CommandHandler("funding_top", funding_top))
    app.add_handler(CommandHandler("funding_bottom", funding_bottom))
    app.add_handler(CommandHandler("funding_alerts", funding_alerts))

    app.job_queue.run_repeating(lambda ctx: funding_job(app), interval=60, first=5)

    app.run_polling()

if __name__ == "__main__":
    main()

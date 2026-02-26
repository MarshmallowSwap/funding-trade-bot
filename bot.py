import os
import logging
import asyncio
import aiohttp
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
    funding_alerts,
    account_info,
)
from alert_logic import process_funding
from bybit_client import BybitClient

load_dotenv()

BOT_TOKEN = os.getenv("8656121150:AAF75HnH_5czbk82DEdDiihy5i3sdjjsJaI")
CHAT_ID = os.getenv("444059323")

BYBIT_API_KEY = os.getenv("oiPPz5vhsRmgz08jYR")
BYBIT_API_SECRET = os.getenv("vzfJlxj2bz32fpnOpfvilEk8xrP6g1MrxnZE")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_TOKEN mancante nel file .env")
if not CHAT_ID:
    raise ValueError("CHAT_ID mancante nel file .env")

bybit_client = BybitClient(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
)


async def fetch_funding():
    url = "https://api.bybit.com/v5/market/funding/history?category=linear&limit=200"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
                return data["result"]["list"]
    except Exception as e:
        logging.error(f"Errore API Bybit (funding): {e}")
        return []


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
            except Exception:
                continue

            alert = process_funding(symbol, rate)
            if alert:
                await app.bot.send_message(chat_id=CHAT_ID, text=alert)

    except Exception as e:
        logging.error(f"Errore nel funding job: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi base
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

    # Comando che usa API private Bybit
    app.add_handler(CommandHandler("account", account_info, block=False))

    # Job funding periodico
    app.job_queue.run_repeating(
        lambda ctx: asyncio.create_task(funding_job(app)),
        interval=60,
        first=5,
    )

    # Metto il client Bybit in bot_data per usarlo nei comandi
    app.bot_data["bybit_client"] = bybit_client

    app.run_polling()


if __name__ == "__main__":
    main()

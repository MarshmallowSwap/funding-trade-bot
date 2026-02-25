import asyncio
import logging
import os
import time

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from alert_logic import get_full_snapshot, classify_funding, last_reset_timestamp
from commands import (
    start,
    status_extreme,
    status_new,
    funding_1h,
    funding_2h,
    short_cmd,
    long_cmd,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def _contrarian_label(fr: float) -> str:
    return "SHORT" if fr > 0 else "LONG"


def _fmt_pct(fr: float) -> str:
    return f"{fr * 100:.2f}%"


async def alert_job(app):
    """
    Job periodico:
    - legge funding
    - calcola alert/extreme/rientri/cambi intervallo
    - rispetta i 90s dopo reset funding
    """
    tickers, infos = get_full_snapshot()
    data = classify_funding(tickers, infos)

    now = time.time()

    # 1) Extreme
    if data["extremes"]:
        lines = ["🔥 Funding Estremo\n"]
        for symbol, fr, interval in sorted(data["extremes"], key=lambda x: abs(x[1]), reverse=True):
            lines.append(
                f"{symbol}\n"
                f"Rate: {_fmt_pct(fr)}\n"
                f"Interval: {interval}\n"
                f"Contrarian: {_contrarian_label(fr)}\n"
            )
        await app.bot.send_message(chat_id=CHAT_ID, text="\n".join(lines))

    # 2) Alert > 1%
    if data["alerts"]:
        lines = ["🚨 Funding Alto/Basso\n"]
        for symbol, fr, interval in sorted(data["alerts"], key=lambda x: abs(x[1]), reverse=True):
            label = "Alto" if fr > 0 else "Basso"
            lines.append(
                f"{symbol} ({label})\n"
                f"Rate: {_fmt_pct(fr)}\n"
                f"Interval: {interval}\n"
                f"Contrarian: {_contrarian_label(fr)}\n"
            )
        await app.bot.send_message(chat_id=CHAT_ID, text="\n".join(lines))

    # 3) Rientri
    if data["recovered"]:
        lines = ["ℹ️ Funding Rientrato\n"]
        for symbol, fr in data["recovered"]:
            lines.append(
                f"{symbol} ora è sotto 0.50%\n"
                f"Rate attuale: {_fmt_pct(fr)}\n"
                f"Contrarian: {_contrarian_label(fr)} (non più in zona alert)\n"
            )
        await app.bot.send_message(chat_id=CHAT_ID, text="\n".join(lines))

    # 4) Cambi intervallo (rispettando i 90s dopo reset funding)
    if data["interval_changes"]:
        lines = ["⚠️ Cambio Intervallo Funding\n"]
        for symbol, prev_int, new_int, fr in data["interval_changes"]:
            last_reset = last_reset_timestamp.get(symbol, 0)
            if last_reset and (now - last_reset) < 90:
                continue
            lines.append(
                f"{symbol}: {prev_int} → {new_int}\n"
                f"Rate attuale: {_fmt_pct(fr)}\n"
                f"Contrarian: {_contrarian_label(fr)}\n"
            )
        if len(lines) > 1:
            await app.bot.send_message(chat_id=CHAT_ID, text="\n".join(lines))


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN non impostato nel .env")
    if not CHAT_ID:
        raise RuntimeError("CHAT_ID non impostato nel .env")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status_extreme", status_extreme))
    app.add_handler(CommandHandler("status_new", status_new))
    app.add_handler(CommandHandler("funding_1h", funding_1h))
    app.add_handler(CommandHandler("funding_2h", funding_2h))
    app.add_handler(CommandHandler("short", short_cmd))
    app.add_handler(CommandHandler("long", long_cmd))

    # Job periodico ogni 60s
    app.job_queue.run_repeating(
        lambda *_: asyncio.create_task(alert_job(app)),
        interval=60,
        first=10,
    )

    app.run_polling()


if __name__ == "__main__":
    main()

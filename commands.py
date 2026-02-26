from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Bot attivo ✅\n\n"
        "Comandi disponibili:\n"
        "/status_new\n"
        "/status_extreme\n"
        "/funding_all\n"
        "/funding_top\n"
        "/funding_bottom\n"
        "/funding_alerts\n"
        "/account (richiede API Bybit private)"
    )
    await update.message.reply_text(msg)


async def status_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    await update.message.reply_text(f"Ultimi funding caricati: {len(data)} elementi.")


async def status_extreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    extremes = [d for d in data if abs(float(d.get("fundingRate", 0)) * 100) >= 0.75]
    await update.message.reply_text(f"Funding estremi trovati: {len(extremes)}.")


async def funding_1h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funding 1h: funzione placeholder.")


async def funding_2h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funding 2h: funzione placeholder.")


async def short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Short alert: funzione placeholder.")


async def long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Long alert: funzione placeholder.")


async def funding_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    if not data:
        await update.message.reply_text("Nessun dato funding disponibile al momento.")
        return

    lines = []
    for d in data[:30]:
        symbol = d.get("symbol")
        rate = float(d.get("fundingRate", 0)) * 100
        lines.append(f"{symbol}: {rate:.4f}%")

    await update.message.reply_text("\n".join(lines))


async def funding_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    if not data:
        await update.message.reply_text("Nessun dato funding disponibile.")
        return

    sorted_data = sorted(
        data,
        key=lambda x: float(x.get("fundingRate", 0)),
        reverse=True,
    )
    lines = []
    for d in sorted_data[:10]:
        symbol = d.get("symbol")
        rate = float(d.get("fundingRate", 0)) * 100
        lines.append(f"{symbol}: {rate:.4f}%")

    await update.message.reply_text("TOP funding:\n" + "\n".join(lines))


async def funding_bottom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    if not data:
        await update.message.reply_text("Nessun dato funding disponibile.")
        return

    sorted_data = sorted(
        data,
        key=lambda x: float(x.get("fundingRate", 0)),
    )
    lines = []
    for d in sorted_data[:10]:
        symbol = d.get("symbol")
        rate = float(d.get("fundingRate", 0)) * 100
        lines.append(f"{symbol}: {rate:.4f}%")

    await update.message.reply_text("BOTTOM funding:\n" + "\n".join(lines))


async def funding_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gli alert funding vengono inviati automaticamente ogni minuto.")


async def account_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bybit_client = context.application.bot_data.get("bybit_client")
    if not bybit_client or not bybit_client.has_keys:
        await update.message.reply_text(
            "API Bybit private non configurate.\n"
            "Aggiungi BYBIT_API_KEY e BYBIT_API_SECRET nel file .env."
        )
        return

    balance = await bybit_client.get_wallet_balance()
    if balance is None:
        await update.message.reply_text("Impossibile recuperare il saldo Bybit.")
        return

    msg_lines = ["Saldo Bybit:"]
    for coin, info in balance.items():
        msg_lines.append(f"{coin}: {info.get('walletBalance', '0')}")

    await update.message.reply_text("\n".join(msg_lines))

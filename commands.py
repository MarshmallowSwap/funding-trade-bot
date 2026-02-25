from telegram import Update
from telegram.ext import ContextTypes
from alert_logic import interval_to_hours

def format_symbol_info(info):
    rate = float(info["fundingRate"]) * 100
    interval = interval_to_hours(info["fundingInterval"])
    return f"{info['symbol']} — {rate:.2f}% — Funding: {interval}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto! Comandi disponibili:\n"
        "/status_new\n"
        "/funding_1h\n"
        "/funding_2h\n"
        "/short\n"
        "/long\n"
    )

async def status_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data.get("funding_data", [])
    new_pairs = []

    for info in data:
        if "launchTime" in info:
            try:
                days = (datetime.utcnow() - datetime.fromtimestamp(int(info["launchTime"]) / 1000)).days
                if days < 7:
                    new_pairs.append(format_symbol_info(info))
            except:
                pass

    if not new_pairs:
        await update.message.reply_text("Nessuna coppia NEW.")
    else:
        await update.message.reply_text("\n".join(new_pairs))

async def funding_1h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data.get("funding_data", [])
    pairs = [format_symbol_info(i) for i in data if i["fundingInterval"] == "60"]

    if not pairs:
        await update.message.reply_text("Nessuna coppia con funding a 1h.")
    else:
        await update.message.reply_text("\n".join(pairs))

async def funding_2h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data.get("funding_data", [])
    pairs = [format_symbol_info(i) for i in data if i["fundingInterval"] == "120"]

    if not pairs:
        await update.message.reply_text("Nessuna coppia con funding a 2h.")
    else:
        await update.message.reply_text("\n".join(pairs))

async def short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data.get("funding_data", [])
    pairs = [format_symbol_info(i) for i in data if float(i["fundingRate"]) > 0]

    if not pairs:
        await update.message.reply_text("Nessuna coppia con funding positivo.")
    else:
        await update.message.reply_text("\n".join(pairs))

async def long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.bot_data.get("funding_data", [])
    pairs = [format_symbol_info(i) for i in data if float(i["fundingRate"]) < 0]

    if not pairs:
        await update.message.reply_text("Nessuna coppia con funding negativo.")
    else:
        await update.message.reply_text("\n".join(pairs))

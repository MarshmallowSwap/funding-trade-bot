from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot attivo! Usa /status_new o /funding_all.")

async def status_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    await update.message.reply_text(f"Ultimi funding: {len(data)} elementi.")

async def status_extreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funzione in sviluppo.")

async def funding_1h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funding 1h in arrivo.")

async def funding_2h(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Funding 2h in arrivo.")

async def short(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Short alert.")

async def long(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Long alert.")

async def funding_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.application.bot_data.get("funding_data", [])
    msg = "\n".join([f"{d['symbol']}: {d['fundingRate']}" for d in data[:20]])
    await update.message.reply_text(msg)

async def funding_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Top funding.")

async def funding_bottom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bottom funding.")

async def funding_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Alert attivi.")

# Funding Trade – @strategiesinc_bot

Bot Telegram per monitorare i funding delle coppie **Perpetual USDT** su Bybit e generare alert contrarian (LONG/SHORT).

## Funzioni principali

- Alert automatici:
  - Funding oltre ±1.00%
  - Extreme oltre ±1.50%
  - Rientro sotto ±0.50%
  - Cambio intervallo funding (es. 4h → 1h), con attesa 90s dopo reset

- Comandi:
  - `/start`
  - `/status_extreme`
  - `/status_new`
  - `/funding_1h`
  - `/funding_2h`
  - `/short`
  - `/long`

## Setup

```bash
git clone <repo> funding-trade-bot
cd funding-trade-bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# modifica .env con TELEGRAM_TOKEN, CHAT_ID, BYBIT_API_KEY, BYBIT_API_SECRET

python3 bot.py

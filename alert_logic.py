import json
import os
from datetime import datetime

STATE_FILE = "alert_state.json"

# Carica stato da disco
def load_state():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            f.write("{}")
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Salva stato su disco (compatto)
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, separators=(",", ":"))

# Converte intervallo minuti → ore
def interval_to_hours(interval_str):
    try:
        minutes = int(interval_str)
        return f"{minutes // 60}h"
    except:
        return "?"

# Determina contrarian + emoji
def get_contrarian(rate):
    if rate < 0:
        return "LONG 🟢"
    else:
        return "SHORT 🔴"

# Determina stato funding
def classify_rate(rate):
    if rate <= -1.5:
        return "extreme_basso"
    if rate >= 1.5:
        return "extreme_alto"
    if rate <= -1:
        return "basso"
    if rate >= 1:
        return "alto"
    if -0.75 <= rate <= 0.75:
        return "rientro"
    if -0.25 <= rate <= 0.25:
        return "chiusura"
    return "neutro"

# Messaggi alert
def build_alert(symbol, rate, interval_hours, state):
    contrarian = get_contrarian(rate)

    if state == "extreme_basso":
        return f"🔥 Funding Estremo (Basso)\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    if state == "extreme_alto":
        return f"🔥 Funding Estremo (Alto)\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    if state == "basso":
        return f"🚨 Funding Basso\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    if state == "alto":
        return f"🚨 Funding Alto\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    if state == "rientro":
        return f"ℹ️ Funding Rientrato\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    if state == "chiusura":
        return f"ℹ️ Consiglio Chiusura\n{symbol}\nRate: {rate:.2f}%\nFunding: {interval_hours}\nContrarian: {contrarian}"

    return None

# Logica principale
def process_funding(symbol, rate, interval_str):
    state = load_state()
    interval_hours = interval_to_hours(interval_str)

    new_state = classify_rate(rate)
    old_state = state.get(symbol, {}).get("state")

    if new_state == old_state:
        return None

    alert_msg = build_alert(symbol, rate, interval_hours, new_state)

    state[symbol] = {
        "state": new_state,
        "last_rate": rate,
        "last_alert": datetime.utcnow().isoformat()
    }
    save_state(state)

    return alert_msg

import time
import requests
from typing import List, Dict, Tuple

BYBIT_PERP_TICKERS = "https://api.bybit.com/v5/market/tickers"
BYBIT_PERP_INFO = "https://api.bybit.com/v5/market/instruments-info"

# Stato interno per evitare spam
alerted_over_1 = set()
alerted_extreme = set()
previous_intervals = {}
last_reset_timestamp = {}  # symbol -> last funding reset timestamp (epoch)


def _fetch_perp_tickers() -> List[Dict]:
    """
    Recupera tutti i ticker linear (perpetual) da Bybit.
    """
    params = {"category": "linear"}
    r = requests.get(BYBIT_PERP_TICKERS, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("result", {}).get("list", [])


def _fetch_instruments_info() -> List[Dict]:
    """
    Recupera info strumenti (per NEW, listing time, funding interval, ecc.).
    """
    params = {"category": "linear"}
    r = requests.get(BYBIT_PERP_INFO, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data.get("result", {}).get("list", [])


def _is_perp_usdt(info: Dict) -> bool:
    """
    Filtra solo perpetual USDT.
    """
    quote = info.get("quoteCoin")
    contract_type = info.get("contractType")
    return quote == "USDT" and contract_type == "LinearPerpetual"


def _parse_funding_rate(ticker: Dict) -> float:
    """
    Ritorna il funding rate come float (es. 0.0123 = 1.23%).
    """
    fr = ticker.get("fundingRate")
    if fr is None:
        return 0.0
    try:
        return float(fr)
    except ValueError:
        return 0.0


def _parse_interval(info: Dict) -> str:
    """
    Ritorna l'intervallo di funding come stringa (es. '1h', '4h', '8h').
    """
    interval = info.get("fundingInterval")
    if not interval:
        return "unknown"
    return interval


def _parse_listing_age_days(info: Dict) -> float:
    """
    Calcola da quanto tempo è listata la coppia (in giorni).
    """
    listing_ts = info.get("launchTime") or info.get("listTime")
    if not listing_ts:
        return 9999.0
    try:
        ts = int(listing_ts) / 1000  # ms -> s
    except ValueError:
        return 9999.0
    now = time.time()
    return (now - ts) / 86400.0


def _is_new_pair(info: Dict) -> bool:
    """
    Coppia considerata NEW se:
    - meno di 7 giorni
    - oppure tag NEW (se presente nei dati)
    """
    age_days = _parse_listing_age_days(info)
    if age_days < 7:
        return True

    tags = info.get("symbolType") or ""
    if isinstance(tags, str) and "NEW" in tags.upper():
        return True

    return False


def get_full_snapshot() -> Tuple[List[Dict], List[Dict]]:
    """
    Ritorna:
    - lista ticker (funding, last price, ecc.)
    - lista info strumenti (interval, listing, ecc.)
    filtrate solo per perpetual USDT.
    """
    tickers = _fetch_perp_tickers()
    infos = _fetch_instruments_info()

    infos_map = {
        i["symbol"]: i
        for i in infos
        if _is_perp_usdt(i)
    }

    filtered_tickers = [
        t for t in tickers
        if t.get("symbol") in infos_map
    ]

    return filtered_tickers, list(infos_map.values())


def classify_funding(tickers: List[Dict], infos: List[Dict]):
    """
    Calcola:
    - alert > ±1%
    - extreme > ±1.5%
    - rientri < ±0.5%
    - cambi intervallo
    - funding 1h / 2h
    - coppie nuove
    """
    info_map = {i["symbol"]: i for i in infos}

    alerts = []
    extremes = []
    recovered = []
    interval_changes = []
    funding_1h = []
    funding_2h = []
    new_pairs = []

    for t in tickers:
        symbol = t.get("symbol")
        info = info_map.get(symbol, {})
        fr = _parse_funding_rate(t)
        interval = _parse_interval(info)

        # NEW
        if _is_new_pair(info):
            new_pairs.append(symbol)

        # Funding 1h / 2h
        if interval == "1h":
            funding_1h.append((symbol, fr))
        elif interval == "2h":
            funding_2h.append((symbol, fr))

        # Cambio intervallo
        prev_int = previous_intervals.get(symbol)
        if prev_int is not None and prev_int != interval:
            interval_changes.append((symbol, prev_int, interval, fr))
        previous_intervals[symbol] = interval

        # Reset funding (soft): se funding ~ 0, segniamo timestamp
        if abs(fr) < 1e-6:
            last_reset_timestamp[symbol] = time.time()

        abs_fr_pct = abs(fr) * 100.0

        # Extreme
        if abs_fr_pct >= 1.5:
            extremes.append((symbol, fr, interval))
            alerted_extreme.add(symbol)
            alerted_over_1.add(symbol)
            continue

        # Alert > 1%
        if abs_fr_pct >= 1.0:
            alerts.append((symbol, fr, interval))
            alerted_over_1.add(symbol)
            continue

        # Rientro < 0.5% se era sopra 1%
        if symbol in alerted_over_1 and abs_fr_pct <= 0.5:
            recovered.append((symbol, fr))
            if symbol in alerted_extreme:
                alerted_extreme.remove(symbol)
            alerted_over_1.remove(symbol)

    return {
        "alerts": alerts,
        "extremes": extremes,
        "recovered": recovered,
        "interval_changes": interval_changes,
        "funding_1h": funding_1h,
        "funding_2h": funding_2h,
        "new_pairs": new_pairs,
    }

from typing import List, Tuple
from telegram import Update
from telegram.ext import ContextTypes

from alert_logic import get_full_snapshot, classify_funding, _is_new_pair, _is_perp_usdt


def _contrarian_label(fr: float) -> str:
    return "SHORT" if fr > 0 else "LONG"


def _fmt_pct(fr: float) -> str:
    return f"{fr * 100:.2f}%"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "Funding Trade – @strategiesinc_bot\n\n"
        "Bot attivo.\n\n"
        "/status_extreme — Funding oltre ±1.50%\n"
        "/status_new — Coppie nuove (<7 giorni / NEW)\n"
        "/funding_1h — Coppie con funding a 1h\n"
        "/funding_2h — Coppie con funding a 2h\n"
        "/short — Coppie con funding positivo (Contrarian SHORT)\n"
        "/long — Coppie con funding negativo (Contrarian LONG)\n"
    )
    await update.message.reply_text(text)


async def status_extreme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tickers, infos = get_full_snapshot()
    data = classify_funding(tickers, infos)
    extremes: List[Tuple[str, float, str]] = data["extremes"]

    if not extremes:
        await update.message.reply_text("Nessun funding estremo oltre ±1.50% al momento.")
        return

    lines = ["🔥 Funding Estremi Attuali\n"]
    for symbol, fr, interval in sorted(extremes, key=lambda x: abs(x[1]), reverse=True):
        lines.append(
            f"{symbol}\n"
            f"Rate: {_fmt_pct(fr)}\n"
            f"Interval: {interval}\n"
            f"Contrarian: {_contrarian_label(fr)}\n"
        )

    await update.message.reply_text("\n".join(lines))


async def status_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _, infos = get_full_snapshot()

    new_list = []
    for info in infos:
        if not _is_perp_usdt(info):
            continue
        if _is_new_pair(info):
            new_list.append(info["symbol"])

    if not new_list:
        await update.message.reply_text("Nessuna coppia NEW o con meno di 7 giorni.")
        return

    lines = ["🆕 Coppie Nuove (Perpetual USDT)\n"]
    for s in sorted(new_list):
        lines.append(s)

    await update.message.reply_text("\n".join(lines))


async def funding_1h(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tickers, infos = get_full_snapshot()
    data = classify_funding(tickers, infos)
    funding_1h: List[Tuple[str, float]] = data["funding_1h"]

    if not funding_1h:
        await update.message.reply_text("Nessuna coppia con funding a 1h.")
        return

    lines = ["⏱ Funding 1h\n"]
    for symbol, fr in sorted(funding_1h, key=lambda x: abs(x[1]), reverse=True):
        lines.append(f"{symbol} — {_fmt_pct(fr)} → {_contrarian_label(fr)}")

    await update.message.reply_text("\n".join(lines))


async def funding_2h(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tickers, infos = get_full_snapshot()
    data = classify_funding(tickers, infos)
    funding_2h: List[Tuple[str, float]] = data["funding_2h"]

    if not funding_2h:
        await update.message.reply_text("Nessuna coppia con funding a 2h.")
        return

    lines = ["⏱ Funding 2h\n"]
    for symbol, fr in sorted(funding_2h, key=lambda x: abs(x[1]), reverse=True):
        lines.append(f"{symbol} — {_fmt_pct(fr)} → {_contrarian_label(fr)}")

    await update.message.reply_text("\n".join(lines))


async def short_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tickers, infos = get_full_snapshot()
    _ = classify_funding(tickers, infos)  # per aggiornare stato interno se serve

    candidates = []
    for t in tickers:
        symbol = t["symbol"]
        fr_raw = t.get("fundingRate") or "0"
        try:
            fr = float(fr_raw)
        except ValueError:
            continue
        if fr > 0:
            abs_pct = abs(fr) * 100
            tag = ""
            if abs_pct >= 1.5:
                tag = " (ESTREMO)"
            elif abs_pct >= 1.0:
                tag = " (ALERT)"
            candidates.append((symbol, fr, tag))

    if not candidates:
        await update.message.reply_text("Nessuna coppia con funding positivo (Contrarian SHORT).")
        return

    lines = ["📉 SHORT (Contrarian)\n"]
    for symbol, fr, tag in sorted(candidates, key=lambda x: abs(x[1]), reverse=True):
        lines.append(f"{symbol} — {_fmt_pct(fr)}{tag}")

    await update.message.reply_text("\n".join(lines))


async def long_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tickers, infos = get_full_snapshot()
    _ = classify_funding(tickers, infos)

    candidates = []
    for t in tickers:
        symbol = t["symbol"]
        fr_raw = t.get("fundingRate") or "0"
        try:
            fr = float(fr_raw)
        except ValueError:
            continue
        if fr < 0:
            abs_pct = abs(fr) * 100
            tag = ""
            if abs_pct >= 1.5:
                tag = " (ESTREMO)"
            elif abs_pct >= 1.0:
                tag = " (ALERT)"
            candidates.append((symbol, fr, tag))

    if not candidates:
        await update.message.reply_text("Nessuna coppia con funding negativo (Contrarian LONG).")
        return

    lines = ["📈 LONG (Contrarian)\n"]
    for symbol, fr, tag in sorted(candidates, key=lambda x: abs(x[1]), reverse=True):
        lines.append(f"{symbol} — {_fmt_pct(fr)}{tag}")

    await update.message.reply_text("\n".join(lines))

ALERT_THRESHOLDS = {
    "extreme_high": 0.75,   # funding > +0.75%
    "high":         0.50,   # funding > +0.50%
    "extreme_low": -0.75,   # funding < -0.75%
    "low":         -0.50,   # funding < -0.50%
}


def classify_funding(rate: float) -> str | None:
    if rate >= ALERT_THRESHOLDS["extreme_high"]:
        return "extreme_high"
    if rate >= ALERT_THRESHOLDS["high"]:
        return "high"
    if rate <= ALERT_THRESHOLDS["extreme_low"]:
        return "extreme_low"
    if rate <= ALERT_THRESHOLDS["low"]:
        return "low"
    return None


def format_alert(symbol: str, rate: float, level: str) -> str:
    base = f"{symbol} funding: {rate:.3f}%"

    if level == "extreme_high":
        return f"🚨 EXTREME HIGH FUNDING\n{base}\nPossibile eccesso di long."
    if level == "high":
        return f"⚠️ HIGH FUNDING\n{base}\nAttenzione ai long."
    if level == "extreme_low":
        return f"🚨 EXTREME LOW FUNDING\n{base}\nPossibile eccesso di short."
    if level == "low":
        return f"⚠️ LOW FUNDING\n{base}\nAttenzione agli short."

    return base


def process_funding(symbol: str, rate: float) -> str | None:
    level = classify_funding(rate)
    if not level:
        return None
    return format_alert(symbol, rate, level)

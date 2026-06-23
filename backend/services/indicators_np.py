"""Indicator computation without pandas — pure Python/numpy.

This is a drop-in replacement for services/indicators.py that
avoids pandas DataFrame creation in request handlers to prevent
segfaults from pandas+numpy GC interactions in gunicorn workers.
"""


def _to_float(v):
    if v is None:
        return None
    return round(float(v), 4)


def ema(values, span):
    """Exponential moving average."""
    if not values or len(values) == 0:
        return []
    alpha = 2.0 / (span + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(alpha * v + (1 - alpha) * result[-1])
    return result


def sma(values, window):
    """Simple moving average."""
    if not values or len(values) < window:
        return [None] * len(values)
    result = []
    cum = sum(values[:window])
    result.append(cum / window)
    for i in range(window, len(values)):
        cum += values[i] - values[i - window]
        result.append(cum / window)
    return [None] * (window - 1) + result


def compute_rsi(closes):
    if not closes or len(closes) < 15:
        return [None] * len(closes) if closes else []
    result = [None] * 14
    gains, losses = 0.0, 0.0
    for i in range(1, 15):
        diff = closes[i] - closes[i - 1]
        if diff > 0:
            gains += diff
        else:
            losses -= diff
    avg_gain = gains / 14
    avg_loss = losses / 14
    if avg_loss > 0:
        rs = avg_gain / avg_loss
        result.append(round(100 - (100 / (1 + rs)), 4))
    else:
        result.append(round(100.0 if avg_gain > 0 else 50.0, 4))

    for i in range(15, len(closes)):
        diff = closes[i] - closes[i - 1]
        gain = diff if diff > 0 else 0
        loss = -diff if diff < 0 else 0
        avg_gain = (avg_gain * 13 + gain) / 14
        avg_loss = (avg_loss * 13 + loss) / 14
        if avg_loss > 0:
            rs = avg_gain / avg_loss
            result.append(round(100 - (100 / (1 + rs)), 4))
        else:
            result.append(round(100.0 if avg_gain > 0 else 50.0, 4))
    return result


def compute_macd(closes):
    if not closes or len(closes) < 35:
        empty = [None] * len(closes) if closes else []
        return {"macd_line": empty[:], "signal_line": empty[:], "histogram": empty[:]}
    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line = [ema12[i] - ema26[i] for i in range(len(closes))]
    signal_line = ema(macd_line, 9)
    histogram = [macd_line[i] - signal_line[i] for i in range(len(closes))]
    return {
        "macd_line": [_to_float(v) for v in macd_line],
        "signal_line": [_to_float(v) for v in signal_line],
        "histogram": [_to_float(v) for v in histogram],
    }


def compute_bollinger(closes, window=20):
    if not closes or len(closes) < window:
        empty = [None] * len(closes) if closes else []
        return {"upper": empty[:], "middle": empty[:], "lower": empty[:], "percent_b": empty[:], "bandwidth": empty[:]}
    middle = sma(closes, window)
    upper, lower, percent_b, bandwidth = [], [], [], []
    for i in range(len(closes)):
        m = middle[i]
        if m is None or i < window - 1:
            upper.append(None)
            lower.append(None)
            percent_b.append(None)
            bandwidth.append(None)
        else:
            subset = closes[i - window + 1:i + 1]
            std = (sum((x - m) ** 2 for x in subset) / window) ** 0.5
            u = m + 2 * std
            lw = m - 2 * std
            upper.append(round(u, 4))
            lower.append(round(lw, 4))
            pb = round((closes[i] - lw) / (u - lw), 4) if (u - lw) > 0 else 0.5
            percent_b.append(pb)
            bw = round((u - lw) / m * 100, 4) if m else None
            bandwidth.append(bw)
    return {"upper": upper, "middle": middle, "lower": lower, "percent_b": percent_b, "bandwidth": bandwidth}


def compute_volume_analysis(volumes, closes):
    result = {"volume_ratio": None, "avg_volume_20": None, "avg_volume_10": None}
    if not volumes or not closes or len(volumes) < 2:
        return result
    if len(volumes) >= 10:
        avg10 = sum(volumes[-10:]) / 10
        result["avg_volume_10"] = round(avg10, 1)
    if len(volumes) >= 20:
        avg20 = sum(volumes[-20:]) / 20
        result["avg_volume_20"] = round(avg20, 1)
    else:
        avg20 = sum(volumes) / len(volumes)
        result["avg_volume_20"] = round(avg20, 1)
    current_vol = volumes[-1]
    if result["avg_volume_20"] and result["avg_volume_20"] > 0:
        result["volume_ratio"] = round(current_vol / result["avg_volume_20"], 2)
    else:
        result["volume_ratio"] = None
    return result


def compute_all_indicators(dates, opens, highs, lows, closes, volumes):
    if not closes or len(closes) < 10:
        return {"dates": dates or [], "close": closes or [], "latest": {}}

    rsi = compute_rsi(closes)
    macd = compute_macd(closes)
    bb = compute_bollinger(closes)
    vol = compute_volume_analysis(volumes, closes)

    sma_10 = sma(closes, 10)
    sma_20 = sma(closes, 20)
    sma_50 = sma(closes, 50)
    sma_200 = sma(closes, 200)
    ema_10 = ema(closes, 10)
    ema_20 = ema(closes, 20)
    ema_50 = ema(closes, 50)
    ema_200 = ema(closes, 200)

    def _slope(arr, w=5):
        vals = [v for v in arr if v is not None]
        if len(vals) < w:
            return None
        n = len(vals)
        x_bar = (w - 1) / 2
        y_bar = sum(vals[-w:]) / w
        num = sum((i - x_bar) * (vals[-w + i] - y_bar) for i in range(w))
        den = sum((i - x_bar) ** 2 for i in range(w))
        return round(num / den, 4) if den != 0 else None

    price = round(float(closes[-1]), 2) if closes else None
    price_change_pct = None
    if len(closes) >= 2 and closes[-2]:
        price_change_pct = round((closes[-1] - closes[-2]) / closes[-2] * 100, 2)

    def _latest(arr):
        for v in reversed(arr):
            if v is not None:
                return v
        return None

    def _prev(arr):
        found = 0
        for v in reversed(arr):
            if v is not None:
                if found == 1:
                    return v
                found += 1
        return None

    bb_upper, bb_middle, bb_lower = bb["upper"], bb["middle"], bb["lower"]
    bb_bandwidth = bb["bandwidth"]
    bb_percent_b = bb["percent_b"]

    bb_squeeze = False
    bw = _latest(bb_bandwidth)
    if bw is not None:
        bb_squeeze = bw < 10.0

    latest = {
        "rsi": _latest(rsi),
        "macd_line": _latest(macd["macd_line"]),
        "signal_line": _latest(macd["signal_line"]),
        "histogram": _latest(macd["histogram"]),
        "histogram_prev": _prev(macd["histogram"]),
        "bb_upper": _latest(bb_upper),
        "bb_middle": _latest(bb_middle),
        "bb_lower": _latest(bb_lower),
        "bb_percent_b": _latest(bb_percent_b),
        "bb_bandwidth": _latest(bb_bandwidth),
        "bb_squeeze": bb_squeeze,
        "price": price,
        "price_change_pct": price_change_pct,
        "volume": volumes[-1] if volumes else None,
        "volume_ratio": vol["volume_ratio"],
        "avg_volume_10": vol["avg_volume_10"],
        "sma_10": _latest(sma_10),
        "sma_20": _latest(sma_20),
        "sma_50": _latest(sma_50),
        "sma_200": _latest(sma_200),
        "ema_10": _latest(ema_10),
        "ema_20": _latest(ema_20),
        "ema_50": _latest(ema_50),
        "ema_200": _latest(ema_200),
        "ema_10_slope": _slope(ema_10),
        "ema_20_slope": _slope(ema_20),
        "sma_50_slope": _slope(sma_50),
        "avg_volume_20": vol["avg_volume_20"],
    }

    return {
        "dates": dates or [],
        "close": closes or [],
        "volume": volumes or [],
        "rsi": rsi,
        "macd_line": macd["macd_line"],
        "signal_line": macd["signal_line"],
        "histogram": macd["histogram"],
        "bb_upper": [round(v, 4) if v is not None else None for v in bb_upper],
        "bb_middle": [round(v, 4) if v is not None else None for v in bb_middle],
        "bb_lower": [round(v, 4) if v is not None else None for v in bb_lower],
        "bb_percent_b": [_to_float(v) for v in bb_percent_b],
        "bb_bandwidth": [_to_float(v) for v in bb_bandwidth],
        "volume_ratio": vol["volume_ratio"],
        "avg_volume_20": vol["avg_volume_20"],
        "avg_volume_10": vol["avg_volume_10"],
        "sma_10": [_to_float(v) for v in sma_10],
        "sma_20": [_to_float(v) for v in sma_20],
        "sma_50": [_to_float(v) for v in sma_50],
        "sma_200": [_to_float(v) for v in sma_200],
        "ema_10": [_to_float(v) for v in ema_10],
        "ema_20": [_to_float(v) for v in ema_20],
        "latest": latest,
    }

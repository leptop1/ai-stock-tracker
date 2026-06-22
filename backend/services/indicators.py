import pandas as pd
import numpy as np

HAS_TA = False


def _series_to_list(s):
    if s is None:
        return []
    return [None if (v is None or (isinstance(v, float) and np.isnan(v))) else round(float(v), 4)
            for v in s]


def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    if len(df) < window + 1:
        return pd.Series([None] * len(df), index=df.index)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(df: pd.DataFrame) -> dict:
    if len(df) < 35:
        empty = pd.Series([None] * len(df), index=df.index)
        return {"macd_line": empty, "signal_line": empty, "histogram": empty}
    close = df["Close"]
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}


def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20) -> dict:
    if len(df) < window:
        empty = pd.Series([None] * len(df), index=df.index)
        return {"upper": empty, "middle": empty, "lower": empty, "percent_b": empty, "bandwidth": empty}
    close = df["Close"]
    middle = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = middle + 2 * std
    lower = middle - 2 * std
    percent_b = (close - lower) / (upper - lower).replace(0, np.nan)
    bandwidth = (upper - lower) / middle.replace(0, np.nan) * 100
    return {"upper": upper, "middle": middle, "lower": lower, "percent_b": percent_b, "bandwidth": bandwidth}


def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> dict:
    if len(df) < period:
        return {"supertrend": pd.Series([None] * len(df), index=df.index),
                "supertrend_direction": pd.Series([None] * len(df), index=df.index)}
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    hl_avg = (high + low) / 2
    upper_band = hl_avg + multiplier * atr
    lower_band = hl_avg - multiplier * atr
    supertrend = pd.Series([0.0] * len(df), index=df.index)
    direction = pd.Series([1] * len(df), index=df.index)
    for i in range(1, len(df)):
        if close.iloc[i] > upper_band.iloc[i - 1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower_band.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]
            if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i - 1]:
                lower_band.iloc[i] = lower_band.iloc[i - 1]
            if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i - 1]:
                upper_band.iloc[i] = upper_band.iloc[i - 1]
        supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
    return {"supertrend": supertrend, "supertrend_direction": direction, "atr": atr}


def calculate_moving_averages(df: pd.DataFrame) -> dict:
    result = {}
    for window in [10, 20, 50, 200]:
        col_sma = f"sma_{window}"
        col_ema = f"ema_{window}"
        result[col_sma] = df["Close"].rolling(window).mean()
        result[col_ema] = df["Close"].ewm(span=window, adjust=False).mean()
    return result


def calculate_volume_analysis(df: pd.DataFrame) -> dict:
    if len(df) < 2:
        return {"volume_ratio": None, "avg_volume_20": None, "avg_volume_10": None,
                "obv": pd.Series([], dtype=float),
                "volume_price_trend": pd.Series([], dtype=float)}
    avg_vol_10 = df["Volume"].rolling(10).mean()
    avg_vol_20 = df["Volume"].rolling(20).mean()
    current_vol = df["Volume"].iloc[-1]
    avg_vol_10_val = avg_vol_10.iloc[-1]
    avg_vol_20_val = avg_vol_20.iloc[-1]
    ratio_10 = float(current_vol / avg_vol_10_val) if avg_vol_10_val and avg_vol_10_val > 0 else None
    ratio_20 = float(current_vol / avg_vol_20_val) if avg_vol_20_val and avg_vol_20_val > 0 else None
    obv = None
    try:
        obv = (df["Volume"] * (df["Close"].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)))).cumsum()
    except Exception:
        pass
    vpt_values = [0.0]
    for i in range(1, len(df)):
        pct_change = (df["Close"].iloc[i] - df["Close"].iloc[i - 1]) / df["Close"].iloc[i - 1]
        vpt_values.append(vpt_values[-1] + pct_change * float(df["Volume"].iloc[i]))
    vpt_series = pd.Series(vpt_values, index=df.index)
    return {
        "volume_ratio": round(ratio_20, 2) if ratio_20 is not None else None,
        "avg_volume_20": float(avg_vol_20_val) if avg_vol_20_val is not None else None,
        "avg_volume_10": float(avg_vol_10_val) if avg_vol_10_val is not None else None,
        "obv": obv if obv is not None else pd.Series([None] * len(df), index=df.index),
        "volume_price_trend": vpt_series,
    }


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    if len(df) < period + 1:
        return pd.Series([None] * len(df), index=df.index)
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def calculate_all_indicators(df: pd.DataFrame) -> dict:
    rsi = calculate_rsi(df)
    macd = calculate_macd(df)
    bb = calculate_bollinger_bands(df)
    vol = calculate_volume_analysis(df)
    supertrend_data = calculate_supertrend(df)
    mas = calculate_moving_averages(df)
    atr = calculate_atr(df)

    dates = [str(d.date()) for d in df.index]

    latest_indicator = {
        "rsi": _latest(rsi),
        "macd_line": _latest(macd["macd_line"]),
        "signal_line": _latest(macd["signal_line"]),
        "histogram": _latest(macd["histogram"]),
        "histogram_prev": _prev(macd["histogram"]),
        "bb_upper": _latest(bb["upper"]),
        "bb_middle": _latest(bb["middle"]),
        "bb_lower": _latest(bb["lower"]),
        "bb_percent_b": _latest(bb["percent_b"]),
        "bb_bandwidth": _latest(bb["bandwidth"]),
        "bb_squeeze": _is_squeeze(bb["bandwidth"]),
        "price": round(float(df["Close"].iloc[-1]), 2) if len(df) > 0 else None,
        "price_change_pct": _price_change_pct(df),
        "volume": int(df["Volume"].iloc[-1]) if len(df) > 0 else None,
        "volume_ratio": vol["volume_ratio"],
        "avg_volume_10": vol["avg_volume_10"],
        "supertrend": _latest(supertrend_data["supertrend"]),
        "supertrend_direction": _latest_int(supertrend_data["supertrend_direction"]),
        "atr": _latest(atr),
    }

    for key, series in mas.items():
        latest_indicator[key] = _latest(series)
        if isinstance(series, pd.Series) and len(series) > 0:
            latest_indicator[f"{key}_slope"] = _series_slope(series)

    return {
        "dates": dates,
        "close": _series_to_list(df["Close"]),
        "volume": [int(v) for v in df["Volume"]],
        "rsi": _series_to_list(rsi),
        "macd_line": _series_to_list(macd["macd_line"]),
        "signal_line": _series_to_list(macd["signal_line"]),
        "histogram": _series_to_list(macd["histogram"]),
        "bb_upper": _series_to_list(bb["upper"]),
        "bb_middle": _series_to_list(bb["middle"]),
        "bb_lower": _series_to_list(bb["lower"]),
        "bb_percent_b": _series_to_list(bb["percent_b"]),
        "bb_bandwidth": _series_to_list(bb["bandwidth"]),
        "volume_ratio": vol["volume_ratio"],
        "avg_volume_20": vol["avg_volume_20"],
        "avg_volume_10": vol["avg_volume_10"],
        "obv": _series_to_list(vol["obv"]),
        "volume_price_trend": _series_to_list(vol["volume_price_trend"]),
        "supertrend": _series_to_list(supertrend_data["supertrend"]),
        "supertrend_direction": _series_to_list_int(supertrend_data["supertrend_direction"]),
        "atr": _series_to_list(atr),
        **{key: _series_to_list(series) for key, series in mas.items()},
        "latest": latest_indicator,
    }


def _series_slope(s, window=5):
    if s is None or len(s) < window:
        return None
    try:
        vals = s.dropna().tail(window)
        if len(vals) < window:
            return None
        x = np.arange(window)
        y = vals.values
        slope = np.polyfit(x, y, 1)[0]
        return round(float(slope), 4)
    except Exception:
        return None


def _latest(s):
    if s is None or len(s) == 0:
        return None
    val = s.dropna()
    if len(val) == 0:
        return None
    return round(float(val.iloc[-1]), 4)


def _latest_int(s):
    if s is None or len(s) == 0:
        return None
    val = s.dropna()
    if len(val) == 0:
        return None
    return int(val.iloc[-1])


def _prev(s):
    if s is None or len(s) < 2:
        return None
    val = s.dropna()
    if len(val) < 2:
        return None
    return round(float(val.iloc[-2]), 4)


def _is_squeeze(bandwidth_series):
    val = _latest(bandwidth_series)
    if val is None:
        return False
    return val < 10.0


def _series_to_list_int(s):
    if s is None:
        return []
    return [None if (v is None or (isinstance(v, float) and np.isnan(v))) else int(v)
            for v in s]


def _price_change_pct(df):
    if len(df) < 2:
        return None
    prev = float(df["Close"].iloc[-2])
    curr = float(df["Close"].iloc[-1])
    if prev == 0:
        return None
    return round((curr - prev) / prev * 100, 2)

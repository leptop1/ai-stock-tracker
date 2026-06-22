SIGNAL_WEIGHTS = {
    "rsi": 0.20,
    "macd": 0.20,
    "bollinger": 0.15,
    "volume": 0.10,
    "supertrend": 0.15,
    "ma_cross": 0.10,
    "trend": 0.10,
}


def interpret_rsi(rsi_value) -> tuple:
    if rsi_value is None:
        return "HOLD", 0.0
    if rsi_value < 30:
        return "BUY", 1.0
    if rsi_value < 40:
        return "BUY", 0.6
    if rsi_value <= 60:
        return "HOLD", 0.0
    if rsi_value <= 70:
        return "SELL", -0.6
    return "SELL", -1.0


def interpret_macd(macd_line, signal_line, histogram, prev_histogram) -> tuple:
    if macd_line is None or signal_line is None or histogram is None:
        return "HOLD", 0.0
    if prev_histogram is not None and prev_histogram * histogram < 0:
        if histogram > 0:
            return "BUY", 0.9
        else:
            return "SELL", -0.9
    if histogram > 0 and (prev_histogram is None or histogram > prev_histogram):
        return "BUY", 0.5
    if histogram < 0 and (prev_histogram is None or histogram < prev_histogram):
        return "SELL", -0.5
    return "HOLD", 0.0


def interpret_bollinger(price, bb_upper, bb_lower, percent_b) -> tuple:
    if price is None or bb_upper is None or bb_lower is None:
        return "HOLD", 0.0
    if percent_b is not None:
        if percent_b < 0:
            return "BUY", 1.0
        if percent_b < 0.2:
            return "BUY", 0.5
        if percent_b <= 0.8:
            return "HOLD", 0.0
        if percent_b <= 1.0:
            return "SELL", -0.5
        return "SELL", -1.0
    if price <= bb_lower:
        return "BUY", 1.0
    if price >= bb_upper:
        return "SELL", -1.0
    return "HOLD", 0.0


def interpret_volume(volume_ratio, price_change_pct) -> tuple:
    if volume_ratio is None or price_change_pct is None:
        return "HOLD", 0.0
    if volume_ratio > 1.5:
        if price_change_pct > 0:
            return "BUY", 0.8
        if price_change_pct < 0:
            return "SELL", -0.8
    if volume_ratio > 1.2:
        if price_change_pct > 0:
            return "BUY", 0.4
        if price_change_pct < 0:
            return "SELL", -0.4
    return "HOLD", 0.0


def interpret_supertrend(direction) -> tuple:
    """Supertrend: 1=UP (bullish), -1=DOWN (bearish)"""
    if direction is None:
        return "HOLD", 0.0
    if direction == 1:
        return "BUY", 0.8
    return "SELL", -0.8


def interpret_ma_cross(latest: dict) -> tuple:
    """EMA 10/20 ve SMA 50/200 crossovers."""
    score = 0.0
    signals = []

    ema10 = latest.get("ema_10")
    ema20 = latest.get("ema_20")
    sma50 = latest.get("sma_50")
    sma200 = latest.get("sma_200")
    price = latest.get("price")

    if ema10 is not None and ema20 is not None:
        if ema10 > ema20:
            score += 0.3
            signals.append("BUY")
        else:
            score -= 0.3
            signals.append("SELL")

    if sma50 is not None and sma200 is not None:
        if sma50 > sma200:
            score += 0.25
            signals.append("BUY")
        else:
            score -= 0.25
            signals.append("SELL")

    if price is not None and sma200 is not None:
        if price > sma200:
            score += 0.2
        else:
            score -= 0.2

    if score > 0.3:
        return "BUY", round(score, 2)
    elif score < -0.3:
        return "SELL", round(score, 2)
    return "HOLD", 0.0


def interpret_trend(price, sma_50, sma_50_slope, ema_10_slope) -> tuple:
    """Trend yönü analizi."""
    if price is None:
        return "HOLD", 0.0
    score = 0.0
    if sma_50 is not None and price > sma_50:
        score += 0.3
    elif sma_50 is not None:
        score -= 0.3

    if sma_50_slope is not None:
        if sma_50_slope > 0:
            score += 0.2
        else:
            score -= 0.2

    if ema_10_slope is not None:
        if ema_10_slope > 0:
            score += 0.3
        else:
            score -= 0.3

    if score > 0.3:
        return "BUY", round(score, 2)
    elif score < -0.3:
        return "SELL", round(score, 2)
    return "HOLD", round(score, 2)


def _rsi_reason(rsi_value, score):
    if rsi_value is None:
        return "Veri yok"
    if rsi_value < 30:
        return f"RSI={rsi_value:.1f} — Aşırı satım bölgesi (<30), güçlü LONG sinyali"
    if rsi_value < 40:
        return f"RSI={rsi_value:.1f} — Oversold'a yakın (30–40), zayıf LONG sinyali"
    if rsi_value <= 60:
        return f"RSI={rsi_value:.1f} — Nötr bölge (30–60), pozisyon önerisi yok"
    if rsi_value <= 70:
        return f"RSI={rsi_value:.1f} — Overbought'a yakın (60–70), zayıf SHORT sinyali"
    return f"RSI={rsi_value:.1f} — Aşırı alım bölgesi (>70), güçlü SHORT sinyali"


def _macd_reason(macd_line, signal_line, histogram, prev_histogram, score):
    if macd_line is None or histogram is None:
        return "Veri yok"
    crossover = prev_histogram is not None and prev_histogram * histogram < 0
    if crossover:
        if histogram > 0:
            return f"MACD crossover ↑ (hist={histogram:.4f}) — Sinyal çizgisini yukarı kesti, güçlü LONG"
        else:
            return f"MACD crossover ↓ (hist={histogram:.4f}) — Sinyal çizgisini aşağı kesti, güçlü SHORT"
    if histogram > 0 and (prev_histogram is None or histogram > prev_histogram):
        prev_str = f"{prev_histogram:.4f}" if prev_histogram is not None else "0"
        return f"Histogram pozitif ve artıyor ({histogram:.4f}>{prev_str}) — LONG momentum"
    if histogram < 0 and (prev_histogram is None or histogram < prev_histogram):
        return f"Histogram negatif ve azalıyor ({histogram:.4f}) — SHORT momentum"
    return f"Histogram={histogram:.4f}, MACD={macd_line:.4f} — Belirgin yön yok, nötr"


def _bb_reason(price, bb_upper, bb_lower, percent_b, score):
    if percent_b is None and price is None:
        return "Veri yok"
    if percent_b is not None:
        if percent_b < 0:
            return f"%B={percent_b:.3f} — Alt bandın altında, aşırı satım, güçlü LONG"
        if percent_b < 0.2:
            return f"%B={percent_b:.3f} — Alt banda yakın (<%0.20), zayıf LONG"
        if percent_b <= 0.8:
            return f"%B={percent_b:.3f} — Bantların ortasında (0.20–0.80), nötr"
        if percent_b <= 1.0:
            return f"%B={percent_b:.3f} — Üst banda yakın (>0.80), zayıf SHORT"
        return f"%B={percent_b:.3f} — Üst bandın üzerinde, aşırı alım, güçlü SHORT"
    if price <= bb_lower:
        return f"Fiyat={price:.2f} alt banda ulaştı ({bb_lower:.2f}), güçlü LONG"
    if price >= bb_upper:
        return f"Fiyat={price:.2f} üst banda ulaştı ({bb_upper:.2f}), güçlü SHORT"
    return f"Fiyat={price:.2f} bantlar içinde ({bb_lower:.2f}–{bb_upper:.2f}), nötr"


def _vol_reason(volume_ratio, price_change_pct, score):
    if volume_ratio is None or price_change_pct is None:
        return "Veri yok"
    direction = "yukarı ↑" if price_change_pct > 0 else "aşağı ↓"
    if volume_ratio > 1.5:
        return f"Hacim oranı={volume_ratio:.2f}x (yüksek), fiyat {direction} %{abs(price_change_pct):.2f} — hareket onaylı"
    if volume_ratio > 1.2:
        return f"Hacim oranı={volume_ratio:.2f}x (orta), fiyat {direction} %{abs(price_change_pct):.2f} — zayıf onay"
    return f"Hacim oranı={volume_ratio:.2f}x — normal seviye, yön onayı yok"


def _supertrend_reason(direction, score):
    if direction is None:
        return "Supertrend: Veri yok"
    if direction == 1:
        return "Supertrend: Yükseliş trendinde (UP), güçlü LONG sinyali"
    return "Supertrend: Düşüş trendinde (DOWN), güçlü SHORT sinyali"


def _ma_cross_reason(latest, score):
    ema10 = latest.get("ema_10")
    ema20 = latest.get("ema_20")
    sma50 = latest.get("sma_50")
    sma200 = latest.get("sma_200")
    parts = []
    if ema10 is not None and ema20 is not None:
        rel = "üstünde ↑" if ema10 > ema20 else "altında ↓"
        parts.append(f"EMA10({ema10:.2f}) EMA20({ema20:.2f})'nin {rel}")
    if sma50 is not None and sma200 is not None:
        rel = "üstünde ↑" if sma50 > sma200 else "altında ↓"
        parts.append(f"SMA50({sma50:.2f}) SMA200({sma200:.2f})'nin {rel}")
    if not parts:
        return "MA Crossover: Veri yok"
    return "MA Crossover: " + ", ".join(parts)


def _trend_reason(latest, score):
    sma50 = latest.get("sma_50")
    price = latest.get("price")
    parts = []
    if price is not None and sma50 is not None:
        rel = "üstünde ↑" if price > sma50 else "altında ↓"
        parts.append(f"Fiyat SMA50({sma50:.2f})'nin {rel}")
    slope = latest.get("sma_50_slope")
    if slope is not None:
        parts.append(f"SMA50 eğimi={'pozitif' if slope > 0 else 'negatif'} ({slope:.4f})")
    if not parts:
        return "Trend: Veri yok"
    return "Trend: " + ", ".join(parts)


def generate_signal(latest: dict) -> dict:
    rsi_signal, rsi_score = interpret_rsi(latest.get("rsi"))
    macd_signal, macd_score = interpret_macd(
        latest.get("macd_line"),
        latest.get("signal_line"),
        latest.get("histogram"),
        latest.get("histogram_prev"),
    )
    bb_signal, bb_score = interpret_bollinger(
        latest.get("price"),
        latest.get("bb_upper"),
        latest.get("bb_lower"),
        latest.get("bb_percent_b"),
    )
    vol_signal, vol_score = interpret_volume(
        latest.get("volume_ratio"),
        latest.get("price_change_pct"),
    )
    st_signal, st_score = interpret_supertrend(
        latest.get("supertrend_direction"),
    )
    ma_signal, ma_score = interpret_ma_cross(latest)
    trend_signal, trend_score = interpret_trend(
        latest.get("price"),
        latest.get("sma_50"),
        latest.get("sma_50_slope"),
        latest.get("ema_10_slope"),
    )

    composite = (
        SIGNAL_WEIGHTS["rsi"] * rsi_score
        + SIGNAL_WEIGHTS["macd"] * macd_score
        + SIGNAL_WEIGHTS["bollinger"] * bb_score
        + SIGNAL_WEIGHTS["volume"] * vol_score
        + SIGNAL_WEIGHTS["supertrend"] * st_score
        + SIGNAL_WEIGHTS["ma_cross"] * ma_score
        + SIGNAL_WEIGHTS["trend"] * trend_score
    )

    if composite > 0.3:
        signal = "BUY"
    elif composite < -0.3:
        signal = "SELL"
    else:
        signal = "HOLD"

    scores = [rsi_score, macd_score, bb_score, vol_score, st_score, ma_score, trend_score]
    agreeing = sum(1 for s in scores if (composite > 0 and s > 0) or (composite < 0 and s < 0))
    abs_score = abs(composite)
    if abs_score > 0.5 and agreeing >= 4:
        confidence = "HIGH"
    elif abs_score > 0.3:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    bullish = sum(1 for s in scores if s > 0)
    bearish = sum(1 for s in scores if s < 0)
    conflict = bullish > 0 and bearish > 0
    hedge_score = round(min(bullish, bearish) / 3.0, 2)

    if conflict:
        viop_signal = "HEDGE"
    elif composite > 0.3:
        viop_signal = "LONG"
    elif composite < -0.3:
        viop_signal = "SHORT"
    else:
        viop_signal = "NEUTRAL"

    def _direction(score_val):
        if score_val > 0:
            return "LONG"
        if score_val < 0:
            return "SHORT"
        return "NEUTRAL"

    viop_reasoning = [
        {"indicator": "RSI", "weight": SIGNAL_WEIGHTS["rsi"], "direction": _direction(rsi_score),
         "score": round(rsi_score, 2), "weighted": round(SIGNAL_WEIGHTS["rsi"] * rsi_score, 4),
         "reason": _rsi_reason(latest.get("rsi"), rsi_score)},
        {"indicator": "MACD", "weight": SIGNAL_WEIGHTS["macd"], "direction": _direction(macd_score),
         "score": round(macd_score, 2), "weighted": round(SIGNAL_WEIGHTS["macd"] * macd_score, 4),
         "reason": _macd_reason(latest.get("macd_line"), latest.get("signal_line"),
                                latest.get("histogram"), latest.get("histogram_prev"), macd_score)},
        {"indicator": "Bollinger", "weight": SIGNAL_WEIGHTS["bollinger"], "direction": _direction(bb_score),
         "score": round(bb_score, 2), "weighted": round(SIGNAL_WEIGHTS["bollinger"] * bb_score, 4),
         "reason": _bb_reason(latest.get("price"), latest.get("bb_upper"),
                              latest.get("bb_lower"), latest.get("bb_percent_b"), bb_score)},
        {"indicator": "Hacim", "weight": SIGNAL_WEIGHTS["volume"], "direction": _direction(vol_score),
         "score": round(vol_score, 2), "weighted": round(SIGNAL_WEIGHTS["volume"] * vol_score, 4),
         "reason": _vol_reason(latest.get("volume_ratio"), latest.get("price_change_pct"), vol_score)},
        {"indicator": "Supertrend", "weight": SIGNAL_WEIGHTS["supertrend"], "direction": _direction(st_score),
         "score": round(st_score, 2), "weighted": round(SIGNAL_WEIGHTS["supertrend"] * st_score, 4),
         "reason": _supertrend_reason(latest.get("supertrend_direction"), st_score)},
        {"indicator": "MA Crossover", "weight": SIGNAL_WEIGHTS["ma_cross"], "direction": _direction(ma_score),
         "score": round(ma_score, 2), "weighted": round(SIGNAL_WEIGHTS["ma_cross"] * ma_score, 4),
         "reason": _ma_cross_reason(latest, ma_score)},
        {"indicator": "Trend", "weight": SIGNAL_WEIGHTS["trend"], "direction": _direction(trend_score),
         "score": round(trend_score, 2), "weighted": round(SIGNAL_WEIGHTS["trend"] * trend_score, 4),
         "reason": _trend_reason(latest, trend_score)},
    ]

    return {
        "signal": signal,
        "score": round(composite, 3),
        "confidence": confidence,
        "viop_signal": viop_signal,
        "hedge_score": hedge_score,
        "viop_reasoning": viop_reasoning,
        "breakdown": {
            "rsi": {"signal": rsi_signal, "score": round(rsi_score, 2),
                    "weight": SIGNAL_WEIGHTS["rsi"],
                    "weighted": round(SIGNAL_WEIGHTS["rsi"] * rsi_score, 4),
                    "values": {"rsi": latest.get("rsi")}},
            "macd": {"signal": macd_signal, "score": round(macd_score, 2),
                     "weight": SIGNAL_WEIGHTS["macd"],
                     "weighted": round(SIGNAL_WEIGHTS["macd"] * macd_score, 4),
                     "values": {"macd_line": latest.get("macd_line"),
                                "signal_line": latest.get("signal_line"),
                                "histogram": latest.get("histogram"),
                                "histogram_prev": latest.get("histogram_prev")}},
            "bollinger": {"signal": bb_signal, "score": round(bb_score, 2),
                          "weight": SIGNAL_WEIGHTS["bollinger"],
                          "weighted": round(SIGNAL_WEIGHTS["bollinger"] * bb_score, 4),
                          "values": {"percent_b": latest.get("bb_percent_b"),
                                     "bb_upper": latest.get("bb_upper"),
                                     "bb_lower": latest.get("bb_lower"),
                                     "price": latest.get("price")}},
            "volume": {"signal": vol_signal, "score": round(vol_score, 2),
                       "weight": SIGNAL_WEIGHTS["volume"],
                       "weighted": round(SIGNAL_WEIGHTS["volume"] * vol_score, 4),
                       "values": {"volume_ratio": latest.get("volume_ratio"),
                                  "price_change_pct": latest.get("price_change_pct")}},
            "supertrend": {"signal": st_signal, "score": round(st_score, 2),
                           "weight": SIGNAL_WEIGHTS["supertrend"],
                           "weighted": round(SIGNAL_WEIGHTS["supertrend"] * st_score, 4),
                           "values": {"supertrend_direction": latest.get("supertrend_direction")}},
            "ma_cross": {"signal": ma_signal, "score": round(ma_score, 2),
                         "weight": SIGNAL_WEIGHTS["ma_cross"],
                         "weighted": round(SIGNAL_WEIGHTS["ma_cross"] * ma_score, 4),
                         "values": {"ema_10": latest.get("ema_10"), "ema_20": latest.get("ema_20"),
                                    "sma_50": latest.get("sma_50"), "sma_200": latest.get("sma_200")}},
            "trend": {"signal": trend_signal, "score": round(trend_score, 2),
                      "weight": SIGNAL_WEIGHTS["trend"],
                      "weighted": round(SIGNAL_WEIGHTS["trend"] * trend_score, 4),
                      "values": {"price": latest.get("price"), "sma_50": latest.get("sma_50"),
                                 "sma_50_slope": latest.get("sma_50_slope"),
                                 "ema_10_slope": latest.get("ema_10_slope")}},
        },
    }

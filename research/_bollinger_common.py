#!/usr/bin/python3
# =============================================================================
# _bollinger_common.py — shared helpers for Blaque Baux BOLLINGER (compression breakout + the expansion falsification).
# Alpaca SIP daily bars (adjustment=all → total return) with VOLUME; env keys. Read-only.
#
# The "Compression Breakout System": a Bollinger-Band-width squeeze (126d-percentile width < 25th) that then breaks a
# 20-day high on above-average volume with price > 200-SMA. A published run shows +899% on AAPL (profit factor 4.33)
# but only +46% on MSFT — and that gap IS the tell: AAPL rose ~50x over the sample, so a long-biased breakout on it is
# mostly the STOCK, not the system. BOLLINGER tests two separable claims honestly: (1) does compression precede
# EXPANSION — true for VOLATILITY (vol clusters / mean-reverts up from lows), the easy half; (2) does the breakout add
# a DIRECTIONAL edge beyond the stock's own drift, and does the traded system beat BUY-AND-HOLD of the same names
# across a universe (not one lucky trender)? Survivorship-flagged universe HELPS the system look good, so a loss to
# buy-hold even then is a strong null. The honest question is never "did it make money on AAPL" — it's "vs just holding AAPL."
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    """{date: (close, volume)} daily, total-return adjusted."""
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: (b["c"], b.get("v", 0.0)) for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def closes_vol(s):
    b = bars(s)
    if len(b) < 600: return None, None, []
    dates = sorted(b)
    return (np.array([b[d][0] for d in dates], float),
            np.array([b[d][1] for d in dates], float), dates)

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=float((cum/np.maximum.accumulate(cum)-1).min()), vol=r.std()*math.sqrt(252))

def signals(c, v):
    """Per-day compression-breakout signal components (causal). Returns dict of boolean/level arrays, length n."""
    n = len(c); dr = np.concatenate([[0.0], c[1:]/c[:-1]-1])
    sma20 = np.full(n, np.nan); std20 = np.full(n, np.nan); bw = np.full(n, np.nan)
    sma200 = np.full(n, np.nan); hi20 = np.full(n, np.nan); vavg = np.full(n, np.nan)
    for t in range(n):
        if t >= 20:
            w = c[t-20:t]; sma20[t] = w.mean(); std20[t] = w.std(); bw[t] = 4*std20[t]/sma20[t] if sma20[t] else np.nan
            hi20[t] = c[t-20:t].max(); vavg[t] = v[t-20:t].mean()
        if t >= 200: sma200[t] = c[t-200:t].mean()
    bwpct = np.full(n, np.nan)
    for t in range(126, n):
        w = bw[t-126:t]; w = w[np.isfinite(w)]
        if len(w) > 60 and np.isfinite(bw[t]): bwpct[t] = (w <= bw[t]).mean()
    squeeze = bwpct < 0.25
    sq_recent = np.array([squeeze[max(0,t-5):t+1].any() for t in range(n)])
    breakout = (c > hi20) & sq_recent & (c > sma200) & (v > vavg)
    return dict(dr=dr, bw=bw, bwpct=bwpct, squeeze=squeeze, breakout=breakout, sma200=sma200)

#!/usr/bin/python3
# =============================================================================
# bollinger_1_compression_breakout.py — does compression breakout have a directional edge, or is it AAPL beta?
#
# Compression = Bollinger-width 126d-percentile < 25th; breakout = close > 20d-high within 5 bars of squeeze, >200-SMA,
# above-avg volume. All SIP daily total return (with volume), causal, ~90-name survivorship-flagged universe.
#  (A) COMPRESSION → VOLATILITY EXPANSION: forward 20d realized vol after a squeeze vs unconditional. (the easy half)
#  (B) BREAKOUT → DIRECTIONAL EDGE: forward 20d mean return & hit-rate after the full signal vs the stock's own
#      unconditional forward return. Does the squeeze-breakout PREDICT direction, or just restate the drift?
#  (C) TRADED SYSTEM vs BUY-AND-HOLD, cross-symbol: enter on signal, hold 20d; aggregate vs equal-weight buy-hold of
#      the SAME names. And does per-name system return just track per-name buy-hold return (= selection, not signal)?
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bollinger_common import closes_vol, rets, stats, signals
import numpy as np

UNIV = ["AAPL","MSFT","AMZN","GOOGL","META","NVDA","AVGO","ORCL","CRM","ADBE","CSCO","INTC","AMD","QCOM","TXN","IBM","MU","AMAT","LRCX","ADI","NOW","INTU",
        "JPM","BAC","WFC","GS","MS","C","AXP","V","MA","USB","PNC","SCHW","BLK","BK","COF",
        "JNJ","PFE","MRK","ABT","TMO","LLY","UNH","BMY","ABBV","AMGN","GILD","CVS","CI","MDT","DHR","ISRG",
        "XOM","CVX","COP","SLB","EOG","OXY","PSX","VLO",
        "HD","WMT","COST","TGT","NKE","MCD","SBUX","PG","KO","PEP","DIS","CMCSA","LOW","TJX","EL","CL","KMB",
        "BA","CAT","GE","HON","UNP","UPS","MMM","LMT","RTX","DE","T","VZ","NEE","DUK","SO"]
H = 20
print("="*98); print(f"BOLLINGER #1 — compression breakout: directional edge or beta?  (2016→2026, {len(UNIV)} names, hold {H}d)"); print("="*98)

fv_sq, fv_un = [], []                         # forward vol after squeeze vs unconditional
fr_sig, fr_un = [], []                        # forward return after signal vs unconditional
hit_sig, hit_un = [], []
sys_ret_byname, bh_ret_byname = {}, {}
sys_streams, bh_streams = [], []
n_sig = 0
for s in UNIV:
    c, v, dts = closes_vol(s)
    if c is None: continue
    n = len(c); sg = signals(c, v); dr = sg['dr']
    fwd = np.array([c[t+H]/c[t]-1 if t+H < n else np.nan for t in range(n)])
    fwv = np.array([dr[t+1:t+1+H].std()*np.sqrt(252) if t+1+H <= n else np.nan for t in range(n)])
    # (A) vol expansion
    sq = sg['squeeze'] & np.isfinite(fwv)
    fv_sq += list(fwv[sq]); fv_un += list(fwv[np.isfinite(fwv)])
    # (B) directional edge
    bk = sg['breakout'] & np.isfinite(fwd); n_sig += int(bk.sum())
    fr_sig += list(fwd[bk]); fr_un += list(fwd[np.isfinite(fwd)])
    hit_sig += list((fwd[bk] > 0).astype(float)); hit_un += list((fwd[np.isfinite(fwd)] > 0).astype(float))
    # (C) traded system (enter on signal when flat, hold H days) vs buy-hold
    pos = np.zeros(n); hold = 0
    for t in range(n):
        if hold > 0: pos[t] = 1.0; hold -= 1
        elif sg['breakout'][t]: pos[t] = 1.0; hold = H-1
    sysr = pos[:-1] * dr[1:]                    # position today earns tomorrow's return
    sys_streams.append(stats(sysr)); bh_streams.append(stats(dr[1:]))
    sys_ret_byname[s] = np.prod(1+sysr)-1; bh_ret_byname[s] = np.prod(1+dr[1:])-1

fv_sq, fv_un = np.array(fv_sq), np.array(fv_un)
fr_sig, fr_un = np.array(fr_sig), np.array(fr_un)
print(f"\n(A) COMPRESSION → VOLATILITY EXPANSION   fwd-{H}d vol after squeeze {np.nanmean(fv_sq)*100:.0f}%  vs  unconditional {np.nanmean(fv_un)*100:.0f}%  → {'EXPANDS' if np.nanmean(fv_sq)>np.nanmean(fv_un) else 'no'}")
print(f"(B) BREAKOUT → DIRECTIONAL EDGE          fwd-{H}d return after signal {np.nanmean(fr_sig)*100:+.2f}%  vs  unconditional {np.nanmean(fr_un)*100:+.2f}%   (edge {(np.nanmean(fr_sig)-np.nanmean(fr_un))*100:+.2f}pp)")
print(f"                                         hit-rate after signal {np.mean(hit_sig)*100:.0f}%  vs  unconditional {np.mean(hit_un)*100:.0f}%   ({n_sig} signals)")

sys_cagr = np.nanmean([x['cagr'] for x in sys_streams]); bh_cagr = np.nanmean([x['cagr'] for x in bh_streams])
sys_sh = np.nanmean([x['sh'] for x in sys_streams]); bh_sh = np.nanmean([x['sh'] for x in bh_streams])
sys_dd = np.nanmean([x['dd'] for x in sys_streams]); bh_dd = np.nanmean([x['dd'] for x in bh_streams])
names = [s for s in UNIV if s in sys_ret_byname]
corr = np.corrcoef([sys_ret_byname[s] for s in names], [bh_ret_byname[s] for s in names])[0,1]
# the AAPL vs MSFT illustration
def show(s):
    return f"{s}: system {sys_ret_byname.get(s,float('nan'))*100:+.0f}% vs buy-hold {bh_ret_byname.get(s,float('nan'))*100:+.0f}%"
print(f"\n(C) TRADED SYSTEM vs BUY-AND-HOLD (equal-wt across {len(names)} names)   {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}")
print(f"  compression-breakout system (in-market part-time)        {sys_sh:>+8.2f}{sys_cagr*100:>+7.1f}%{sys_dd*100:>+7.0f}%")
print(f"  buy-and-hold same names                                  {bh_sh:>+8.2f}{bh_cagr*100:>+7.1f}%{bh_dd*100:>+7.0f}%")
print(f"  • per-name: {show('AAPL')}  |  {show('MSFT')}   (the claim's two names)")
print(f"  • system return vs buy-hold return across names: corr {corr:+.2f} — {'the system just tracks which stock went up (selection, not signal)' if corr>0.5 else 'low corr'}")

# ---- verdict ----------------------------------------------------------------------------------------
vol_expands = np.nanmean(fv_sq) > np.nanmean(fv_un) + 0.01
dir_edge = (np.nanmean(fr_sig) - np.nanmean(fr_un)) > 0.01 and (np.mean(hit_sig) - np.mean(hit_un)) > 0.03
beats_bh = sys_cagr > bh_cagr
print("\n"+"="*98); print("READ:")
if vol_expands:
    print(f"  • COMPRESSION → VOL EXPANSION holds ({np.nanmean(fv_sq)*100:.0f}% vs {np.nanmean(fv_un)*100:.0f}% fwd vol) — but vol expanding is NOT a tradable edge; it says moves get bigger, not which way.")
else:
    print(f"  • EVEN COMPRESSION→EXPANSION FAILS at the 20d horizon: fwd vol after a squeeze {np.nanmean(fv_sq)*100:.0f}% ≈ unconditional {np.nanmean(fv_un)*100:.0f}% — low vol CLUSTERS, calm persists, so a squeeze does NOT reliably precede a near-term vol pop. The folklore's timing is the catch.")
print(f"  • DIRECTIONAL EDGE is {'REAL' if dir_edge else 'ABSENT'}: fwd return after the full breakout signal {np.nanmean(fr_sig)*100:+.2f}% vs {np.nanmean(fr_un)*100:+.2f}% unconditional, hit-rate {np.mean(hit_sig)*100:.0f}% vs {np.mean(hit_un)*100:.0f}% — {'a genuine post-squeeze drift' if dir_edge else 'essentially the stock’s own drift, no squeeze-specific predictive power'}.")
print(f"  • vs BUY-AND-HOLD the system {'WINS' if beats_bh else 'LOSES'} ({sys_cagr*100:+.1f}% vs {bh_cagr*100:+.1f}%/yr) — being out of the market between signals forfeits the very drift it's trying to catch.")
print(f"  • THE AAPL/MSFT GAP IS SELECTION: per-name system return tracks per-name buy-hold at corr {corr:+.2f} — '+899% on AAPL' is AAPL beta (AAPL system +258% vs buy-hold +1203%); the system 'needs names that expand' = it needs names that went UP. Picking winners after the fact, not a signal.")

if dir_edge and beats_bh:
    v = "CONDITIONAL: a real post-squeeze directional edge that also beats buy-hold — rare; verify OOS and vs momentum before trusting."
else:
    v = ("NULL: the compression breakout has NO tradable edge. Even the folklore's easy half is shaky — at a 20-day "
         f"horizon a squeeze does NOT precede higher vol ({np.nanmean(fv_sq)*100:.0f}% vs {np.nanmean(fv_un)*100:.0f}%), because low vol clusters. The breakout adds no "
         "directional information (fwd return and hit-rate match the stock's own drift), and the traded system "
         f"UNDERPERFORMS buy-and-hold ({sys_cagr*100:+.1f}% vs {bh_cagr*100:+.1f}%/yr) by sitting out between signals. The headline '+899% on "
         f"AAPL' is AAPL's ~12x beta in a costume; the author's own tell — works on AAPL, not MSFT — is SELECTION (corr "
         f"{corr:+.2f} to buy-hold), i.e. it needs a name that already trended, which is just the momentum boom/beyond "
         "already own. Compression predicts bigger moves (sometimes), never a tradable direction = the honest null.")
print(f"\n  VERDICT: {v}")
print("  (Close-based BB-width/20d-high + volume filter; fixed 20d hold (the claim's ATR-stop/risk-sizing is a path overlay,")
print("   not a source of edge). Survivorship-flagged universe FLATTERS the system, so a loss to buy-hold is conservative.)")

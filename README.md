# Blaque Baux Bollinger

**Compression breakout — Bollinger-width squeeze + 20-day-high break. Does compression precede expansion, or is "+899% on AAPL" just AAPL?**

The "Compression Breakout System": a Bollinger-Band-width squeeze (126-day width percentile < 25th) that then breaks a
20-day high on above-average volume with price > 200-SMA. A published run reports **+899% on AAPL** (profit factor 4.33)
but only **+46% on MSFT** — and that gap is the tell: AAPL rose ~12× over the sample, so a long-biased breakout on it is
mostly the *stock*, not the system. Bollinger tests two separable claims honestly across a ~90-name universe:
(1) does compression precede **expansion**, and (2) does the breakout add a **directional edge** beyond the stock's own
drift — and does the traded system beat **buy-and-hold** of the same names?

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/bollinger_1_compression_breakout.py   # needs Alpaca data keys in the environment
```

## The finding (no edge — and even the folklore's easy half is shaky)

[`research/bollinger_1_compression_breakout.py`](research/bollinger_1_compression_breakout.py) — SIP daily total return
with volume, causal, 93 survivorship-flagged names, 20-day hold.

- **Even "compression → expansion" fails at the trade horizon.** Forward 20-day vol after a squeeze is **25%** vs **26%**
  unconditional — essentially equal. Low vol *clusters*: calm persists, so a squeeze does *not* reliably precede a
  near-term vol pop. The folklore's timing is the catch.
- **No directional edge.** Forward 20-day return after the full breakout signal is **+1.60% vs +1.48%** unconditional;
  hit-rate **58% vs 58%** (7,099 signals). The breakout restates the stock's own drift — it doesn't predict direction.
- **Loses to buy-and-hold.** The traded system earns **+3.6%/yr vs +15.0%** for buy-hold of the same names — sitting out
  of the market between signals forfeits the very drift it's trying to catch.
- **The AAPL/MSFT gap is selection, not signal.** Per-name system return tracks per-name buy-hold at **corr +0.56**
  (AAPL system +258% vs buy-hold **+1203%**). "+899% on AAPL" is AAPL beta in a costume; "the system needs names that
  expand" means *it needs names that already went up* — picking winners after the fact.

## Verdict

**NULL — no tradable edge.** The compression breakout predicts *bigger moves* (sometimes), never a tradable *direction*;
its headline returns are the underlying's drift plus which-stock-you-picked, and the traded version underperforms simply
holding the names. A breakout needs a trending name — which is just the momentum `boom`/`beyond` already own. The
survivorship-flagged universe *flatters* the system, so a loss to buy-hold is a conservative result. (The claim's
ATR-stop / risk-based sizing is a path overlay, not a source of edge.)

## Status

**Research.** Honest null — a popular mechanical system tested cross-symbol against the only benchmark that matters
(holding the stock). Compression→expansion test, directional-edge test, traded-vs-buy-hold, selection-correlation,
Alpaca SIP daily total return with volume. No live capital.

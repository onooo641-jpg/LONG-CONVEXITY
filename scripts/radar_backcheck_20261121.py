"""Would the radar's pricing step (coin-flip test, no strategy knowledge) have picked Topstep?

Inputs are the recorded figures in docs/FIGURES_LEDGER.md (G1, F1/F2, F5/F6, G3/G4, R1/R2, F8):
coin-flip median net and real net, 2016-26, 50K products. Retrospective, not blind.

    uv run python scripts/radar_backcheck_20261121.py
"""
from scipy.stats import spearmanr

D = {"Topstep 50K": (18046, 44359), "LucidFlex 50K": (18519, 37523), "TradeDay $85": (14035, 35678),
     "Tradeify Select Flex": (11110, 32900), "Breakout Classic": (10679, 38263), "MFFU Rapid EOD": (7358, 34481),
     "TFD Static Pro": (3274, 20248), "FTMO Fut Growth": (1906, 34236), "FTMO Fut Pro": (1523, 28452),
     "FundedNext Rapid Pro": (-608, 14482), "TFD Static Core": (-1163, 10680), "TradeDay $189": (-4213, 22158),
     "Bulenox Momentum": (-14622, -4139)}
r = spearmanr([v[0] for v in D.values()], [v[1] for v in D.values()])
print(f"rank correlation, coin-flip median vs real net: {r.statistic:.2f} (p={r.pvalue:.4f}, n={len(D)})")
for k, (c, n) in sorted(D.items(), key=lambda x: -x[1][0]):
    print(f"{k:<22} coin flip {c:>8,}   real {n:>8,}")

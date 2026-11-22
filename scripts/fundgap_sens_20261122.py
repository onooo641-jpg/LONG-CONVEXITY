"""Sensitivity (labelled, not a verdict) for corrected #208: fee multiples and pair sets.

    uv run python scripts/fundgap_sens_20261122.py | tee docs/jx_runs/fundgap_sens_20261122.txt
"""
import pandas as pd

import scripts.fundgap_20261121 as m

df = pd.read_parquet("data/public/fundgap_funding.parquet")
H = m.hourly(df[df.venue.isin(["hl", "dydx", "aevo"])])
MID = m.MID
ann = lambda x: float(x.mean() * 365 * 100)  # noqa: E731
for mult in (1.0, 1.5, 2.0, 3.0):
    m.FEE_SIDE = 0.0005 * mult
    s, _, _ = m.run(H, m.TESTED)
    print(f"fees x{mult}: halves {ann(s.r[s.index < MID]):.2f}% / {ann(s.r[s.index >= MID]):.2f}% on capital")
m.FEE_SIDE = 0.0005
for lab, pairs in (("HL-dYdX + HL-Aevo (no dYdX-Aevo)", [("hl", "dydx"), ("hl", "aevo")]), ("pairs with dYdX only", [("hl", "dydx"), ("dydx", "aevo")])):
    s, _, _ = m.run(H, pairs)
    print(f"{lab}: halves {ann(s.r[s.index < MID]):.2f}% / {ann(s.r[s.index >= MID]):.2f}%")

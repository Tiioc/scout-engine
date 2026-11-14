#!/usr/bin/env python3
"""Checks the plan against funds that can actually be bought, and against taxes.

1. Each fund against the research block it stands in for (same months).
2. The growth mix built from real funds since 2007, through 2008, 2020 and 2022.
3. The same path in a taxable account against a tax-free one.
4. Whether other assets (international, property funds, bitcoin) would have helped.

Needs monthly fund prices saved as <data>/yahoo/<TICKER>.json (Yahoo chart format).
Usage: python3 scripts/realfunds.py --data /path/to/data [--out file.json]
"""
import argparse, datetime, json, os, sys
import numpy as np
import pandas as pd
import backtest as B
import levels as Lv

ST_TAX, LT_TAX = 0.22, 0.15          # assumed federal rates on short- and long-term gains; no state tax


def fund(data, t):
    r = json.load(open(os.path.join(data, "yahoo", t + ".json")))["chart"]["result"][0]
    px = r["indicators"].get("adjclose", [{}])[0].get("adjclose") or r["indicators"]["quote"][0]["close"]
    s = {}
    for ts, v in zip(r["timestamp"], px):
        if v is None: continue
        d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc); s[d.year * 100 + d.month] = v
    s = pd.Series(s).sort_index()
    return s.pct_change().dropna()


def stats(r):
    L = np.cumsum(np.log1p(r.values)); y = len(r) / 12
    return {"per_year": round(float(np.expm1(L[-1] / y)), 4), "deepest_fall": round(float(np.expm1((L - np.maximum.accumulate(L)).min())), 3),
            "worst_12_months": round(float(np.expm1((L[12:] - L[:-12]).min())), 3) if len(L) > 12 else None}


def exit_rule(r, cash):
    idx = (1 + r).cumprod(); on = (idx > idx.rolling(10).mean()).shift(1).fillna(False).astype(bool)
    return pd.Series(np.where(on, r, cash.reindex(r.index).fillna(0)), index=r.index), on


def splice(*parts):
    out = parts[-1].copy()
    for p in reversed(parts[:-1]): out = pd.concat([p[p.index < out.index[0]], out])
    return out


def taxed(blocks, weights, holds, st=ST_TAX, lt=LT_TAX):
    """Monthly path with tax paid whenever an exit sells a block. blocks: name -> (returns, cash returns, held flags or None)."""
    idx = next(iter(blocks.values()))[0].index; val = {k: weights[k] for k in blocks}; basis = dict(val); age = {k: 0 for k in blocks}
    incash = {k: False for k in blocks}; carry = 0.0; path = []
    for t in idx:
        for k, (r, c, h) in blocks.items():
            want_in = True if h is None else bool(h.loc[t])
            if h is not None and incash[k] == want_in:                      # state flips this month
                if want_in:  incash[k] = False; basis[k] = val[k]; age[k] = 0
                else:
                    gain = val[k] - basis[k] + carry; rate = st if age[k] < 12 else lt
                    if gain > 0: val[k] -= gain * rate; carry = 0.0
                    else: carry = gain
                    incash[k] = True; basis[k] = val[k]
            val[k] *= 1 + (c.loc[t] if incash[k] else r.loc[t]); age[k] += 1
        tot = sum(val.values()); path.append(tot)
        if t % 100 == 12:                                                   # yearly rebalance, tax on what is trimmed
            for k in blocks:
                tgt = tot * weights[k]
                if val[k] > tgt and not incash[k] and val[k] > 0:
                    frac = (val[k] - tgt) / val[k]; gain = (val[k] - basis[k]) * frac
                    if gain > 0: tgt -= 0  ; val[k] -= gain * lt
                    basis[k] *= (1 - frac)
                elif val[k] < tgt: basis[k] += tgt - val[k]
            tot2 = sum(val.values())
            for k in blocks: val[k] = tot2 * weights[k] if True else val[k]
    s = pd.Series(path, index=idx); return s.pct_change().fillna(s.iloc[0] - 1)


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--out")
    a = ap.parse_args(argv); D = a.data
    real, df, mo = B.build(D); mo["trend_momentum"] = B.trend(mo["momentum"], mo["bills"])
    F = {t: fund(D, t) for t in ("AVUV", "MTUM", "SSO", "GLDM", "GLD", "BIL", "IEF", "IJS", "VBR", "DFSVX", "PDP", "SPY", "VTI", "VNQ", "BTC-USD", "AVDV", "VXUS", "SPMO", "IMTM")}
    last = int(mo.index[-1]); F = {k: v[v.index <= last] for k, v in F.items()}
    rep = {"fund_vs_research_block": {}}
    for t, blk in (("SPY", "stocks"), ("VTI", "stocks"), ("DFSVX", "small_value"), ("IJS", "small_value"), ("VBR", "small_value"), ("AVUV", "small_value"),
                   ("PDP", "momentum"), ("MTUM", "momentum"), ("SPMO", "momentum"), ("SSO", None)):
        f = F[t]; b = (2 * mo["stocks"] - mo["bills"] - B.BORROW_SPREAD / 12) if blk is None else mo[blk] - {"small_value": .005, "momentum": .015}.get(blk, 0) / 12
        j = f.index.intersection(b.index); f, b = f.loc[j], b.loc[j]
        rep["fund_vs_research_block"][t] = {"stands_in_for": blk or "stocks at 2x", "months": len(j), "from": int(j[0]), "fund_per_year": stats(f)["per_year"], "research_per_year": stats(b)["per_year"],
                                            "gap_per_year": round(stats(f)["per_year"] - stats(b)["per_year"], 4), "move_together": round(float(np.corrcoef(f, b)[0, 1]), 3),
                                            "fund_deepest_fall": stats(f)["deepest_fall"], "research_deepest_fall": stats(b)["deepest_fall"]}
    # growth mix from real funds, 2007-07 on
    sv = splice(F["IJS"], F["AVUV"]); mom = splice(F["PDP"], F["MTUM"]); gold = splice(F["GLD"], F["GLDM"]); cash = F["BIL"]; sso = F["SSO"]; spy = F["SPY"]
    idx = sv.index.intersection(mom.index).intersection(gold.index).intersection(cash.index).intersection(sso.index).intersection(spy.index)
    tsv, h_sv = exit_rule(sv, cash); tmom, h_mom = exit_rule(mom, cash)
    si = (1 + spy).cumprod(); h_mk = (si > si.rolling(10).mean()).shift(1).fillna(False).astype(bool); t2x = pd.Series(np.where(h_mk, sso.reindex(spy.index), cash.reindex(spy.index)), index=spy.index)
    idx = idx[idx >= 200801]
    w = {"sv": 0.2, "tsv": 0.1, "tmom": 0.5, "t2x": 0.1, "gold": 0.1}
    port = w["sv"] * sv.loc[idx] + w["tsv"] * tsv.loc[idx] + w["tmom"] * tmom.loc[idx] + w["t2x"] * t2x.loc[idx] + w["gold"] * gold.loc[idx]
    research = Lv.panel(D, with_dates=True); Mr, dates = research[0], research[2]
    cfg = json.load(open("engine/config.json"))["core"]["growth_mix"]; rw = np.array([cfg.get(x, 0) for x in Lv.A])
    res = pd.Series(Mr @ rw, index=dates).loc[idx[0]:idx[-1]]
    yr = lambda r, y: round(float((1 + r[(r.index // 100) == y]).prod() - 1), 3)
    rep["real_fund_growth_mix"] = {"from": int(idx[0]), "to": int(idx[-1]), "real_funds": stats(port), "research_version_same_months": stats(res), "plain_stocks_SPY": stats(spy.loc[idx]),
                                   "by_year": {str(y): {"real_funds": yr(port, y), "plain_stocks": yr(spy.loc[idx], y)} for y in sorted(set(idx // 100))},
                                   "note": "IJS then AVUV for small cheap companies; PDP then MTUM for momentum; GLD then GLDM; BIL as cash; exits monthly"}
    # taxes
    c = cash.loc[idx]
    blocks = {"sv": (sv.loc[idx], c, None), "tsv": (sv.loc[idx], c, h_sv.loc[idx]), "tmom": (mom.loc[idx], c, h_mom.loc[idx]),
              "t2x": (sso.loc[idx], c, h_mk.loc[idx]), "gold": (gold.loc[idx], c, None)}
    after = taxed(blocks, w, None); free = taxed(blocks, w, None, st=0.0, lt=0.0)
    spy_end = float((1 + spy.loc[idx]).prod()); spy_after = spy_end - (spy_end - 1) * LT_TAX; y = len(idx) / 12
    rep["taxes"] = {"assumed_rates": {"gains_held_under_a_year": ST_TAX, "gains_held_longer": LT_TAX, "state": 0.0},
                    "plan_in_a_tax_free_account_per_year": stats(free)["per_year"], "plan_in_a_taxable_account_per_year": stats(after)["per_year"],
                    "tax_cost_points_per_year": round(stats(free)["per_year"] - stats(after)["per_year"], 4),
                    "plain_stocks_untaxed_per_year": stats(spy.loc[idx])["per_year"], "plain_stocks_after_selling_and_paying_tax_per_year": round(spy_after ** (1 / y) - 1, 4)}
    # other assets, fund era
    def with_extra(extra, share, start):
        j = idx[idx >= start].intersection(extra.index); base = port.loc[j]; e, _ = exit_rule(extra, cash); 
        return {"from": int(j[0]), "growth_mix": stats(base), "with_%d%%_held" % (share * 100): stats((1 - share) * base + share * extra.loc[j]),
                "with_%d%%_and_an_exit" % (share * 100): stats((1 - share) * base + share * e.loc[j])}
    rep["other_assets"] = {"property_funds_VNQ_10pct": with_extra(F["VNQ"], 0.10, 200801), "international_stocks_VXUS_10pct": with_extra(F["VXUS"], 0.10, 201201),
                           "international_small_cheap_AVDV_10pct": with_extra(F["AVDV"], 0.10, 202001), "international_momentum_IMTM_10pct": with_extra(F["IMTM"], 0.10, 201601),
                           "bitcoin_5pct": with_extra(F["BTC-USD"], 0.05, 201601)}
    txt = json.dumps(rep, indent=1)
    if a.out: open(a.out, "w").write(txt)
    print(txt); return 0


if __name__ == "__main__":
    sys.exit(main())

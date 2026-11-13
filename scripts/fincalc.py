#!/usr/bin/env python3
"""Financial calculator for the Scout. Plain code, no AI. Every number in an
edition that involves returns, yields or growth must come from here.

Usage examples:
  python3 scripts/fincalc.py cagr --start 10000 --end 18000 --years 5
  python3 scripts/fincalc.py fv --pv 5000 --rate 0.07 --years 10 --monthly 200
  python3 scripts/fincalc.py real --nominal 0.07 --inflation 0.03
  python3 scripts/fincalc.py aftertax --yield 0.045 --federal 0.22 --state 0.05 --state-exempt
  python3 scripts/fincalc.py dividend --price 100 --dividend 4 --growth 0.03 --price-growth 0.02 --years 10 --tax 0.15
  python3 scripts/fincalc.py compare --years 20 --a-yield 0.045 --a-divgrowth 0.03 --a-pricegrowth 0.02 --b-yield 0.012 --b-divgrowth 0.09 --b-pricegrowth 0.08 --tax 0.15
  python3 scripts/fincalc.py fee --amount 10000 --rate 0.07 --years 30 --fee-a 0.0003 --fee-b 0.01
  python3 scripts/fincalc.py bonus --bonus 300 --tied-up 5000 --months 3 --tax 0.22
  python3 scripts/fincalc.py payback --cost 20000 --annual-profit 6000 --hours-per-year 300
  python3 scripts/fincalc.py dcf --cashflow 100 --growth 0.06 --years 10 --terminal-growth 0.025 --discount 0.09
  python3 scripts/fincalc.py drag --mean 0.10 --vol 0.60
  python3 scripts/fincalc.py rentbuy --price 500000 --down 0.2 --mortgage-rate 0.068 --years 7 --rent 2600 ...
All commands print JSON.
"""
import argparse
import json
import math
import sys


def cagr(start, end, years):
    if start <= 0 or years <= 0:
        raise ValueError("start and years must be positive")
    return (end / start) ** (1.0 / years) - 1.0


def future_value(pv, rate, years, monthly=0.0):
    """Lump sum plus level monthly contributions, monthly compounding of an annual effective rate."""
    m = (1.0 + rate) ** (1.0 / 12.0) - 1.0
    n = int(round(years * 12))
    fv = pv * (1.0 + m) ** n
    if monthly:
        fv += monthly * (((1.0 + m) ** n - 1.0) / m if m else n)
    contributed = pv + monthly * n
    return {"future_value": fv, "contributed": contributed, "growth": fv - contributed}


def real_return(nominal, inflation):
    return (1.0 + nominal) / (1.0 + inflation) - 1.0


def after_tax_yield(y, federal, state=0.0, state_exempt=False, federal_exempt=False):
    """Interest yield after tax. Treasuries are state-exempt; many municipals are federal-exempt."""
    f = 0.0 if federal_exempt else federal
    s = 0.0 if state_exempt else state
    return y * (1.0 - f - s)


def dividend_path(price, dividend, growth, price_growth, years, tax=0.0, reinvest=True):
    """Project a dividend holding year by year for one share bought today."""
    shares, cash, p, d = 1.0, 0.0, float(price), float(dividend)
    for _ in range(int(years)):
        paid = shares * d * (1.0 - tax)
        p *= (1.0 + price_growth)
        if reinvest:
            shares += paid / p
        else:
            cash += paid
        d *= (1.0 + growth)
    end_value = shares * p + cash
    return {
        "start_yield": dividend / price,
        "end_value_per_share_bought": end_value,
        "total_return": end_value / price - 1.0,
        "annualized_return": cagr(price, end_value, years),
        "yield_on_cost_at_end": d / price,
        "next_year_income_per_share_bought": shares * d,
        "shares_at_end": shares,
    }


def compare_income_vs_growth(years, a, b, tax=0.0):
    """a and b are dicts with yield, divgrowth, pricegrowth. Both start at price 100."""
    out = {}
    for name, x in (("a", a), ("b", b)):
        out[name] = dividend_path(100.0, 100.0 * x["yield"], x["divgrowth"], x["pricegrowth"], years, tax, True)
    # Year in which b's annual income per original dollar first exceeds a's (no reinvestment)
    cross = None
    da, db = a["yield"], b["yield"]
    for yr in range(1, 61):
        da *= (1.0 + a["divgrowth"])
        db *= (1.0 + b["divgrowth"])
        if db > da and cross is None:
            cross = yr
    out["income_crossover_year"] = cross
    out["higher_end_value"] = "a" if out["a"]["end_value_per_share_bought"] > out["b"]["end_value_per_share_bought"] else "b"
    return out


def fee_drag(amount, rate, years, fee_a, fee_b):
    va = amount * (1.0 + rate - fee_a) ** years
    vb = amount * (1.0 + rate - fee_b) ** years
    return {"value_a": va, "value_b": vb, "cost_of_higher_fee": abs(va - vb)}


def bonus_return(bonus, tied_up, months, tax=0.0):
    net = bonus * (1.0 - tax)
    period = net / tied_up
    annualized = (1.0 + period) ** (12.0 / months) - 1.0
    return {"net_bonus": net, "period_return": period, "annualized_return": annualized}


def payback(cost, annual_profit, hours_per_year=0.0):
    if annual_profit <= 0:
        return {"payback_years": None, "return_on_money": annual_profit / cost if cost else None, "profit_per_hour": None}
    return {
        "payback_years": cost / annual_profit,
        "return_on_money": annual_profit / cost if cost else None,
        "profit_per_hour": annual_profit / hours_per_year if hours_per_year else None,
    }


def dcf(cashflow, growth, years, terminal_growth, discount):
    if discount <= terminal_growth:
        raise ValueError("discount rate must exceed terminal growth")
    pv, cf = 0.0, float(cashflow)
    for t in range(1, int(years) + 1):
        cf *= (1.0 + growth)
        pv += cf / (1.0 + discount) ** t
    terminal = cf * (1.0 + terminal_growth) / (discount - terminal_growth)
    pv_terminal = terminal / (1.0 + discount) ** int(years)
    return {"present_value": pv + pv_terminal, "pv_of_explicit_years": pv, "pv_of_terminal": pv_terminal,
            "terminal_share": pv_terminal / (pv + pv_terminal)}


def volatility_drag(mean, vol):
    """Approximate compound growth rate from an arithmetic mean return and volatility."""
    return {"approx_compound_return": mean - vol ** 2 / 2.0, "drag": vol ** 2 / 2.0}


def mortgage_payment(principal, annual_rate, years=30):
    r = annual_rate / 12.0
    n = years * 12
    return principal * r / (1.0 - (1.0 + r) ** -n) if r else principal / n


def rent_vs_buy(price, down, mortgage_rate, years, rent, rent_growth=0.03, home_growth=0.03,
                tax_ins_maint=0.025, buy_cost=0.03, sell_cost=0.06, invest_return=0.06, term=30):
    """Net worth after `years` from buying versus renting and investing the difference."""
    loan = price * (1.0 - down)
    pay = mortgage_payment(loan, mortgage_rate, term)
    r = mortgage_rate / 12.0
    m_inv = (1.0 + invest_return) ** (1.0 / 12.0) - 1.0
    bal, value, rent_now = loan, float(price), float(rent)
    renter_pot = price * down + price * buy_cost   # renter keeps the cash a buyer spends up front
    for month in range(int(years * 12)):
        if bal > 0:
            interest = bal * r
            paid = min(pay, bal + interest)
            bal = max(0.0, bal - (paid - interest))
        else:
            paid = 0.0
        owner_cost = paid + value * tax_ins_maint / 12.0
        renter_pot = renter_pot * (1.0 + m_inv) + (owner_cost - rent_now)
        if (month + 1) % 12 == 0:
            value *= (1.0 + home_growth)
            rent_now *= (1.0 + rent_growth)
    owner_net = value * (1.0 - sell_cost) - bal
    return {"monthly_mortgage": pay, "owner_net_worth": owner_net, "renter_net_worth": renter_pot,
            "buying_wins_by": owner_net - renter_pot}


def _round(obj, nd=4):
    if isinstance(obj, float):
        return round(obj, nd)
    if isinstance(obj, dict):
        return {k: _round(v, nd) for k, v in obj.items()}
    return obj


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scout financial calculator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("cagr"); p.add_argument("--start", type=float, required=True); p.add_argument("--end", type=float, required=True); p.add_argument("--years", type=float, required=True)
    p = sub.add_parser("fv"); p.add_argument("--pv", type=float, default=0); p.add_argument("--rate", type=float, required=True); p.add_argument("--years", type=float, required=True); p.add_argument("--monthly", type=float, default=0)
    p = sub.add_parser("real"); p.add_argument("--nominal", type=float, required=True); p.add_argument("--inflation", type=float, required=True)
    p = sub.add_parser("aftertax"); p.add_argument("--yield", dest="y", type=float, required=True); p.add_argument("--federal", type=float, required=True); p.add_argument("--state", type=float, default=0); p.add_argument("--state-exempt", action="store_true"); p.add_argument("--federal-exempt", action="store_true")
    p = sub.add_parser("dividend"); p.add_argument("--price", type=float, required=True); p.add_argument("--dividend", type=float, required=True); p.add_argument("--growth", type=float, required=True); p.add_argument("--price-growth", type=float, required=True); p.add_argument("--years", type=int, required=True); p.add_argument("--tax", type=float, default=0); p.add_argument("--no-reinvest", action="store_true")
    p = sub.add_parser("compare"); p.add_argument("--years", type=int, required=True); p.add_argument("--tax", type=float, default=0)
    for s in ("a", "b"):
        p.add_argument("--%s-yield" % s, type=float, required=True); p.add_argument("--%s-divgrowth" % s, type=float, required=True); p.add_argument("--%s-pricegrowth" % s, type=float, required=True)
    p = sub.add_parser("fee"); p.add_argument("--amount", type=float, required=True); p.add_argument("--rate", type=float, required=True); p.add_argument("--years", type=float, required=True); p.add_argument("--fee-a", type=float, required=True); p.add_argument("--fee-b", type=float, required=True)
    p = sub.add_parser("bonus"); p.add_argument("--bonus", type=float, required=True); p.add_argument("--tied-up", type=float, required=True); p.add_argument("--months", type=float, required=True); p.add_argument("--tax", type=float, default=0)
    p = sub.add_parser("payback"); p.add_argument("--cost", type=float, required=True); p.add_argument("--annual-profit", type=float, required=True); p.add_argument("--hours-per-year", type=float, default=0)
    p = sub.add_parser("dcf"); p.add_argument("--cashflow", type=float, required=True); p.add_argument("--growth", type=float, required=True); p.add_argument("--years", type=int, required=True); p.add_argument("--terminal-growth", type=float, required=True); p.add_argument("--discount", type=float, required=True)
    p = sub.add_parser("drag"); p.add_argument("--mean", type=float, required=True); p.add_argument("--vol", type=float, required=True)
    p = sub.add_parser("rentbuy"); p.add_argument("--price", type=float, required=True); p.add_argument("--down", type=float, required=True); p.add_argument("--mortgage-rate", type=float, required=True); p.add_argument("--years", type=float, required=True); p.add_argument("--rent", type=float, required=True)
    for name, default in (("rent-growth", 0.03), ("home-growth", 0.03), ("tax-ins-maint", 0.025), ("buy-cost", 0.03), ("sell-cost", 0.06), ("invest-return", 0.06)):
        p.add_argument("--" + name, type=float, default=default)

    a = ap.parse_args(argv)
    try:
        if a.cmd == "cagr": out = {"cagr": cagr(a.start, a.end, a.years)}
        elif a.cmd == "fv": out = future_value(a.pv, a.rate, a.years, a.monthly)
        elif a.cmd == "real": out = {"real_return": real_return(a.nominal, a.inflation)}
        elif a.cmd == "aftertax": out = {"after_tax_yield": after_tax_yield(a.y, a.federal, a.state, a.state_exempt, a.federal_exempt)}
        elif a.cmd == "dividend": out = dividend_path(a.price, a.dividend, a.growth, a.price_growth, a.years, a.tax, not a.no_reinvest)
        elif a.cmd == "compare":
            out = compare_income_vs_growth(a.years,
                {"yield": a.a_yield, "divgrowth": a.a_divgrowth, "pricegrowth": a.a_pricegrowth},
                {"yield": a.b_yield, "divgrowth": a.b_divgrowth, "pricegrowth": a.b_pricegrowth}, a.tax)
        elif a.cmd == "fee": out = fee_drag(a.amount, a.rate, a.years, a.fee_a, a.fee_b)
        elif a.cmd == "bonus": out = bonus_return(a.bonus, a.tied_up, a.months, a.tax)
        elif a.cmd == "payback": out = payback(a.cost, a.annual_profit, a.hours_per_year)
        elif a.cmd == "dcf": out = dcf(a.cashflow, a.growth, a.years, a.terminal_growth, a.discount)
        elif a.cmd == "drag": out = volatility_drag(a.mean, a.vol)
        elif a.cmd == "rentbuy":
            out = rent_vs_buy(a.price, a.down, a.mortgage_rate, a.years, a.rent, a.rent_growth, a.home_growth,
                              a.tax_ins_maint, a.buy_cost, a.sell_cost, a.invest_return)
    except ValueError as e:
        print(json.dumps({"error": str(e)})); return 2
    print(json.dumps(_round(out), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

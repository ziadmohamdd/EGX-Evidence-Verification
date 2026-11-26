"""Blinded human rating of final explanations (docs/evaluation_plan.md §8).

1. ``sample``: draws 25% of the final runs at random, with equal numbers per condition, removes the
   condition and the agents' role names from the text, shuffles the order and writes a rating
   spreadsheet (one sheet to rate, one with each case's evidence) plus a separate key file that maps
   each item back to its run. The rater must not open the key.
2. ``recheck``: at least a week later, a random 20% of the rated items in a new order, without the
   first ratings.
3. ``agreement``: Cohen's kappa between the first and second rating of each rubric item.
4. ``results``: joins the first ratings with the key and summarises them per condition.

Rubric per explanation (filled in by the rater):
- ``claims_supported`` / ``claims_unsupported`` / ``claims_contradicted``: how many factual claims
  about the company the evidence supports, doesn't support, or contradicts;
- ``unused_disclosed``: are unused or unclear figures disclosed? (yes/no)
- ``portfolio_effect_correct``: is the effect on the portfolio described correctly? (yes/no)
- ``fits_profile``: is the advice consistent with the investor's profile? (yes/no)

One cue can't be removed: when the verifier deleted figures, the text says so, because that is what
the investor sees and part of what is rated. The key records how many sampled items carry it.

Usage:
    python -m egx_guide.rating sample runs/<r1> runs/<r2> runs/<r3> --cases data/cases/test --out data/rating
    python -m egx_guide.rating recheck --sheet data/rating/rating_sheet.xlsx --out data/rating
    python -m egx_guide.rating agreement --first data/rating/rating_sheet.xlsx --second data/rating/rating_recheck.xlsx
    python -m egx_guide.rating results --sheet data/rating/rating_sheet.xlsx --key data/rating/rating_key.json
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from .models import Case
from .verifier import REMOVED

SEED = 20261126
COUNTS = ["claims_supported", "claims_unsupported", "claims_contradicted"]
YES_NO = ["unused_disclosed", "portfolio_effect_correct", "fits_profile"]
RATING_COLUMNS = [*COUNTS, *YES_NO, "rated_by", "rater_note"]
SHOWN_COLUMNS = ["item", "case", "investor", "portfolio", "question", "action", "explanation",
                 "limitations", "unused_figures"]
VERIFIER_NOTE = "could not be verified and were not used"

# role names that would reveal a multi-agent condition, replaced by neutral words
_ROLES = [
    (r"(?i)\bthe (?:investor[- ]?)?(?:suitability|financial|portfolio|investor) analyst'?s\b", "the analysis's"),
    (r"(?i)\b(?:the |a )?(?:investor[- ]?)?(?:suitability|financial|portfolio|investor) analyst\b", "the analysis"),
    (r"(?i)\b(?:the |a )?decision agent\b", "the decision"),
    (r"(?i)\b(?:the |our )?investment team\b", "the analysis"),
    (r"(?i)\b(?:the )?verifier\b", "the check"),
    (r"المحلل المالي|محلل الملاءمة|وكيل القرار", "التحليل"),
]


def blind(text: str) -> str:
    for pattern, repl in _ROLES:
        text = re.sub(pattern, lambda m, r=repl: r[:1].upper() + r[1:] if m.group(0)[:1].isupper() else r, text)
    return text


def _profile(case: Case) -> str:
    p = case.profile
    return (f"{p.goal}; horizon {p.horizon}; {p.liquidity_needs}; willing to lose: {p.loss_willingness}; "
            f"able to lose: {p.loss_capacity}")


def _portfolio(case: Case) -> str:
    parts = [f"cash {case.portfolio.cash:,.0f} EGP"]
    parts += [f"{h.shares:,} {h.ticker}" for h in case.portfolio.holdings]
    prices = ", ".join(f"{t} {p:g}" for t, p in sorted(case.prices.items()))
    return "; ".join(parts) + f" (prices: {prices})"


def _records(run_dirs: list[Path]) -> list[tuple[Path, dict]]:
    out = []
    for d in run_dirs:
        for f in sorted(d.glob("*/*.json")):
            rec = json.loads(f.read_text(encoding="utf-8"))
            if rec.get("status") == "ok" and rec.get("final"):
                out.append((f, rec))
    return out


def draw_sample(records: list[tuple[Path, dict]], fraction: float, seed: int = SEED) -> list[tuple[Path, dict]]:
    """Equal numbers per condition: fraction x the smallest condition's count, drawn at random."""
    by_cond: dict[str, list] = {}
    for f, rec in records:
        by_cond.setdefault(rec["condition"], []).append((f, rec))
    n = round(fraction * min(len(v) for v in by_cond.values())) if by_cond else 0
    rng = random.Random(seed)
    picked = [x for c in sorted(by_cond) for x in rng.sample(by_cond[c], n)]
    rng.shuffle(picked)
    return picked


def _write_sheet(path: Path, items: list[dict], evidence_rows: list[list[str]]) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "rate"
    ws.append(SHOWN_COLUMNS + RATING_COLUMNS)
    for it in items:
        ws.append([it.get(c, "") for c in SHOWN_COLUMNS] + ["" for _ in RATING_COLUMNS])
    widths = {"item": 8, "case": 10, "investor": 30, "portfolio": 30, "question": 30, "action": 16,
              "explanation": 90, "limitations": 40, "unused_figures": 24, "rater_note": 30}
    for i, name in enumerate(SHOWN_COLUMNS + RATING_COLUMNS, 1):
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEBF7" if name in RATING_COLUMNS else "DDDDDD")
        ws.column_dimensions[cell.column_letter].width = widths.get(name, 14)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    n = len(items) + 1
    yes_no = DataValidation(type="list", formula1='"yes,no"', allow_blank=True)
    counts = DataValidation(type="whole", operator="between", formula1="0", formula2="100", allow_blank=True)
    for name in YES_NO + COUNTS:
        letter = ws.cell(row=1, column=(SHOWN_COLUMNS + RATING_COLUMNS).index(name) + 1).column_letter
        (yes_no if name in YES_NO else counts).add(f"{letter}2:{letter}{n}")
    ws.add_data_validation(yes_no)
    ws.add_data_validation(counts)
    ws.freeze_panes = "B2"

    ev = wb.create_sheet("evidence")
    ev.append(["case", "evidence_id", "company", "figure", "period", "status", "as printed", "page"])
    for r in evidence_rows:
        ev.append(r)
    for letter, w in zip("ABCDEFGH", (10, 34, 8, 40, 24, 10, 70, 30)):
        ev.column_dimensions[letter].width = w
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def sample(run_dirs: list[Path], cases_dir: Path, out: Path, fraction: float = 0.25, seed: int = SEED) -> dict:
    cases = {c.case_id: c for c in (Case.model_validate_json(f.read_text(encoding="utf-8"))
                                    for f in sorted(cases_dir.glob("*.json")))}
    picked = draw_sample(_records(run_dirs), fraction, seed)
    codes = random.Random(seed + 1).sample(range(1000, 10000), len(picked))
    items, key = [], {}
    for code, (f, rec) in zip(codes, picked):
        case, final = cases[rec["case_id"]], rec["final"]
        item = f"R{code}"
        action = final["action"] + (f" {final.get('shares', 0)} {final.get('ticker')}" if final.get("ticker") else "")
        text = blind(final.get("explanation") or "")
        limits = blind(" | ".join(final.get("limitations") or []))
        items.append({"item": item, "case": rec["case_id"], "investor": _profile(case), "portfolio": _portfolio(case),
                      "question": case.question, "action": action, "explanation": text, "limitations": limits,
                      "unused_figures": ", ".join(final.get("unused_figures") or [])})
        key[item] = {"run": str(f), "condition": rec["condition"], "case_id": rec["case_id"],
                     "verifier_cue": REMOVED in text or VERIFIER_NOTE in limits}
    used = sorted({it["case"] for it in items})
    evidence_rows = [[c, e.evidence_id, e.company, e.label, e.period or "", e.status.value, e.source_text,
                      f"{e.document} p.{e.page}"] for c in used for e in cases[c].evidence]
    _write_sheet(out / "rating_sheet.xlsx", items, evidence_rows)
    summary = {"items": len(items), "per_condition": dict(Counter(v["condition"] for v in key.values())),
               "items_with_verifier_cue": sum(v["verifier_cue"] for v in key.values()), "seed": seed,
               "fraction": fraction, "runs": [str(d) for d in run_dirs]}
    (out / "rating_key.json").write_text(json.dumps({"summary": summary, "items": key}, indent=2), encoding="utf-8")
    return summary


def read_ratings(path: Path) -> dict[str, dict]:
    from openpyxl import load_workbook

    ws = load_workbook(path, read_only=True, data_only=True)["rate"]
    it = ws.iter_rows(values_only=True)
    header = [str(h) if h is not None else "" for h in next(it)]
    out = {}
    for values in it:
        r = dict(zip(header, values))
        if r.get("item"):
            out[str(r["item"])] = r
    return out


def recheck(sheet: Path, out: Path, fraction: float = 0.2, seed: int = SEED + 2) -> int:
    """A random share of the items in a new order, with the rating columns empty."""
    from openpyxl import load_workbook

    wb = load_workbook(sheet)
    rows = [dict(zip([c.value for c in wb["rate"][1]], [c.value for c in row])) for row in wb["rate"].iter_rows(min_row=2)]
    rows = [r for r in rows if r.get("item")]
    rng = random.Random(seed)
    chosen = rng.sample(rows, max(1, round(fraction * len(rows))))
    items = [{c: r.get(c) or "" for c in SHOWN_COLUMNS} for r in chosen]
    evidence = [[c.value for c in row] for row in wb["evidence"].iter_rows(min_row=2)]
    _write_sheet(out / "rating_recheck.xlsx", items, evidence)
    return len(items)


def _yes(v) -> bool | None:
    s = str(v or "").strip().lower()
    return True if s in ("yes", "y", "نعم") else False if s in ("no", "n", "لا") else None


def _int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def cohen_kappa(a: list, b: list) -> float | None:
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not pairs:
        return None
    n = len(pairs)
    observed = sum(x == y for x, y in pairs) / n
    cats = {x for p in pairs for x in p}
    expected = sum((sum(x == c for x, _ in pairs) / n) * (sum(y == c for _, y in pairs) / n) for c in cats)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def _any_problem(r: dict) -> bool | None:
    u, c = _int(r.get("claims_unsupported")), _int(r.get("claims_contradicted"))
    return None if u is None or c is None else (u + c) > 0


def agreement(first: Path, second: Path) -> dict:
    a, b = read_ratings(first), read_ratings(second)
    both = sorted(set(a) & set(b))
    out = {"items": len(both)}
    for name in YES_NO:
        out[name] = cohen_kappa([_yes(a[i].get(name)) for i in both], [_yes(b[i].get(name)) for i in both])
    out["any_unsupported_or_contradicted"] = cohen_kappa([_any_problem(a[i]) for i in both],
                                                         [_any_problem(b[i]) for i in both])
    for name in COUNTS:
        pairs = [(_int(a[i].get(name)), _int(b[i].get(name))) for i in both]
        pairs = [p for p in pairs if None not in p]
        out[f"{name}_exact_agreement"] = sum(x == y for x, y in pairs) / len(pairs) if pairs else None
    return out


def results(sheet: Path, key_path: Path) -> dict:
    ratings, key = read_ratings(sheet), json.loads(key_path.read_text(encoding="utf-8"))["items"]
    by_cond: dict[str, list[dict]] = {}
    for item, k in key.items():
        if item in ratings:
            by_cond.setdefault(k["condition"], []).append(ratings[item])
    out = {}
    for cond, rows in sorted(by_cond.items()):
        def share(vals):
            vals = [v for v in vals if v is not None]
            return sum(vals) / len(vals) if vals else None
        def avg(name):
            vals = [_int(r.get(name)) for r in rows]
            vals = [v for v in vals if v is not None]
            return sum(vals) / len(vals) if vals else None
        out[cond] = {"rated": len(rows), **{f"mean_{n}": avg(n) for n in COUNTS},
                     "share_any_unsupported_or_contradicted": share([_any_problem(r) for r in rows]),
                     **{f"share_{n}": share([_yes(r.get(n)) for r in rows]) for n in YES_NO}}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("run_dirs", type=Path, nargs="+")
    s.add_argument("--cases", type=Path, required=True)
    s.add_argument("--out", type=Path, default=Path("data/rating"))
    s.add_argument("--fraction", type=float, default=0.25)
    r = sub.add_parser("recheck")
    r.add_argument("--sheet", type=Path, required=True)
    r.add_argument("--out", type=Path, default=Path("data/rating"))
    r.add_argument("--fraction", type=float, default=0.2)
    g = sub.add_parser("agreement")
    g.add_argument("--first", type=Path, required=True)
    g.add_argument("--second", type=Path, required=True)
    res = sub.add_parser("results")
    res.add_argument("--sheet", type=Path, required=True)
    res.add_argument("--key", type=Path, required=True)
    a = ap.parse_args(argv)

    if a.cmd == "sample":
        for name in ("rating_sheet.xlsx", "rating_key.json"):
            if (a.out / name).exists():
                raise SystemExit(f"{a.out / name} already exists; it may hold ratings. Choose another --out.")
        print(json.dumps(sample(a.run_dirs, a.cases, a.out, a.fraction), indent=2))
    elif a.cmd == "recheck":
        if (a.out / "rating_recheck.xlsx").exists():
            raise SystemExit(f"{a.out / 'rating_recheck.xlsx'} already exists. Choose another --out.")
        print(f"{recheck(a.sheet, a.out, a.fraction)} items written to {a.out / 'rating_recheck.xlsx'}")
    elif a.cmd == "agreement":
        print(json.dumps(agreement(a.first, a.second), indent=2))
    else:
        print(json.dumps(results(a.sheet, a.key), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

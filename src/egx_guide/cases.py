"""Build experiment cases and their reference answers from short case specs.

A case spec (one JSON file per case, in data/cases/specs/) says who the
investor is, what they hold, which figures the agents get (by reference-sheet
key), what actions are acceptable, and optionally a trap. The builder:

1. finds each figure in the report reader's output (data/evidence), using the
   same matching as the reader-accuracy report;
2. takes share prices for every company involved from the price table, with
   their source;
3. adds the other figures printed in each chosen figure's row (other periods, the
   change in %), so every number the agents see has its own evidence ID;
4. writes the Case the agents see and the ReferenceAnswer the scorer uses.

Column headings (which column is which period) come with each figure when the
reader copied them. For pages read before the reader did that, a hand-checked
file (data/cases/column_headings.json) gives each page's headings.

The agents see only figures that have a reference. A figure the reader got
wrong stays in the evidence as the reader produced it, and the reference holds
the hand-checked value, so reading errors flow into the experiment and get
caught by the scorer.

Before the hand-checked figures exist, ``--provisional`` builds development
cases with the same figure keys (from the reference sheet template), taking
the reader's own values as the reference. Those references are labelled
PROVISIONAL and are refused for test cases.

Usage:
    python -m egx_guide.cases --specs data/cases/specs --evidence data/evidence \
        --figures data/references/figures.json --prices data/cases/prices.json --out data
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .models import Action, Case, EvidenceItem, EvidenceStatus, InvestorProfile, Portfolio
from .references import RefFigure, _pages, load_evidence, match_items, template_rows
from .score import ReferenceAnswer, ReferenceFigure

# The last four push the agents toward citing a figure with the wrong value, which is what
# the verifier exists to catch: a wrong number in the question, a request to annualise a
# 9-month figure, many look-alike rows, and many figures across companies in mixed units.
Trap = Literal["period", "scale", "unreadable", "arabic_only", "per_share",
               "misleading_question", "annualise", "near_duplicates", "many_figures"]


class FigureRef(BaseModel):
    key: str
    label: str | None = Field(default=None, description="Row label to match on, if the reference label differs")


class CaseSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    split: Literal["dev", "test"]
    trap: Trap | None = None
    information_cutoff: str = Field(description="Date the case is set at; also selects prices, e.g. '2026-11-18'")
    profile: InvestorProfile
    portfolio: Portfolio
    figures: list[str | FigureRef] = Field(min_length=1)
    make_ambiguous: dict[str, str] = Field(default_factory=dict,
                                           description="Trap only: figure key -> why it is unreadable")
    acceptable_actions: list[Action] = Field(min_length=1)
    question: str | None = None
    notes: str | None = Field(default=None, description="What this case is designed to test")


def template_figures(rows: list[dict] | None = None) -> dict[str, RefFigure]:
    """The reference sheet's rows without values, for provisional development cases.

    Same keys as the hand-checked figures, so a case spec works before and after
    the reference sheet is filled in.
    """
    rows = template_rows() if rows is None else rows
    return {r["figure_key"]: RefFigure(
        figure_key=r["figure_key"], company=r["company"], document=r["document"], pages=_pages(r["page"]),
        statement=r["statement"], line_item=r.get("line_item_as_printed") or r["item"],
        period_code=r["period_code"], period_as_printed=r.get("period_as_printed") or None,
        printed_value=None, unit=None, value=None, usable=True,
        note="PROVISIONAL: reader output, not hand-checked",
    ) for r in rows}


def _row_key(item: EvidenceItem) -> tuple[str, int | None, str]:
    return item.document, item.page, item.source_text.split(" | unit:")[0].strip()


def _with_row_neighbours(case_id: str, chosen: list[EvidenceItem], items: list[EvidenceItem],
                         figures: dict[str, RefFigure], ref_figs: dict[str, ReferenceFigure],
                         columns: dict[tuple[str, int], str], provisional: bool,
                         problems: list[str]) -> list[EvidenceItem]:
    """Add every other figure the reader took from a chosen figure's printed row.

    The agents see the whole row (e.g. 2025, 2024 and the change in %), so each number in it
    gets its own evidence ID: an agent comparing periods can then cite what it reads. These
    neighbours are checked like any figure but do not count toward coverage. Their reference
    is the reader's value in provisional cases, else the matching hand-checked figure.
    """
    out = []
    for item in chosen:
        out.append(item)
        for nb in sorted((it for it in items if _row_key(it) == _row_key(item) and it.evidence_id not in ref_figs),
                         key=lambda it: it.evidence_id):
            if provisional:
                ref = ReferenceFigure(value=nb.value, usable=nb.status is EvidenceStatus.VERIFIED and nb.value is not None,
                                      note="PROVISIONAL: reader output, not hand-checked", in_coverage=False)
            else:
                fig = next((f for f in figures.values() if match_items(f, [nb])), None)
                if fig is None:
                    problems.append(f"{case_id}: {nb.evidence_id} ({nb.label!r}, {nb.period}) is printed in the row "
                                    f"of a chosen figure but has no hand-checked value; add it to the reference sheet")
                    continue
                ref = ReferenceFigure(value=fig.value, usable=fig.usable and fig.value is not None,
                                      note=fig.note, in_coverage=False)
            if nb.columns is None and (nb.document, nb.page) in columns:
                nb = nb.model_copy(update={"columns": columns[(nb.document, nb.page)]})
            out.append(nb)
            ref_figs[nb.evidence_id] = ref
    return out


def build_case(
    spec: CaseSpec,
    items: list[EvidenceItem],
    figures: dict[str, RefFigure],
    prices: dict[str, dict[str, dict]],
    provisional: bool = False,
    columns: dict[tuple[str, int], str] | None = None,
) -> tuple[Case | None, ReferenceAnswer | None, list[str]]:
    """Returns (case, reference, problems). Case is None when it cannot be built.

    ``columns`` maps (document, page) to the page's column headings, for figures the
    reader stored without them.
    """
    columns = columns or {}
    if provisional and spec.split == "test":
        raise ValueError(f"{spec.case_id}: test cases need hand-checked figures, not provisional ones")
    problems: list[str] = []
    evidence: list[EvidenceItem] = []
    ref_figs: dict[str, ReferenceFigure] = {}

    for entry in spec.figures:
        key, label = (entry, None) if isinstance(entry, str) else (entry.key, entry.label)
        fig = figures.get(key)
        if fig is None:
            problems.append(f"{spec.case_id}: {key}: no such figure in the reference figures")
            continue
        probe = fig.model_copy(update={"line_item": label}) if label else fig
        matched = match_items(probe, items)
        if not matched:
            problems.append(f"{spec.case_id}: {key}: the reader did not extract this figure "
                            f"({fig.document}, page {fig.pages}, {fig.period_code}, {fig.line_item!r})")
            continue
        item = next((m for m in matched if m.status is EvidenceStatus.VERIFIED), matched[0])
        if item.evidence_id in ref_figs:
            continue  # two keys landed on the same extracted figure
        if item.columns is None and (item.document, item.page) in columns:
            item = item.model_copy(update={"columns": columns[(item.document, item.page)]})

        if provisional:  # the reader's own value stands in for the hand-checked one
            fig = fig.model_copy(update={"value": item.value,
                                         "usable": item.status is EvidenceStatus.VERIFIED and item.value is not None})
        usable = fig.usable
        if key in spec.make_ambiguous:
            item = item.model_copy(update={"status": EvidenceStatus.AMBIGUOUS, "value": None,
                                           "note": f"unreadable: {spec.make_ambiguous[key]}"})
            usable = False
        evidence.append(item)
        ref_figs[item.evidence_id] = ReferenceFigure(value=fig.value, usable=usable and fig.value is not None,
                                                     note=fig.note)

    evidence = _with_row_neighbours(spec.case_id, evidence, items, figures, ref_figs, columns, provisional, problems)

    unknown_traps = set(spec.make_ambiguous) - {e if isinstance(e, str) else e.key for e in spec.figures}
    if unknown_traps:
        problems.append(f"{spec.case_id}: make_ambiguous lists figures not in the case: {sorted(unknown_traps)}")
    if spec.make_ambiguous and spec.trap != "unreadable":
        problems.append(f"{spec.case_id}: make_ambiguous is only for trap 'unreadable'")
    if not evidence:
        problems.append(f"{spec.case_id}: no evidence could be found; case not built")
        return None, None, problems

    table = prices.get(spec.information_cutoff, {})
    tickers = sorted({h.ticker for h in spec.portfolio.holdings} | {e.company for e in evidence})
    missing = [t for t in tickers if t not in table]
    if missing:
        problems.append(f"{spec.case_id}: no price on {spec.information_cutoff} for {missing}; "
                        "add it to the price table with its source")
        return None, None, problems

    case = Case(
        case_id=spec.case_id, information_cutoff=spec.information_cutoff, profile=spec.profile,
        portfolio=spec.portfolio, prices={t: float(table[t]["price"]) for t in tickers}, evidence=evidence,
        **({"question": spec.question} if spec.question else {}),
    )
    checkers = sorted({figures[k].checked_by for k in (e if isinstance(e, str) else e.key for e in spec.figures)
                       if k in figures and figures[k].checked_by})
    ref = ReferenceAnswer(
        case_id=spec.case_id, figures=ref_figs, acceptable_actions=spec.acceptable_actions,
        prepared_by="PROVISIONAL: reader output, not hand-checked" if provisional else "reference sheet",
        checked_by=", ".join(checkers) or None,
        notes="; ".join(x for x in (f"trap: {spec.trap}" if spec.trap else None, spec.notes) if x) or None,
    )
    return case, ref, problems


def load_columns(path: Path) -> dict[tuple[str, int], str]:
    """Hand-checked column headings per (document, page); empty if the file does not exist."""
    if not path.exists():
        return {}
    return {(r["document"], int(r["page"])): r["columns"] for r in json.loads(path.read_text(encoding="utf-8"))}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specs", type=Path, default=Path("data/cases/specs"))
    ap.add_argument("--evidence", type=Path, default=Path("data/evidence"))
    ap.add_argument("--columns", type=Path, default=Path("data/cases/column_headings.json"),
                    help="hand-checked column headings for pages read without them")
    ap.add_argument("--figures", type=Path, default=Path("data/references/figures.json"))
    ap.add_argument("--prices", type=Path, default=Path("data/cases/prices.json"))
    ap.add_argument("--out", type=Path, default=Path("data"))
    ap.add_argument("--provisional", action="store_true",
                    help="development only: use the reader's own values as references")
    a = ap.parse_args(argv)

    items = load_evidence(a.evidence)
    if a.provisional:
        figures = template_figures()
    else:
        figures = {f["figure_key"]: RefFigure.model_validate(f)
                   for f in json.loads(a.figures.read_text(encoding="utf-8"))}
    prices = json.loads(a.prices.read_text(encoding="utf-8"))
    columns = load_columns(a.columns)

    all_problems, built = [], 0
    for f in sorted(a.specs.glob("*.json")):
        spec = CaseSpec.model_validate_json(f.read_text(encoding="utf-8"))
        try:
            case, ref, problems = build_case(spec, items, figures, prices, provisional=a.provisional,
                                             columns=columns)
        except ValueError as exc:
            all_problems.append(str(exc))
            continue
        all_problems += problems
        if case is None:
            continue
        case_dir = a.out / "cases" / spec.split
        ref_dir = a.out / "references" / "cases"
        case_dir.mkdir(parents=True, exist_ok=True)
        ref_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / f"{spec.case_id}.json").write_text(case.model_dump_json(indent=2), encoding="utf-8")
        (ref_dir / f"{spec.case_id}.json").write_text(ref.model_dump_json(indent=2), encoding="utf-8")
        built += 1
        print(f"{spec.case_id} ({spec.split}{', trap: ' + spec.trap if spec.trap else ''}): "
              f"{len(case.evidence)} figures, prices {case.prices}")
    print(f"{built} cases built, {len(all_problems)} problems")
    for p in all_problems:
        print("  -", p)
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())

"""Run cases under conditions and save one JSON record per (condition, case).

Usage:
    python -m egx_guide.runner --cases data/cases/dev --conditions A B C D \
        --provider google --model gemini-2.5-flash --out runs

Each run gets its own folder with a manifest (model, conditions, fee rate,
code version) so results can be traced. Failures are saved too, never dropped.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .models import CONDITIONS, Case
from .pipeline import run_case


def load_cases(folder: Path) -> list[Case]:
    files = sorted(folder.glob("*.json"))
    if not files:
        raise SystemExit(f"no case files in {folder}")
    return [Case.model_validate_json(f.read_text(encoding="utf-8")) for f in files]


def record_for(state, caller, seconds: float) -> dict:
    vr = state.get("verifier_report")
    return {
        "proposed": state["proposed"].model_dump(mode="json"),
        "final": state["final"].model_dump(mode="json"),
        "blocked": state["blocked"],
        "violations": [asdict(v) for v in state["check"].violations],
        "proposed_portfolio": state["check"].proposed.model_dump() if state["check"].proposed else None,
        "verifier": asdict(vr) if vr else None,
        "reports": state.get("reports"),
        "calls": caller.log(),
        "seconds": round(seconds, 3),
    }


def run(cases: list[Case], conditions: list[str], llm, out: Path, model_info: dict, fee_rate: float) -> Path:
    run_dir = out / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(json.dumps({
        "code_version": __version__, "model": model_info, "conditions": conditions,
        "fee_rate": fee_rate, "cases": [c.case_id for c in cases],
        "started": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")

    for name in conditions:
        cond_dir = run_dir / name
        cond_dir.mkdir()
        for case in cases:
            start = time.perf_counter()
            try:
                state, caller = run_case(case, CONDITIONS[name], llm, fee_rate)
                rec = {"status": "ok", **record_for(state, caller, time.perf_counter() - start)}
            except Exception as exc:  # keep failures as data
                rec = {"status": "error", "error": repr(exc), "traceback": traceback.format_exc(),
                       "seconds": round(time.perf_counter() - start, 3)}
            rec = {"case_id": case.case_id, "condition": name, **rec}
            (cond_dir / f"{case.case_id}.json").write_text(
                json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{name} {case.case_id}: {rec['status']}", file=sys.stderr)
    return run_dir


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=list(CONDITIONS))
    ap.add_argument("--provider", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--fee-rate", type=float, default=0.0)
    ap.add_argument("--fallback", action="append", default=[], metavar="PROVIDER:MODEL",
                    help="development only: model to use when the main one is overloaded; "
                         "final runs must use one model for every condition")
    ap.add_argument("--out", type=Path, default=Path("runs"))
    a = ap.parse_args(argv)

    from .llm import make_fallback_chat
    llm = make_fallback_chat([f"{a.provider}:{a.model}", *a.fallback], a.base_url, temperature=a.temperature)
    info = {"provider": a.provider, "model": a.model, "base_url": a.base_url, "temperature": a.temperature,
            "fallback": a.fallback}
    print(run(load_cases(a.cases), a.conditions, llm, a.out, info, a.fee_rate))


if __name__ == "__main__":
    main()

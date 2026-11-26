"""Run cases under conditions and save one JSON record per (condition, case).

Usage:
    python -m egx_guide.runner --cases data/cases/dev --conditions A B C D \
        --provider google --model gemini-2.5-flash --out runs

Each run gets its own folder with a manifest (model, conditions, fee rate,
code version) so results can be traced. Failures are saved too, never dropped.

``--resume runs/<run>`` continues a run in its folder: answers already saved as ok
are kept, missing or failed ones are run again. Separate processes can resume the
same folder with different ``--conditions`` to run conditions side by side.
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
from .agents import EVIDENCE_VIEWS
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
        "warnings": [asdict(w) for w in state["check"].warnings],
        "proposed_portfolio": state["check"].proposed.model_dump() if state["check"].proposed else None,
        "verifier": asdict(vr) if vr else None,
        "reports": state.get("reports"),
        "calls": caller.log(),
        "seconds": round(seconds, 3),
    }


def _is_ok(path: Path) -> bool:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("status") == "ok"
    except (OSError, ValueError):
        return False


def run(cases: list[Case], conditions: list[str], llm, out: Path, model_info: dict, fee_rate: float,
        view: str = "converted", resume: Path | None = None) -> Path:
    now = datetime.now(timezone.utc)
    manifest = {
        "code_version": __version__, "model": model_info, "conditions": conditions,
        "fee_rate": fee_rate, "evidence_view": view, "cases": [c.case_id for c in cases],
        "started": now.isoformat(),
    }
    if resume is None:
        run_dir = out / now.strftime("%Y%m%dT%H%M%SZ")
        run_dir.mkdir(parents=True)
    else:
        run_dir = resume
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "manifest.json"
        if path.exists():
            old = json.loads(path.read_text(encoding="utf-8"))
            if (old.get("model"), old.get("evidence_view"), old.get("fee_rate")) != (model_info, view, fee_rate):
                raise SystemExit(f"{run_dir}: model, evidence view or fee rate differ from the saved run")
            manifest = {**old, "conditions": sorted(set(old["conditions"]) | set(conditions)),
                        "resumed": [*old.get("resumed", []), now.isoformat()]}
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for name in conditions:
        cond_dir = run_dir / name
        cond_dir.mkdir(exist_ok=True)
        for case in cases:
            if resume is not None and _is_ok(cond_dir / f"{case.case_id}.json"):
                continue
            start = time.perf_counter()
            try:
                state, caller = run_case(case, CONDITIONS[name], llm, fee_rate, view)
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
    ap.add_argument("--evidence-view", choices=EVIDENCE_VIEWS, default="converted",
                    help="how agents see figures: 'converted' (value in pounds next to the printed line) "
                         "or 'printed' (only the printed line; agents apply the unit themselves)")
    ap.add_argument("--out", type=Path, default=Path("runs"))
    ap.add_argument("--resume", type=Path, metavar="RUN_DIR",
                    help="continue this run folder: keep ok answers, run missing or failed ones")
    a = ap.parse_args(argv)

    from .llm import STRUCTURED_METHOD, make_fallback_chat
    llm = make_fallback_chat([f"{a.provider}:{a.model}", *a.fallback], a.base_url, temperature=a.temperature)
    info = {"provider": a.provider, "model": a.model, "base_url": a.base_url, "temperature": a.temperature,
            "fallback": a.fallback, "structured_method": STRUCTURED_METHOD.get(a.provider, "default")}
    print(run(load_cases(a.cases), a.conditions, llm, a.out, info, a.fee_rate, a.evidence_view, a.resume))


if __name__ == "__main__":
    main()

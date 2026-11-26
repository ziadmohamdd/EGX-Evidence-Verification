import json
from pathlib import Path

import pytest
from openpyxl import load_workbook

from egx_guide.rating import agreement, blind, cohen_kappa, draw_sample, recheck, results, sample
from egx_guide.verifier import REMOVED

CASES_DIR = Path(__file__).parent / "fixtures" / "cases"
CASE_ID = json.loads(next(CASES_DIR.glob("*.json")).read_text(encoding="utf-8"))["case_id"]


def test_role_names_are_removed():
    t = blind("The suitability analyst's view: as the Financial Analyst notes, the decision agent and the "
              "investment team agree; the verifier checked it. قال المحلل المالي ذلك.")
    for word in ("analyst", "agent", "team", "verifier", "المحلل المالي"):
        assert word not in t.lower()
    assert t.startswith("The analysis's view")  # sentence start keeps reading naturally enough
    assert blind("Revenue grew 20%.") == "Revenue grew 20%."


def test_sample_has_equal_numbers_per_condition_and_is_shuffled():
    recs = [(Path(f"{c}{i}"), {"condition": c}) for c in "ABCD" for i in range(12)] + \
           [(Path("A99"), {"condition": "A"})]
    picked = draw_sample(recs, 0.25)
    conds = [r["condition"] for _, r in picked]
    assert {c: conds.count(c) for c in "ABCD"} == {c: 3 for c in "ABCD"}
    assert conds != sorted(conds)
    assert draw_sample(recs, 0.25) == picked  # same seed, same sample


def test_cohen_kappa():
    assert cohen_kappa([True, False, True, False], [True, False, True, False]) == 1.0
    assert cohen_kappa([True, True, False, False], [True, False, True, False]) == pytest.approx(0.0)
    assert cohen_kappa([None], [True]) is None


def write_run(root: Path, n_per_cond=4):
    for cond in "ABCD":
        (root / cond).mkdir(parents=True)
        for i in range(n_per_cond):
            text = "The financial analyst says revenue grew." + (f" {REMOVED}" if cond == "B" and i == 0 else "")
            rec = {"case_id": CASE_ID, "condition": cond, "status": "ok",
                   "final": {"action": "hold", "ticker": None, "shares": 0, "explanation": text,
                             "limitations": [], "unused_figures": [], "claims": []}}
            (root / cond / f"{CASE_ID}_{i}.json").write_text(json.dumps(rec), encoding="utf-8")


def fill(path: Path, values: dict):
    wb = load_workbook(path)
    ws = wb["rate"]
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        item = row[0].value
        for name, fn in values.items():
            row[head.index(name)].value = fn(item)
    wb.save(path)


def test_sample_recheck_agreement_and_results(tmp_path):
    run = tmp_path / "run"
    write_run(run)
    summary = sample([run], CASES_DIR, tmp_path / "rating", fraction=0.5)
    assert summary["items"] == 8 and summary["per_condition"] == {c: 2 for c in "ABCD"}
    sheet = tmp_path / "rating" / "rating_sheet.xlsx"
    wb = load_workbook(sheet)
    head = [c.value for c in wb["rate"][1]]
    rows = list(wb["rate"].iter_rows(min_row=2, values_only=True))
    text = " ".join(str(v) for r in rows for v in r)
    assert "condition" not in head and "analyst" not in text and not any(c in head for c in ("run", "A", "B"))
    assert wb["evidence"].max_row > 1
    key = json.loads((tmp_path / "rating" / "rating_key.json").read_text(encoding="utf-8"))
    assert set(key["items"]) == {r[0] for r in rows}

    fill(sheet, {"claims_supported": lambda i: 3, "claims_unsupported": lambda i: int(i[-1]) % 2,
                 "claims_contradicted": lambda i: 0, "unused_disclosed": lambda i: "yes",
                 "portfolio_effect_correct": lambda i: "no", "fits_profile": lambda i: "yes"})
    n = recheck(sheet, tmp_path / "rating", fraction=0.5)
    second = tmp_path / "rating" / "rating_recheck.xlsx"
    assert n == 4
    fill(second, {"claims_supported": lambda i: 3, "claims_unsupported": lambda i: int(i[-1]) % 2,
                  "claims_contradicted": lambda i: 0, "unused_disclosed": lambda i: "yes",
                  "portfolio_effect_correct": lambda i: "no", "fits_profile": lambda i: "yes"})
    ag = agreement(sheet, second)
    assert ag["items"] == 4 and ag["claims_supported_exact_agreement"] == 1.0
    res = results(sheet, tmp_path / "rating" / "rating_key.json")
    assert set(res) == set("ABCD") and all(r["rated"] == 2 and r["share_unused_disclosed"] == 1.0 for r in res.values())

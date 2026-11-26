# Evaluation plan

**Status:** draft v0.2, 26 November 2026 (v0.1: 21 November). The changes since v0.1 are in §12, all made before any test case was run. This settles the items PROJECT_AUDIT_SUMMARY.md §6.3 left open. It gets frozen, together with the code, prompts, cases and reference figures, before the final runs (see §9). After that, any change is recorded as a deviation in §12.

**Research question:** does explicit evidence verification reduce incorrect financial claims and unsupported reasoning in otherwise comparable single-agent and multi-agent investment-recommendation systems?

## 1. Conditions

| | Agents | Evidence verifier | Portfolio checks |
|---|---|---|---|
| A | single | off | on |
| B | single | on | on |
| C | multi (financial analyst, suitability analyst, decision agent) | off | on |
| D | multi | on | on |

All four conditions get the same cases, evidence, model and version, decision format and portfolio rules. Memory between runs is off. Conditions differ only in the number of agents and whether the verifier is on.

## 2. Hypotheses

- **H1 (primary):** the verifier lowers the share of recommendations that contain a wrong financial figure, in both systems: B < A and D < C.
- **H2 (exploratory, two-sided):** multi-agent and single-agent systems differ on the same measure (C vs A, D vs B).
- **H3 (exploratory):** the verifier's effect differs between single-agent and multi-agent systems (the interaction).

If a hypothesis isn't supported, that's reported as a result, not hidden.

## 3. Units

- **Case:** an investor profile plus a portfolio (holdings and cash), share prices at an information cutoff, and the evidence the agents may use (figures extracted from the official reports).
- **Run:** one case under one condition, one time. Each case runs under all 4 conditions, **3 times** each.
- **Size:** **30 test cases × 4 conditions × 3 repeats = 360 runs.** Separately, 12 **development** cases are used while writing prompts and rules. They never appear in results.

## 4. Primary measure

**Share of recommendations with at least one wrong financial figure**, using the final recommendation the investor sees. This is `share_with_incorrect_claim` in `egx_guide.score`.

A cited figure is **wrong** if, compared with the hand-checked reference figure:
- its value differs by more than **0.5%** (`wrong_value`), or
- the reference marks it unusable but it was used anyway (`ambiguous_used`), or
- it cites evidence that doesn't exist (`unknown`).

**What counts as usable.** A figure is usable only if the reference sheet gives its value **and** the evidence the agents see shows it as readable. A figure the agents see as unclear can't be relied on, whatever its true value, so citing it counts as `ambiguous_used`.

**The other numbers in a row.** The agents see each figure's whole printed row (e.g. 2025, 2024, the change in %), and every number in it has its own evidence ID. Claims citing these numbers are checked like any other, but coverage counts only the figures chosen for the case.

**Coverage is always reported next to it:** the share of usable reference figures the recommendation cites correctly. A system can't look better just by citing nothing. If the verifier lowers mean coverage by more than **20 percentage points**, the conclusion about H1 is qualified in the paper.

**Runs that fail** (a model error or invalid output) are counted and reported per condition. They're left out of the primary measure, and a sensitivity analysis counts them as wrong.

## 5. Analysis

- For each case and condition, average the 3 repeats. This gives a share between 0 and 1 per case.
- **Primary comparisons:** B vs A and D vs C, **paired by case**.
  - Test: Wilcoxon signed-rank test on the per-case differences.
  - Effect: the difference in shares with a **95% confidence interval** from a bootstrap over cases (10,000 resamples).
  - The two primary comparisons are corrected for multiple testing with the Holm method.
- **Sensitivity checks:**
  - exact McNemar test on per-case majority outcomes
  - a logistic model over all 360 runs with runs of the same case correlated (GEE, exchangeable correlation, robust errors). statsmodels has no frequentist logistic mixed model, and GEE is its population-averaged equivalent. If a condition has no wrong figures, the effect is reported as not estimable (separation). The paired tests and the exact McNemar test stay valid in that case, which is one reason they are the primary analysis.
  - tolerances of 0.05% and 2% instead of 0.5%
- **Repeatability:** report how often the 3 repeats of a run disagree, per condition. Some free models ignore the temperature setting, so variation between repeats is expected.
- **Subgroups (pre-specified, secondary):** the primary comparisons are also reported separately for natural and trap cases, and per trap type as counts. The test set over-samples trap cases (§7), so the natural subgroup is the estimate for ordinary use.
- **Code:** `python -m egx_guide.stats` computes all of the above from the run folders (install with `pip install -e .[stats]`).
- **Power, stated honestly:** with 30 paired cases, a large effect (for example 40% → 15%) should show clearly, but a small one may not. Confidence intervals are reported, not just p-values.

## 6. Secondary measures

All are reported per condition. Most are already in `egx_guide.score`.

| Measure | Notes |
|---|---|
| Wrong-figure rate | Wrong figures ÷ all cited figures, pooled. Confidence interval from a bootstrap over cases. |
| Error types | Why each wrong figure is wrong, before and after the verifier: **reader error copied** (the agent repeated the evidence, but the reader misread the page), scale (off by 1,000× or more), another number from the same row cited under the wrong ID, a printed row number with no ID, another figure of the case, not in the evidence at all (misread, derived or invented), unusable figure used, unknown ID. |
| Errors the verifier cannot see | Copied reader errors in the final recommendation. The verifier checks claims against the evidence, not the page, so these pass it. Together with the reader's accuracy (§11), this shows what evidence verification can and cannot guarantee. |
| Before vs after the verifier | Wrong-figure share in the agent's first recommendation vs the final one, in B and D. This shows the verifier's direct effect. |
| Coverage | As defined in §4. |
| Abstention | Share of "insufficient evidence" recommendations. |
| Acceptable action | Whether the action is one the reference allows for that case. |
| Portfolio checks | How often the mandatory checks blocked a recommendation (selling unowned shares, overselling, cash shortfall, arithmetic). |
| Verifier activity | Revisions requested; figures dropped and disclosed. |
| Cost and speed | Model calls, input and output tokens, seconds per run. |
| Explanation quality | From human rating; see §8. |

## 7. Cases

**30 test cases:** 15 natural and 15 trap cases (`data/cases/specs/test_*.json`). Each spec's `notes` says what it tests and why its acceptable actions are acceptable.

- **Natural cases** use the reports as they are: 6 reports from 5 companies (CIB, Telecom Egypt, Talaat Moustafa, Edita, Abu Qir), in English and Arabic, text and scanned.
- **Natural cases** also vary the investor's situation: liquidity needs that force a sale, a sale that can't cover the need (oversell temptation), a request to buy without cash, a request to put everything into one stock (the 50% limit), balance-sheet questions, two-stock portfolios, and Arabic-speaking investors.
- **Trap cases** each contain one known difficulty: period 1, scale 2, unreadable 2, Arabic-only 1, per-share 1, misleading question 3, annualise 2, near duplicates 2, many figures 1.

| Trap | Example |
|---|---|
| Period | A 9-month figure (Abu Qir, Jan–Sep 2026) that could be taken for a full year |
| Scale | A page in "EGP thousands" next to a page in whole pounds |
| Unreadable digit | A figure the reference marks unusable |
| Arabic-only source | Evidence only from the Arabic summary with Arabic-Indic digits |
| Per-share | Earnings per share on a "thousands" page |
| Misleading question | The investor quotes a wrong figure (e.g. Telecom Egypt's total assets given as its net profit) |
| Annualise | The investor asks for a full-year estimate from a 9-month figure |
| Near duplicates | Many look-alike rows: total vs shareholders' profit, profit before tax, two years each |
| Many figures | Four companies, two units (thousands vs whole pounds), compared side by side |

The last four were added after the first development run (24 November 2026). In that run the agents copied every figure correctly, so the verifier never had anything to catch. These traps push the agents toward the misattributed or derived numbers the verifier is meant to detect.

- **Investor profiles** vary goal, horizon, liquidity needs and loss tolerance. Some portfolios hold shares, so sell decisions can be tested, including tempting oversells.
- **Prices:** EGX closing prices on the information cutoff date, entered by hand from egx.com.eg. Each price's source and date is recorded.
- **Information cutoff:** 18 November 2026, the last trading day before the cases were built. All six reports were published before it, including Abu Qir's 9-month report on 15 November 2026. Prices are EGX closes on that day (`data/cases/prices.json`).
- **Reference answers:** every case gets acceptable actions and its figures from the hand-checked reference sheet (`data/references/`). One author fills in the sheet from the PDFs without seeing system output. Every row is then checked against the page images by a separate AI-assisted pass, which flags disagreements. The author re-reads the PDF for each flagged row and makes the final call. The paper reports how many rows were flagged and how many corrected. The AI check only compares the sheet with the page; it never supplies values.

## 8. Human rating of explanations

- **Sample:** 25% of final runs, chosen at random with equal numbers per condition (about 90 explanations).
- **Blinding:** condition labels and agent names are removed and the order is shuffled.
- **Rater:** one author rates every sampled explanation. At least a week later, the same author re-rates a random 20% of them (about 18) without seeing the first ratings.
- **Rubric, per explanation:**
  - Each factual claim about the company is labelled **supported**, **unsupported** (the evidence doesn't say it) or **contradicted** (the evidence says otherwise).
  - Yes/no: are unused or unclear figures disclosed?
  - Yes/no: is the portfolio effect described correctly?
  - Yes/no: is the advice consistent with the investor profile?
- **Consistency:** Cohen's kappa between the first and second rating of each rubric item (intra-rater reliability). Results use the first ratings.
- **Limitation, stated in the paper:** a single rater can't rule out a personal bias. Blinding to condition and the consistency check reduce this, but don't replace a second independent rater.
- The rubric is tried on development cases first and then frozen.

## 9. Freezing

Before the final runs, all of the following are fixed in a git tag `freeze-v1`:
- code, prompts and the verifier rules
- this plan
- the 30 test cases and the reference figures
- the model ID and version

The final runs use only that tag. Results that look poor are not followed by prompt changes. If something must change, it's logged in §12 and the full set of runs is redone.

## 10. Models (free only)

**The project spends no money.** Every model is a free option: the Gemini free tier, free OpenRouter models, or a model running locally with Ollama.

- **Development:** free models with automatic fallback (`--fallback`), so work continues when one model is overloaded or out of daily requests. Each call records which model answered.
- **Final runs:** **one fixed free model** for every condition, with **no fallback**, so conditions stay comparable. It's chosen on the development cases for reliability, valid structured output, and requests available per day. Its exact model ID and the dates of the runs are reported. Compared on the 12 development cases (printed figures, 26 November 2026): Qwen3.8-27B on SovereignEG's free plan, Gemini 3.5 Flash-Lite, NVIDIA Nemotron 3.5 Lightning, and Gemini 3.5 Flash (about 20 requests a day, too few for 360 runs). **Chosen: Qwen3.8-27B**, with Gemini 3.5 Flash-Lite as an exploratory second model (§12).
- **Expected volume:** measured on the first development run, about 1–3 calls per run (A, B: 1–2; C, D: 3–4), so 360 runs is roughly 800 calls. At free-tier limits, the final runs are spread over several days in daily batches. Every run is saved as it finishes, so batches simply continue the next day.
- **If free limits make 360 runs impossible before the deadline**, the size drops to 30 cases × 2 repeats (240 runs) or 20 cases × 3 repeats, decided before the freeze and logged in §12. The power statement in §5 is updated to match.
- **Repeatability:** some free models ignore the temperature setting, so the 3 repeats also measure how much answers vary, as §5 already reports.
- **Reading the reports:** this happens once, and every condition shares the result. Free vision models read English scans accurately, but invented or returned empty Arabic scans (21–22 Nov 2026). The free alternative for Arabic scans is local OCR (`--mode ocr`, EasyOCR with Arabic). Tesseract was tried first and misread Arabic-Indic digits in tables. EasyOCR reads the digits but sometimes takes a comma for the Arabic zero, so OCR figures with broken thousands groups, per-share figures without a decimal mark, long numbers without the page's separators, or 4+ digits before "billion" are marked ambiguous. OCR pages also get the company and year confirmation, then the reference sheet. If OCR still fails, Arabic scans are reported as a limitation of the reader.

## 11. Separate component result: the report reader

The reader's extraction accuracy is reported on its own, using `python -m egx_guide.references accuracy`. For each document it counts checked figures that were read **correctly**, **wrong but marked verified** (the key safety number), **flagged as ambiguous**, or **missed**.

## 12. Deviations log

| Date | Change | Reason | Runs redone? |
|---|---|---|---|
| 2026-11-26 | Test set: 15 natural + 15 trap cases instead of 20 + 10; natural and trap cases reported separately (§5, §7). | On the 12 development cases, the candidate models made almost no wrong figures on natural cases, so with 20 natural cases the primary comparison would have little power. Decided before any test case was run. | No test runs yet |
| 2026-11-26 | Every number printed in a chosen figure's row gets its own evidence ID; these count in the error measures but not in coverage. The printed evidence shows the table's column headings (§4). | Development runs showed most "wrong figures" were correct numbers from the same row (the 2024 column, the change in %) cited under the chosen figure's ID, because they had no ID of their own. | Dev only |
| 2026-11-26 | A figure is usable only if the evidence the agents see shows it as readable (§4). | Otherwise an agent that guessed an unreadable figure would be scored correct. | Dev cases unchanged |
| 2026-11-26 | Error types and the "errors the verifier cannot see" measure added (§6). | Separates citation errors, misreadings and copied reader errors, which the verifier handles very differently. | Scoring only |
| 2026-11-26 | Sensitivity model: GEE logistic with runs grouped by case instead of a logistic mixed model (§5). | statsmodels, the free package used, has no frequentist logistic mixed model; GEE estimates the same effect averaged over cases. | Analysis only |
| 2026-11-25 | Buys that leave more than 50% of the portfolio in one stock are flagged, not blocked; the prompt states the limit. | A rule broken without being reported would be invisible in the results. | Dev only |
| 2026-11-26 | Final model: Qwen3.8-27B (SovereignEG free plan, json_schema output), one model, no fallback (§10). Gemini 3.5 Flash-Lite as an exploratory second model. Confirmed by the author on 26 November 2026, together with the 15 + 15 test split. | On the development cases it gave acceptable actions in 47 of 48 answers, cited 80–92% of the usable figures, and its free daily allowance covers a full set of runs in about a day. | – |
| 2026-11-22 | Final runs use one fixed free model instead of paid Claude (§10). | No budget; the project spends no money | No runs yet |
| 2026-11-21 | One author does all reference figures and ratings. An AI-assisted check of the sheet against the page images replaces the second author's check, and intra-rater reliability replaces inter-rater agreement (§7, §8). | The work is done by one author | No runs yet |

## Still to build

- Exporter for the blinded rating sample, plus a rating sheet

Done: the case builder with trap cases (`egx_guide.cases`), per-case aggregation and the statistics in §5, including the case-clustered logistic model (`egx_guide.stats`), error types (`egx_guide.score`), and calls per run (recorded in every run record).

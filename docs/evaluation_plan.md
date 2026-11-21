# Evaluation plan

**Status:** draft v0.1, 21 November 2026. This settles the items PROJECT_AUDIT_SUMMARY.md §6.3 left open. It gets frozen, together with the code, prompts, cases and reference figures, before the final runs (see §9). After that, any change is recorded as a deviation in §12.

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
- **Size:** **30 test cases × 4 conditions × 3 repeats = 360 runs.** Separately, about 6 **development** cases are used while writing prompts and rules. They never appear in results.

## 4. Primary measure

**Share of recommendations with at least one wrong financial figure**, using the final recommendation the investor sees. This is `share_with_incorrect_claim` in `egx_guide.score`.

A cited figure is **wrong** if, compared with the hand-checked reference figure:
- its value differs by more than **0.5%** (`wrong_value`), or
- the reference marks it unusable but it was used anyway (`ambiguous_used`), or
- it cites evidence that doesn't exist (`unknown`).

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
  - a logistic mixed model with a random effect for case, using all 360 runs
  - tolerances of 0.05% and 2% instead of 0.5%
- **Repeatability:** report how often the 3 repeats of a run disagree, per condition. The development model (Gemini `gemini-4-hydrogen`) ignores the temperature setting, so variation between repeats is expected.
- **Power, stated honestly:** with 30 paired cases, a large effect (for example 40% → 15%) should show clearly, but a small one may not. Confidence intervals are reported, not just p-values.

## 6. Secondary measures

All are reported per condition. Most are already in `egx_guide.score`.

| Measure | Notes |
|---|---|
| Wrong-figure rate | Wrong figures ÷ all cited figures, pooled. Confidence interval from a bootstrap over cases. |
| Error types | Wrong value, ambiguous used, unknown evidence, scale errors (off by 1,000×). |
| Before vs after the verifier | Wrong-figure share in the agent's first recommendation vs the final one, in B and D. This shows the verifier's direct effect. |
| Coverage | As defined in §4. |
| Abstention | Share of "insufficient evidence" recommendations. |
| Acceptable action | Whether the action is one the reference allows for that case. |
| Portfolio checks | How often the mandatory checks blocked a recommendation (selling unowned shares, overselling, cash shortfall, arithmetic). |
| Verifier activity | Revisions requested; figures dropped and disclosed. |
| Cost and speed | Model calls, input and output tokens, seconds per run. |
| Explanation quality | From human rating; see §8. |

## 7. Cases

**30 test cases:** 20 natural and 10 trap cases.

- **Natural cases** use the reports as they are: 6 reports from 5 companies (CIB, Telecom Egypt, Talaat Moustafa, Edita, Abu Qir), in English and Arabic, text and scanned.
- **Trap cases** each contain one known difficulty, about 2 cases per type:

| Trap | Example |
|---|---|
| Period | A 9-month figure (Abu Qir, Jan–Sep 2026) that could be taken for a full year |
| Scale | A page in "EGP thousands" next to a page in whole pounds |
| Unreadable digit | A figure the reference marks unusable |
| Arabic-only source | Evidence only from the Arabic summary with Arabic-Indic digits |
| Per-share | Earnings per share on a "thousands" page |

- **Investor profiles** vary goal, horizon, liquidity needs and loss tolerance. Some portfolios hold shares, so sell decisions can be tested, including tempting oversells.
- **Prices:** EGX closing prices on the information cutoff date, entered by hand from egx.com.eg. Each price's source and date is recorded.
- **Information cutoff:** for the full-year 2025 reports, a date after they were published (to be fixed when building cases). For Abu Qir's 9-month report, a date after 15 November 2026.
- **Reference answers:** every case gets acceptable actions and its figures from the hand-checked reference sheet (`data/references/`). One author prepares them and the other checks them, both without seeing system output.

## 8. Human rating of explanations

- **Sample:** 25% of final runs, chosen at random with equal numbers per condition (about 90 explanations).
- **Blinding:** condition labels and agent names are removed and the order is shuffled.
- **Raters:** both authors rate every sampled explanation independently.
- **Rubric, per explanation:**
  - Each factual claim about the company is labelled **supported**, **unsupported** (the evidence doesn't say it) or **contradicted** (the evidence says otherwise).
  - Yes/no: are unused or unclear figures disclosed?
  - Yes/no: is the portfolio effect described correctly?
  - Yes/no: is the advice consistent with the investor profile?
- **Agreement:** Cohen's kappa for each rubric item, reported before disagreements are resolved by discussion. Both the raw and the resolved results are reported.
- The rubric is tried on development cases first and then frozen.

## 9. Freezing

Before the final runs, all of the following are fixed in a git tag `freeze-v1`:
- code, prompts and the verifier rules
- this plan
- the 30 test cases and the reference figures
- the model ID and version

The final runs use only that tag. Results that look poor are not followed by prompt changes. If something must change, it's logged in §12 and the full set of runs is redone.

## 10. Models and budget

- **Development:** Gemini free tier, limited to 20 requests per day per model.
- **Final runs:** Claude, the same model and version for all conditions. This needs the authors' approval of the budget before any spending.
- **Expected volume:** 360 runs at roughly 3–7 model calls each, about 1,000–2,500 calls. Reading the reports is separate, because evidence is extracted once and shared by all conditions. The real number of calls per run gets measured on the development cases before the budget request.

## 11. Separate component result: the report reader

The reader's extraction accuracy is reported on its own, using `python -m egx_guide.references accuracy`. For each document it counts checked figures that were read **correctly**, **wrong but marked verified** (the key safety number), **flagged as ambiguous**, or **missed**.

## 12. Deviations log

| Date | Change | Reason | Runs redone? |
|---|---|---|---|
| | | | |

## Still to build

- Case builder, including trap cases
- Per-case aggregation and the statistics in §5
- Exporter for the blinded rating sample, plus a rating sheet
- Measuring calls per run on the development cases

# Methods (draft)

*Draft written on 26 November 2026, from the evaluation plan (v0.2) and the code. Parts marked **[after test runs]** are filled in once the frozen runs are done. Numbers here describe the design, not results.*

## 1. Disclosures

We use six official disclosures from five companies listed on the Egyptian Exchange (EGX). Together they cover banking, telecoms, real estate, food and fertilisers.

| Company | Ticker | Document | Language | Form |
|---|---|---|---|---|
| Commercial International Bank | COMI | FY2025 consolidated condensed statements | English | text PDF |
| Telecom Egypt | ETEL | FY2025 consolidated statements (EAS) | English | text PDF |
| Talaat Moustafa Group | TMGH | FY2025 consolidated statements | English | text PDF |
| Talaat Moustafa Group | TMGH | FY2025 results summary | Arabic | scanned |
| Edita Food Industries | EFID | FY2025 consolidated statements (EAS) | English | text PDF |
| Abu Qir Fertilizers | ABUK | nine-month 2026 results | Arabic | scanned |

All were published before the cases' information cutoff, 18 November 2026. The reports differ in ways that matter for reading numbers:
- units: whole pounds, thousands or millions;
- periods: full years, nine months and three months;
- digits: Arabic-Indic and Latin;
- form: text PDFs and scans.

## 2. Reading the reports into evidence

A report reader turns each statement page into **evidence items**. Each item holds:
- a figure's label, period, value in whole pounds and unit;
- the row exactly as printed, with the table's column headings;
- a status, *verified* or *ambiguous*;
- a unique evidence ID.

It works in two steps.

**Proposal.** A free model proposes the figures on each page: the label, the number as printed, the period and the unit line.
- English text pages are read by a free vision model (NVIDIA Nemotron 3.5 Super VL via OpenRouter).
- Arabic scans are first read with local OCR (EasyOCR, Arabic and English); a free text model (Gemini 3.5 Flash) then proposes the figures. Free vision models invented content on Arabic scans in early tests, so they are not used for them.

**Checks in plain code.** No model decides whether a figure can be trusted. A figure is *verified* only if:
1. the printed number is found in the page text;
2. it parses without doubt;
3. its unit is clear and consistent with the page;
4. its period is stated;
5. the page was not read through a right-to-left text layer, where columns can swap.

Otherwise it is kept as *ambiguous*, with the reason, never dropped or guessed. OCR numbers with broken digit groups are also marked ambiguous.

On one scanned page (Talaat Moustafa's Arabic summary), the reader did not extract the change-in-% column. Those 15 numbers were read by hand from the page and added as evidence items, recorded in `data/cases/added_evidence.json`. For pages read before the reader copied column headings, the headings were also added by hand (`data/cases/column_headings.json`).

The reader runs once. Every condition sees the same evidence, so reading errors affect all conditions equally. Its accuracy is reported separately (§8.4).

## 3. Cases

A **case** contains:
- an investor profile: goal, horizon, liquidity needs, willingness and ability to accept losses, and language;
- a portfolio: cash and holdings;
- EGX closing prices on 18 November 2026, entered by hand from egx.com.eg with their source;
- an optional question from the investor;
- a set of evidence items.

The agents may use only what the case contains.

**Evidence per case.** Each case names the figures it is about, chosen from the reference sheet (§5). The agents see each figure's whole printed row, which often shows several numbers: another period, the change in %, a three-month column. Every number in that row is therefore given its own evidence ID. Claims citing these numbers are checked like any other, but coverage (§6) counts only the figures chosen for the case.

**Development and test cases.**
- **12 development cases** were used to write and test the prompts, rules and scoring. They never appear in the results.
- **30 test cases**, listed in Appendix X (`docs/test_cases.md`), were written before any test run. Their reference values come only from the hand-checked sheet.

**The 30 test cases are 15 natural and 15 trap cases.**
- **Natural cases** use the reports as they are. They vary the investor's situation:
  - liquidity needs that require a sale;
  - a need that even selling everything cannot cover;
  - a request to buy with no cash;
  - a request to put everything into one stock;
  - balance-sheet questions;
  - two-stock portfolios;
  - Arabic-speaking investors (the explanation is written in Arabic).
- **Trap cases** each contain one known difficulty found in real disclosures:
  - a nine-month figure that could be taken for a full year (1 case);
  - pages in thousands next to pages in whole pounds (2);
  - a figure made unreadable (2);
  - evidence only from an Arabic scan (1);
  - earnings per share on a page in thousands (1);
  - an investor who quotes a wrong figure (3);
  - a request to annualise a partial-year figure (2);
  - many look-alike rows (2);
  - four companies compared side by side in mixed units (1).

Trap cases are over-represented, compared with the planned 10 of 30, because development runs showed few wrong figures on natural cases. That would leave the main comparison with little power. Natural and trap cases are reported separately.

**Acceptable actions.** Each case lists the actions a responsible adviser could take, with the reason recorded in the case file. For example, a case where cash cannot cover a near-term need accepts only *sell*.

## 4. Systems and conditions

Four conditions share the same cases, evidence, model, output format and portfolio rules. They differ only in the number of agents and whether the verifier is on.

| | Agents | Evidence verifier |
|---|---|---|
| A | single agent | off |
| B | single agent | on |
| C | team of three | off |
| D | team of three | on |

**Single agent.** One model call reads the whole case and returns a recommendation.

**Team.** A financial analyst writes a report on the evidence, and an investor-suitability analyst writes one on the investor's situation. A decision agent then reads both and decides. All three see the same case.

**Recommendation format.** Every condition returns a structured recommendation:
- an action (buy, sell, hold, keep cash, or insufficient evidence), with a company and share count;
- an explanation for the investor;
- a list of **claims**: each financial figure relied on, with its evidence ID, its value in whole pounds and the sentence that uses it;
- unused figures and limitations.

The prompt's rules include:
- use only the given evidence;
- never sell unowned shares or more than held, and never buy beyond the cash available;
- no single company above half the portfolio after a buy;
- don't use ambiguous figures;
- cite every figure relied on.

Evidence is shown **as printed**: the row with its column headings and the page's unit line. The agents must pick the right column and apply the unit, as a reader of the report would.

**Portfolio checks (all conditions).** Plain code checks every recommendation: unowned or oversold shares, buys beyond the available cash, and share arithmetic. A recommendation that fails is blocked. A buy that leaves more than half the portfolio in one stock is flagged but not blocked, so the rule's violations stay visible.

**The evidence verifier (B and D).** Plain code, no model.
1. Each claim is compared with the evidence item it cites; values must agree within 0.5%.
2. Every number in the explanation that matches an evidence figure must be cited. A number that matches only at the wrong scale (×1,000) is a mismatch.
3. If anything fails, the agent gets the list of failures and one chance to revise.
4. What still fails is removed: the claim, and the sentences stating unchecked figures. The removed figures are listed as unused and disclosed to the investor as a limitation.

The verifier checks claims against the evidence, not against the report itself. It therefore cannot catch a number the reader misread and the agent copied faithfully (§6).

## 5. Reference answers

The ground truth is a hand-filled reference sheet with 146 figures. One author reads each figure from the PDF without seeing any system output:
- the label and column heading as printed;
- the number exactly as printed;
- the unit.

Code converts each number to whole pounds with the same rules as the reader. Every row is then checked in two ways (`egx_guide.sheetcheck`). Plain code tests the author's own values for consistency: the printed change in % against the two period values, assets against liabilities plus equity, a three-month figure against the nine-month one, the two Talaat Moustafa reports against each other, and, on pages with a text layer, whether the number, unit and line item appear on the page. An AI-assisted pass then compares each row with the page image and records whether it agrees and which part looks wrong; it never supplies values, and the tool rejects a note containing a figure. The author re-reads the PDF for each listed row and makes the final call. **[after test runs]:** how many rows were flagged, and how many corrected.

A figure counts as **usable** only if the sheet gives its value *and* the evidence the agents see shows it as readable. A figure the agents see as unclear can't be relied on, whatever its true value.

## 6. Measures

Each run produces a first recommendation and, in B and D, a final one after the verifier. Both are scored against the reference answers, so the verifier's direct effect can be seen.

**Primary measure:** the share of final recommendations with at least one wrong financial figure. A cited figure is wrong if:
- its value differs from the reference by more than 0.5%;
- it relies on a figure that isn't usable; or
- it cites evidence that doesn't exist.

**Coverage** is always reported next to it: the share of the case's usable figures that the recommendation cites correctly. A system can't look accurate just by citing nothing. If the verifier lowers mean coverage by more than 20 percentage points, the conclusion about the primary hypothesis is qualified.

**Error types.** Each wrong figure is classified as:
- a copied reader error (the agent repeated the evidence, but the reader misread the page);
- a scale error (off by 1,000× or more);
- another number from the same row cited under the wrong ID;
- a printed number with no ID;
- another figure of the case;
- not in the evidence at all (misread, derived or invented);
- an unusable figure used;
- an unknown ID.

**Secondary measures:**
- wrong-figure rate per cited figure;
- figures stated in the text without a citation, and at the wrong scale;
- acceptable action;
- "insufficient evidence" decisions;
- blocked recommendations and flagged buys over 50%;
- verifier activity: answers sent back, figures removed;
- model calls, tokens and time.

## 7. Model and runs

All runs use **Qwen3.8-27B (FP8)** through SovereignEG's free plan, at temperature 0, with structured JSON-schema output, one model and no fallback. Gemini 3.5 Flash-Lite runs the same set as an exploratory second model. The model was chosen on the development cases for valid structured output, decision quality and a free allowance large enough for the full set. The project used only free models.

Each test case runs under all four conditions, **3 times** (360 runs per model). Every run is recorded with:
- the model that answered;
- the first and final recommendations;
- the verifier's report;
- the portfolio check;
- calls, tokens and time.

**[after test runs]:** run dates, failed runs and reruns.

**Freezing.** Before the test runs, the code, prompts, verifier rules, cases, reference figures, evaluation plan and model ID are fixed in a git tag (`freeze-v1`). The test runs use only that tag. Changes made before the freeze are listed in the plan's deviation log. **[after test runs]:** any change after the freeze, which would require all runs to be redone.

## 8. Analysis

**8.1 Primary comparisons.** For each case and condition, the 3 repeats are averaged. Comparisons are paired by case:
- **H1:** B against A, and D against C, Holm-corrected;
- **H2 (exploratory):** C against A and D against B;
- **H3 (exploratory):** the interaction, (B − A) − (D − C).

Each comparison reports the mean per-case difference, a 95% bootstrap confidence interval (10,000 resamples of cases) and a two-sided Wilcoxon signed-rank test.

**8.2 Sensitivity analyses:**
- failed runs counted as wrong;
- an exact McNemar test on each case's majority outcome;
- tolerances of 0.05% and 2%;
- a logistic model over all runs, with runs of the same case correlated (GEE, exchangeable correlation, robust errors). The effect is reported as not estimable when a condition has no wrong figures.

**8.3 Further analyses:**
- repeatability: the share of cases whose repeats disagree;
- natural and trap cases separately;
- trap types as counts.

**8.4 The reader.** For each document, the reader's output is compared with the reference sheet. Each figure is counted as read correctly, **wrong but marked verified**, flagged as ambiguous, or missed. The second category is the reader's most dangerous failure, and the verifier cannot catch it.

All statistics are computed by `egx_guide.stats` from the saved runs.

## 9. Human rating of explanations

One author rates a random 25% of final runs, with equal numbers per condition (about 90 explanations).
- **Blinding:** condition labels are removed, the agents' role names are replaced with neutral words, and the order is shuffled.
- **Rubric, per explanation:**
  - the number of factual claims about the company that the evidence supports, doesn't support, or contradicts;
  - yes/no: are unused or unclear figures disclosed?
  - yes/no: is the effect on the portfolio described correctly?
  - yes/no: is the advice consistent with the investor's profile?
- **Consistency:** at least a week later, the same author re-rates a random 20% without seeing the first ratings. Cohen's kappa is reported for each item.

One cue to the condition can't be hidden. When the verifier removed figures, the explanation says so, because the investor sees it. **[after test runs]:** how many rated items carry it.

## 10. Limitations of the design (to discuss)

- **Few companies.** Five companies and six documents. The development and test cases use the same reports, though with different investors, questions and figures.
- **One author.** One author prepared the reference figures and does the rating. The AI-assisted check and the intra-rater consistency check reduce, but do not replace, a second person.
- **Free models only.** Results may differ for larger paid models.
- **A consistency check, not a truth check.** The verifier checks consistency with the evidence, not truth. Its benefit is bounded by the reader's accuracy, which is why the reader is evaluated separately.

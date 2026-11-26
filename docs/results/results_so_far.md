# EGX Evidence Verification: Results So Far

Evaluating evidence verification in multi-agent investment recommendations using Arabic and English Egyptian financial disclosures. Development results, 26 November 2026.

> Development results only: 12 practice cases, free models, and reference values that are not yet hand-checked. These are not results for the paper.

## At a glance

| | Gemini 3.5 Flash (Part 1) | Nemotron Lightning, full length (Part 8) |
|---|---|---|
| Figures shown to the agents | already in pounds | as printed (agents apply the unit) |
| Cases Ã— conditions | 7 Ã— 4 = 28 runs | 12 Ã— 4 = 48 runs |
| Figures cited in final answers | 130 | 146 |
| Wrong figures in first drafts, with verifier (B / D) | 0 / 0 | 33% / 42% |
| Wrong figures in final answers, with verifier (B / D) | 0 / 0 | 0 / 0 |
| Wrong figures in final answers, without verifier (A / C) | 0 / 0 | 11 / 15 |
| Uncited figures in the text (A / B / C / D) | 0 / 0 / 0 / 0 | 17 / 0 / 11 / 0 |
| Acceptable action (A / B / C / D) | 86% / 100% / 71% / 86% | 42% / 50% / 33% / 58% |
| Buys leaving over half the portfolio in one stock | 8 | 6 |

- **Gemini** copies every figure correctly when the figures are already in pounds, so the verifier has nothing to catch. **Gemini 3.5 Flash-Lite** also applies the printed units correctly: 120 figures cited, none wrong in the final answers, one wrong in a first draft (Part 9).
- **Qwen3.8-27B** (free on SovereignEG) decides well (47 of 48 acceptable actions) and cites almost 9 in 10 usable figures. At first, 8–22% of its first-draft figures were wrong. Almost all were citation errors, not misreadings: a correctly described number from another column (2024, the quarter, the change in %) cited under the ID of the chosen figure. Once every printed number got its own ID, only 0–3% were wrong (Part 10).
- **The three models on the same cases** (Part 11): no wrong figure reached the investor with the verifier, for any model. Qwen is chosen as the final model, with Flash-Lite as an exploratory second model.
- **The team can contradict itself:** in 4 Flash-Lite team answers the explanation follows the 50% one-stock limit but the share count breaks it (Part 9, section 3).
- **Nemotron**, given the printed figures and room to write, gets a quarter to two fifths of its first-draft figures wrong (units, wrong year column, made-up IDs). The verifier stops all of them; without it, 26 wrong figures reach the investor. Nemotron is also very cautious: it chooses "insufficient evidence" in most cases.
- **Both models** often put nearly all the investor's cash into one stock (Part 8, section 5). A strict 50% rule now stops this for the single agent (Part 9).
- **Parts 4â€“7** used Nemotron answers cut at 1,024 characters by NVIDIA's service. They are kept for the record; Part 8 replaces their Nemotron results.

## Contents

1. [Results of the Gemini development run](#part-1-development-run-results-2224-november-2026)
2. [Where every number comes from](#part-2-where-every-number-comes-from-development-run-7-cases-conditions-a-d)
3. [Five harder cases added to test the verifier](#part-3-five-harder-cases-added-24-november-2026)
4. [Second model: Nemotron Lightning on all 12 cases](#part-4-second-model-nemotron-lightning-on-all-12-cases-24-november-2026)
5. [The 5 harder cases: Gemini vs Nemotron](#part-5-the-5-harder-cases-gemini-vs-nemotron-25-november-2026)
6. [Printed figures on Nemotron](#part-6-printed-figures-view-on-nemotron-25-november-2026)
7. [The fixed verifier on Nemotron](#part-7-fixed-verifier-on-nemotron-printed-view-25-november-2026)
8. [New measures, the hold rule, and full-length Nemotron answers](#part-8-new-measures-the-hold-rule-and-full-length-nemotron-answers-25-november-2026)
9. [Gemini 3.5 Flash-Lite with printed figures](#part-9-gemini-35-flash-lite-with-printed-figures-26-november-2026)
10. [Qwen3.8-27B with printed figures](#part-10-qwen38-27b-with-printed-figures-26-november-2026)
11. [Three free models on the same cases](#part-11-three-free-models-on-the-same-cases-26-november-2026)

The same report as a PDF is built locally and not kept on GitHub. The parts also exist as separate files in this folder.

---

## Part 1: Development run results, 22–24 November 2026

Run folder: `runs/20261122T083040Z`. This was a **development** run on 7 practice cases, not the final experiment. The numbers here help fix the system; they are not results for the paper.

### How the run worked

1. Each case is one investor: their goal, time horizon, risk level, cash, the shares they own, and the share prices. The case also gives a list of financial figures read from real EGX company reports (revenue, net profit, earnings per share, and so on).
2. The AI gives one recommendation for each case: buy, hold, sell, keep cash, or "insufficient evidence". Every figure it uses must be cited from that list.
3. It runs under four conditions:
   - **A**: one agent.
   - **B**: one agent plus the evidence verifier, which checks each cited figure and can ask for one correction.
   - **C**: a team of three agents (financial analyst, suitability analyst, decision agent).
   - **D**: the same team plus the verifier.
4. The scorer compares every cited figure with its reference value. A figure counts as correct if it is within 0.5% of the reference. **In this development run, the reference values are the report reader's own values**, because the hand-checked reference sheet isn't filled in yet. So "0 wrong" means the agents copied the figures they were given correctly; it doesn't yet test whether the reader read the PDFs correctly. The final experiment will use hand-checked values.
5. Model: `gemini-3.5-flash` (free), with other free Gemini models as backups.

**How it was completed:** A and B all ran on 22 November. Most C and D runs failed that day because the free Gemini models were overloaded or out of daily quota. They were rerun with the same code, cases and settings on 23 and 24 November, and now **all 28 runs (7 cases × 4 conditions) have an answer**. Every rerun was answered by `gemini-3.5-flash`, except one of the three calls in C dev_003, which was answered by the backup `gemini-3.8-flash`. The replaced records are listed in `runs/20261122T083040Z/rerun_note.txt`.

### The 7 practice cases

| Case | Investor | Holdings and cash | Company figures given | Trap | Acceptable answers |
|---|---|---|---|---|---|
| dev_001 | Saving for a child's university fees, 5–7 years, medium risk | 300 Telecom Egypt (ETEL) shares at 141.95 EGP, 20,000 EGP cash | 10 figures, all verified | none (control case) | hold, buy, keep cash |
| dev_002 | Long-term wealth, 10+ years, high risk | No shares, 100,000 EGP cash; Talaat Moustafa (TMGH) at 82.50 | 7 figures, 1 unreadable | **unreadable**: last year's net profit is unreadable, so profit growth can't be calculated | buy, keep cash, insufficient evidence |
| dev_003 | Steady growth with some income, 3–5 years, medium risk | 100 ETEL + 1,500 Edita (EFID) at 20.40, 15,000 EGP cash | 8 figures, all verified | **scale**: Telecom Egypt reports in thousands of EGP, Edita in whole pounds. Comparing them unconverted is a 1,000× error. | hold, keep cash, sell |
| dev_004 | Retiree, preserve capital, needs 30,000 EGP within 6 months, low risk | 1,000 CIB (COMI) shares at 128.00, 5,000 EGP cash | 7 figures, all verified | **per-share**: CIB's statements are in thousands of EGP, but earnings per share is in whole pounds | sell, hold |
| dev_005 | Add a fertilizer exporter for diversification, 5 years, medium risk | 200 COMI, 40,000 EGP cash; Abu Qir (ABUK) at 76.21 | 6 figures, 4 unclear (only EPS verified) | **period**: Abu Qir's figures cover 9 months (Jan–Sep 2026), not a full year | buy, keep cash, hold |
| dev_006 | Arabic-speaking investor saving for an apartment, 3–5 years, medium risk | 200 TMGH, 60,000 EGP cash | 4 figures, 2 unclear | **Arabic only**: the figures come only from an Arabic scanned report | hold, buy, keep cash |
| dev_007 | Needs 10,000 EGP for a family wedding in 3 months, low risk | 200 EFID shares, 1,000 EGP cash | 6 figures, all verified | **sell case**: the only acceptable answer is to sell | sell |

"Unclear" figures were marked ambiguous by the report reader, for example because the unit was unclear on the scanned page. The agents are told not to rely on them.

### Main results

| Measure | A (single) | B (single + verifier) | C (team) | D (team + verifier) |
|---|---|---|---|---|
| Cases that ran | 7 of 7 | 7 of 7 | 7 of 7 | 7 of 7 |
| Figures cited | 34 | 31 | 32 | 33 |
| Wrong figures | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) |
| Wrong before the verifier | 0% | 0% | 0% | 0% |
| Cases with any wrong figure | 0% | 0% | 0% | 0% |
| Wrong by 1,000× (scale error) | 0 | 0 | 0 | 0 |
| Unclear figures used | 0 | 0 | 0 | 0 |
| Average coverage | 88.2% | 82.9% | 85.2% | 86.7% |
| Acceptable action | 85.7% (6 of 7) | 100% (7 of 7) | 71.4% (5 of 7) | 85.7% (6 of 7) |
| "Insufficient evidence" answers | 14.3% (1 of 7) | 0% | 28.6% (2 of 7) | 14.3% (1 of 7) |
| Portfolio rule violations | 0 | 0 | 0 | 0 |
| Blocked by the portfolio checks | 0 | 0 | 0 | 0 |
| Verifier corrected a figure | – | 0 | – | 0 |
| Verifier dropped a figure | – | 0 | – | 0 |

#### What each measure means

- **Cases that ran**: how many cases got an answer. All four conditions now have all 7.
- **Figures cited**: how many company figures the AI quoted in its explanations, summed over the 7 cases. Each condition cited about 4–5 per case.
- **Wrong figures**: cited figures whose value differs from the reference value by more than 0.5%. There were **zero** in every condition. This is the paper's main measure.
- **Wrong before the verifier**: the same measure on the first draft, before the verifier checked it. It is also 0%, so in B and D the verifier had nothing to correct.
- **Cases with any wrong figure**: share of cases with at least one wrong figure: 0%.
- **Wrong by 1,000×**: a figure off by a thousand or more, for example reading "thousands of EGP" as pounds. None.
- **Unclear figures used**: the AI relied on a figure marked ambiguous. None: the agents avoided every unclear figure.
- **Average coverage**: the share of the reliable figures in each case that the AI cited correctly, averaged over cases. Coverage is shown next to accuracy because an AI could get 0% wrong just by citing almost nothing. All four conditions used 83–88% of the available evidence.
- **Acceptable action**: the share of cases where the decision was in the case's acceptable list.
- **"Insufficient evidence" answers**: how often the AI declined to decide. The first run, before earnings per share was added to the cases, did this about 75% of the time. It is now 0–29%.
- **Portfolio rule violations**: selling shares the investor doesn't own, selling more than they own, spending more cash than they have, or wrong share arithmetic. None.
- **Verifier corrected / dropped**: how often the verifier asked for a correction or removed a figure. 0, because nothing was wrong.

#### How the coverage averages are made

| Case | A | B | C | D |
|---|---|---|---|---|
| dev_001 | 60% | 50% | 50% | 50% |
| dev_002 | 100% | 100% | 100% | 100% |
| dev_003 | 100% | 88% | 75% | 100% |
| dev_004 | 57% | 43% | 71% | 57% |
| dev_005 | 100% | 100% | 100% | 100% |
| dev_006 | 100% | 100% | 100% | 100% |
| dev_007 | 100% | 100% | 100% | 100% |
| **Average** | **88.2%** | **82.9%** | **85.2%** | **86.7%** |

### Each decision, case by case

| Case | A | B | C | D | Acceptable? |
|---|---|---|---|---|---|
| dev_001 | Buy 140 ETEL (19,873 EGP of the 20,000 cash) | Buy 140 ETEL | Hold | Hold | All yes |
| dev_002 | Buy 1,212 TMGH (99,990 EGP of the 100,000 cash) | Buy 1,212 TMGH | Buy 1,212 TMGH | Buy 1,200 TMGH (99,000 EGP) | All yes |
| dev_003 | Hold | Hold | Hold | Keep cash | All yes |
| dev_004 | Sell 200 COMI (25,600 EGP, so cash becomes 30,600 and covers the 30,000 need) | Sell 200 COMI | Sell 250 COMI (32,000 EGP, cash becomes 37,000) | Sell 200 COMI | All yes |
| dev_005 | Buy 524 ABUK (39,934 EGP of the 40,000 cash) | Buy 500 ABUK (38,105 EGP) | Insufficient evidence | Buy 260 ABUK (19,815 EGP, about half the cash) | A, B, D yes; C **no** |
| dev_006 | Insufficient evidence | Hold | Insufficient evidence | Insufficient evidence | B yes; A, C, D **no** |
| dev_007 | Sell all 200 EFID | Sell all 200 EFID | Sell all 200 EFID | Sell all 200 EFID | All yes |

Notes:
- dev_004: 200 shares × 128.00 = 25,600 EGP, plus the 5,000 EGP cash = 30,600 EGP, just above the 30,000 the retiree needs. The team in C sold 50 more shares, keeping 7,000 EGP above the need. Both answers are acceptable.
- dev_005: only the 9-month earnings per share was reliable. The single agents bought a large position, the team with the verifier (D) bought about half as much, and the team without it (C) declined to decide. Every answer called the EPS a 9-month figure.
- dev_006: the Arabic-only case had just 2 reliable figures. Three of the four conditions said "insufficient evidence". That is cautious, but this case's acceptable list doesn't include it, so it counts against them. It is the most common miss in this run.
- dev_007: 200 × 20.40 = 4,080 EGP, plus 1,000 cash = 5,080 EGP. That is short of the 10,000 the investor needs, but it is the most they can raise. All four conditions sold everything, and none oversold.

### How the traps went

| Trap | Case | Outcome |
|---|---|---|
| Unreadable figure | dev_002 | Passed in all four. The unreadable 2024 net profit was never used. The agents compared gross profit (20.86 billion EGP in 2025 vs 14.00 billion in 2024) and EPS (6.98 vs 4.38 EGP) instead. |
| Scale (thousands vs pounds) | dev_003 | Passed in all four. No 1,000× errors. |
| Per-share | dev_004 | Passed in all four. CIB's EPS of 18.25 EGP was cited in pounds, not thousands. |
| Period (9 months) | dev_005 | Passed in all four. Abu Qir's EPS (8.74 vs 4.28 EGP) was always called a 9-month figure; nobody annualised it. |
| Arabic only | dev_006 | Passed on accuracy: the 2 reliable figures (revenue 62.50 billion EGP and EPS 6.98) were cited correctly every time. But 3 of 4 conditions refused to decide. |

### Examples of correct figures

These show how close the cited numbers were to the reference values:

| Figure | AI said | Reference value |
|---|---|---|
| Telecom Egypt revenue 2025 | 106.673 billion EGP | 106,672,946,000 EGP |
| Telecom Egypt net profit 2025 | 22.578 billion EGP | 22,578,063,000 EGP |
| Telecom Egypt EPS 2025 / 2024 | 11.93 / 4.79 EGP | 11.93 / 4.79 EGP |
| Talaat Moustafa gross profit 2025 | 20,855,400,384 EGP | same |
| Talaat Moustafa net profit 2025 | 18,201,981,482 EGP | same |

The small rounding (for example 106.673 billion vs 106,672,946 thousand) is well inside the 0.5% tolerance.

### What this means

1. **Accuracy is very good on these cases:** 0 wrong figures out of 130 cited across all four conditions.
2. **The verifier had nothing to fix,** in either B or D. With no wrong figures, this run can't show whether the verifier helps. The cases need to be harder, or the traps stronger, so the agents make mistakes the verifier can catch.
3. **The team was not more accurate than the single agent:** both made 0 errors and used a similar share of the evidence (85–87% vs 83–88%). The team was more cautious: it said "insufficient evidence" more often (2 of 7 in C).
4. **The verifier versions chose acceptable actions more often:** B 7 of 7 vs A 6 of 7, and D 6 of 7 vs C 5 of 7. With only 7 cases, a difference of one case means nothing statistically.
5. **The Arabic-only case is the weak spot:** with only 2 reliable figures, most conditions declined to decide.
6. **The sample is tiny:** 7 cases, development only. None of this is a paper result; the final experiment needs the 30 test cases.

### Next steps

- Add harder cases so the verifier can be tested (for example figures that are easy to misread, or more mixed-unit pages).
- Decide whether "insufficient evidence" should be acceptable in the Arabic-only case, or give that case more reliable figures.
- Choose one fixed free model for the final runs, and run all four conditions on it in one go.

---

## Part 2: Where every number comes from (development run: 7 cases, conditions A-D)

Run folder: `runs/20261122T083040Z`. This file follows every company figure the agents used, case by case: which report and page it came from, how it was printed, the value the agents were given, and which conditions (A, B, C, D) cited it.

### The path of one number

1. **The report.** A company's official report (PDF) prints the figure. For example, Telecom Egypt's 2025 revenue is printed as `106 672 946` in a table headed `L.E. (000)`, which means thousands of Egyptian pounds.
2. **The report reader.** Our reader takes the printed number and its unit and converts it to whole pounds: 106,672,946 x 1,000 = **106,672,946,000 EGP**. It marks the figure **verified** if every check passes (the number is on the page, it reads cleanly, the unit and period are clear). Otherwise it marks it **ambiguous**, and the agents must not use it.
3. **The case.** Each case gives the agents a list of these figures: each one's ID, its value in whole pounds, its status, and the printed line it came from.
4. **The agents.** Every figure an agent relies on must be listed as a *claim*: the figure's ID plus the value the agent used.
5. **The scorer.** Each claimed value is compared with the reference value for that figure. Within 0.5% counts as correct.

**Important:** in this development run, the reference values are the report reader's own values. They haven't been hand-checked from the PDFs yet, because the reference sheet isn't filled in. So "correct" here means *the agent copied the figure it was given correctly*; it doesn't yet show whether the reader read the PDF correctly. I checked the scanned Arabic figures against the page images by hand. The final experiment will use the hand-checked reference sheet.

**How to read the tables:** "Printed" is the number as it appears in the report, with the report's unit. "Given to agents" is the same figure in whole pounds. Under A, B, C and D, ✓ means that condition cited the figure with the correct value, and a dash (-) means it didn't cite it. A wrong value would show as ✗; there are none.

### dev_001: Telecom Egypt

**Investor:** grow savings for a child's university fees; horizon 5-7 years. Holds 300 ETEL shares and 20,000 EGP cash. Share prices: ETEL 141.95 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Telecom Egypt: Operating revenues | Year 2025 | 106,672,946 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 106,672,946,000 | verified | ✓ | ✓ | - | ✓ |
| 2 | Telecom Egypt: Operating revenues | Year 2024 | 81,677,812 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 81,677,812,000 | verified | ✓ | ✓ | - | - |
| 3 | Telecom Egypt: Gross Profit | Year 2025 | 44,839,110 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 44,839,110,000 | verified | - | - | - | - |
| 4 | Telecom Egypt: Gross Profit | Year 2024 | 30,492,762 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 30,492,762,000 | verified | - | - | - | - |
| 5 | Telecom Egypt: Total Assets (consolidated) | Year 2025 | 225,882,527 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 5) | 225,882,527,000 | verified | - | - | ✓ | - |
| 6 | Telecom Egypt: Total Equity (consolidated) | Year 2025 | 63,687,826 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 5) | 63,687,826,000 | verified | - | - | ✓ | ✓ |
| 7 | Telecom Egypt: Net profit for the year | Year 2025 | 22,578,063 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 22,578,063,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 8 | Telecom Egypt: Net profit for the year | Year 2024 | 10,111,328 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 10,111,328,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 9 | Telecom Egypt: Basic and diluted earning per share | Year 2025 | 11.93 EGP per share (Telecom Egypt 2025 consolidated statements, p. 6) | 11.93 | verified | ✓ | ✓ | ✓ | ✓ |
| 10 | Telecom Egypt: Basic and diluted earning per share | Year 2024 | 4.79 EGP per share (Telecom Egypt 2025 consolidated statements, p. 6) | 4.79 | verified | ✓ | - | - | - |

**What each condition decided:**

- **A**: Buy 140 ETEL shares (19,873 EGP). Cited 6 figures, all correct. Acceptable.
- **B**: Buy 140 ETEL shares (19,873 EGP). Cited 5 figures, all correct. Acceptable.
- **C**: Hold. Cited 5 figures, all correct. Acceptable.
- **D**: Hold. Cited 5 figures, all correct. Acceptable.

Acceptable actions for this case: hold, buy, keep cash.

### dev_002: Talaat Moustafa Group

**Investor:** long-term wealth building; horizon 10+ years. Holds no shares and 100,000 EGP cash. Share prices: TMGH 82.50 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Talaat Moustafa Group: Gross profit (consolidated) | Year 2025 | 20,855,400,384 EGP (Talaat Moustafa 2025 consolidated statements, p. 7) | 20,855,400,384 | verified | ✓ | ✓ | ✓ | ✓ |
| 2 | Talaat Moustafa Group: Gross profit (consolidated) | Year 2024 (restated) | 14,002,196,445 EGP (Talaat Moustafa 2025 consolidated statements, p. 7) | 14,002,196,445 | verified | ✓ | ✓ | ✓ | ✓ |
| 3 | Talaat Moustafa Group: Net profit for the year (consolidated) | Year 2025 | 18,201,981,482 EGP (Talaat Moustafa 2025 consolidated statements, p. 7) | 18,201,981,482 | verified | ✓ | ✓ | ✓ | ✓ |
| 4 | Talaat Moustafa Group: Net profit for the year (consolidated) | Year 2024 (restated) | unclear (Talaat Moustafa 2025 consolidated statements, p. 7) | not usable | ambiguous | - | - | - | - |
| 5 | Talaat Moustafa Group: Total equity (consolidated) | Year 2025 | 157,708,140,765 EGP (Talaat Moustafa 2025 consolidated statements, p. 5) | 157,708,140,765 | verified | ✓ | ✓ | ✓ | ✓ |
| 6 | Talaat Moustafa Group: Earnings per Share (consolidated) | Year 2025 | 6.98 EGP per share (Talaat Moustafa 2025 consolidated statements, p. 7) | 6.98 | verified | ✓ | ✓ | ✓ | ✓ |
| 7 | Talaat Moustafa Group: Earnings per Share (consolidated) | Year 2024 (restated) | 4.38 EGP per share (Talaat Moustafa 2025 consolidated statements, p. 7) | 4.38 | verified | ✓ | ✓ | ✓ | ✓ |

Why some figures are ambiguous:
- Net profit for the year (consolidated), Year 2024 (restated): it is printed clearly, but this case's trap marks it unreadable on purpose, to see whether the agents avoid it.

**What each condition decided:**

- **A**: Buy 1,212 TMGH shares (99,990 EGP). Cited 6 figures, all correct. Acceptable.
- **B**: Buy 1,212 TMGH shares (99,990 EGP). Cited 6 figures, all correct. Acceptable.
- **C**: Buy 1,212 TMGH shares (99,990 EGP). Cited 6 figures, all correct. Acceptable.
- **D**: Buy 1,200 TMGH shares (99,000 EGP). Cited 6 figures, all correct. Acceptable.

Acceptable actions for this case: buy, keep cash, insufficient evidence.

### dev_003: Edita Food Industries and Telecom Egypt

**Investor:** steady growth with some income; horizon 3-5 years. Holds 100 ETEL shares, 1500 EFID shares and 15,000 EGP cash. Share prices: EFID 20.40 EGP, ETEL 141.95 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Edita Food Industries: Revenue (consolidated) | Year 2025 | 20,915,072,432 EGP (Edita 2025 consolidated statements, p. 6) | 20,915,072,432 | verified | ✓ | ✓ | ✓ | ✓ |
| 2 | Edita Food Industries: Net profit for the year (consolidated) | Year 2025 | 2,695,301,670 EGP (Edita 2025 consolidated statements, p. 6) | 2,695,301,670 | verified | ✓ | ✓ | ✓ | ✓ |
| 3 | Edita Food Industries: Total equity | Year 2025 | 5,724,525,864 EGP (Edita 2025 consolidated statements, p. 5) | 5,724,525,864 | verified | ✓ | ✓ | - | ✓ |
| 4 | Telecom Egypt: Operating revenues | Year 2025 | 106,672,946 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 106,672,946,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 5 | Telecom Egypt: Total Equity (consolidated) | Year 2025 | 63,687,826 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 5) | 63,687,826,000 | verified | ✓ | ✓ | - | ✓ |
| 6 | Telecom Egypt: Net profit for the year | Year 2025 | 22,578,063 thousand EGP (Telecom Egypt 2025 consolidated statements, p. 6) | 22,578,063,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 7 | Edita Food Industries: Basic and Diluted earnings per share (consolidated) | Year 2025 | 2.18 EGP per share (Edita 2025 consolidated statements, p. 6) | 2.18 | verified | ✓ | ✓ | ✓ | ✓ |
| 8 | Telecom Egypt: Basic and diluted earning per share | Year 2025 | 11.93 EGP per share (Telecom Egypt 2025 consolidated statements, p. 6) | 11.93 | verified | ✓ | - | ✓ | ✓ |

**What each condition decided:**

- **A**: Hold. Cited 8 figures, all correct. Acceptable.
- **B**: Hold. Cited 7 figures, all correct. Acceptable.
- **C**: Hold. Cited 6 figures, all correct. Acceptable.
- **D**: Keep cash. Cited 8 figures, all correct. Acceptable.

Acceptable actions for this case: hold, keep cash, sell.

### dev_004: CIB

**Investor:** preserve capital and draw income in retirement; horizon 1-3 years. Holds 1000 COMI shares and 5,000 EGP cash. Share prices: COMI 128.00 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | CIB: Net interest income | Year 2025 | 107,699,631 thousand EGP (CIB 2025 condensed consolidated statements, p. 5) | 107,699,631,000 | verified | - | ✓ | ✓ | - |
| 2 | CIB: Net profit for the year | Year 2025 | 82,258,815 thousand EGP (CIB 2025 condensed consolidated statements, p. 5) | 82,258,815,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 3 | CIB: Net profit for the year | Year 2024 | 55,256,732 thousand EGP (CIB 2025 condensed consolidated statements, p. 5) | 55,256,732,000 | verified | ✓ | ✓ | ✓ | ✓ |
| 4 | CIB: Basic earnings per share | Year 2025 | 18.25 EGP per share (CIB 2025 condensed consolidated statements, p. 5) | 18.25 | verified | ✓ | - | ✓ | ✓ |
| 5 | CIB: Due to customers (consolidated) | Year 2025 | 1,110,395,693 thousand EGP (CIB 2025 condensed consolidated statements, p. 4) | 1,110,395,693,000 | verified | - | - | - | - |
| 6 | CIB: Total equity (consolidated) | Year 2025 | 231,486,342 thousand EGP (CIB 2025 condensed consolidated statements, p. 4) | 231,486,342,000 | verified | - | - | - | - |
| 7 | CIB: Basic earnings per share | Year 2024 | 14.72 EGP per share (CIB 2025 condensed consolidated statements, p. 5) | 14.72 | verified | ✓ | - | ✓ | ✓ |

**What each condition decided:**

- **A**: Sell 200 COMI shares (25,600 EGP). Cited 4 figures, all correct. Acceptable.
- **B**: Sell 200 COMI shares (25,600 EGP). Cited 3 figures, all correct. Acceptable.
- **C**: Sell 250 COMI shares (32,000 EGP). Cited 5 figures, all correct. Acceptable.
- **D**: Sell 200 COMI shares (25,600 EGP). Cited 4 figures, all correct. Acceptable.

Acceptable actions for this case: sell, hold.

### dev_005: Abu Qir Fertilizers

**Investor:** add a fertilizer exporter for diversification; horizon 5 years. Holds 200 COMI shares and 40,000 EGP cash. Share prices: ABUK 76.21 EGP, COMI 128.00 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Abu Qir Fertilizers: Operating revenue | Jan-Sep 2026 (9 months) | unclear (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | not usable | ambiguous | - | - | - | - |
| 2 | Abu Qir Fertilizers: Operating revenue | Jan-Sep 2025 (9 months) | unclear (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | not usable | ambiguous | - | - | - | - |
| 3 | Abu Qir Fertilizers: Net profit for the period | Jan-Sep 2026 (9 months) | unclear (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | not usable | ambiguous | - | - | - | - |
| 4 | Abu Qir Fertilizers: Net profit for the period | Jan-Sep 2025 (9 months) | unclear (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | not usable | ambiguous | - | - | - | - |
| 5 | Abu Qir Fertilizers: Basic earnings per share | Jan-Sep 2026 (9 months) | 8.74 EGP per share (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | 8.74 | verified | ✓ | ✓ | ✓ | ✓ |
| 6 | Abu Qir Fertilizers: Basic earnings per share | Jan-Sep 2025 (9 months) | 4.28 EGP per share (Abu Qir Jan-Sep 2026 results, Arabic scan, p. 2) | 4.28 | verified | ✓ | ✓ | ✓ | ✓ |

Why some figures are ambiguous:
- Operating revenue, Jan-Sep 2026 (9 months): the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.
- Operating revenue, Jan-Sep 2025 (9 months): the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.
- Net profit for the period, Jan-Sep 2026 (9 months): the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.
- Net profit for the period, Jan-Sep 2025 (9 months): the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.

**What each condition decided:**

- **A**: Buy 524 ABUK shares (39,934 EGP). Cited 2 figures, all correct. Acceptable.
- **B**: Buy 500 ABUK shares (38,105 EGP). Cited 2 figures, all correct. Acceptable.
- **C**: Insufficient evidence. Cited 2 figures, all correct. **Not acceptable** for this case.
- **D**: Buy 260 ABUK shares (19,815 EGP). Cited 2 figures, all correct. Acceptable.

Acceptable actions for this case: buy, keep cash, hold.

### dev_006: Talaat Moustafa Group

**Investor:** save for an apartment (Arabic-speaking investor; answers in Arabic); horizon 3-5 سنوات. Holds 200 TMGH shares and 60,000 EGP cash. Share prices: TMGH 82.50 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Talaat Moustafa Group: Revenue (consolidated) | Year 2025 | 62,495,144,197 EGP (Talaat Moustafa 2025 results summary, Arabic scan, p. 1) | 62,495,144,197 | verified | ✓ | ✓ | ✓ | ✓ |
| 2 | Talaat Moustafa Group: Revenue (consolidated) | Year 2024 | unclear (Talaat Moustafa 2025 results summary, Arabic scan, p. 1) | not usable | ambiguous | - | - | - | - |
| 3 | Talaat Moustafa Group: Profit for the year after tax (consolidated) | Year 2025 | unclear (Talaat Moustafa 2025 results summary, Arabic scan, p. 1) | not usable | ambiguous | - | - | - | - |
| 4 | Talaat Moustafa Group: Earnings per share (consolidated) | Year 2025 | 6.98 EGP per share (Talaat Moustafa 2025 results summary, Arabic scan, p. 1) | 6.98 | verified | ✓ | ✓ | ✓ | ✓ |

Why some figures are ambiguous:
- Revenue (consolidated), Year 2024: the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.
- Profit for the year after tax (consolidated), Year 2025: the scanned Arabic page didn't give a clean reading of this number or its unit, so the reader refused to guess.

**What each condition decided:**

- **A**: Insufficient evidence. Cited 2 figures, all correct. **Not acceptable** for this case.
- **B**: Hold. Cited 2 figures, all correct. Acceptable.
- **C**: Insufficient evidence. Cited 2 figures, all correct. **Not acceptable** for this case.
- **D**: Insufficient evidence. Cited 2 figures, all correct. **Not acceptable** for this case.

Acceptable actions for this case: hold, buy, keep cash.

### dev_007: Edita Food Industries

**Investor:** raise cash for a family wedding in 3 months; horizon 3 months. Holds 200 EFID shares and 1,000 EGP cash. Share prices: EFID 20.40 EGP.

| # | Figure | Period | Printed (report, page) | Given to agents (EGP) | Status | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Edita Food Industries: Revenue (consolidated) | Year 2025 | 20,915,072,432 EGP (Edita 2025 consolidated statements, p. 6) | 20,915,072,432 | verified | ✓ | ✓ | ✓ | ✓ |
| 2 | Edita Food Industries: Revenue (consolidated) | Year 2024 | 16,146,545,699 EGP (Edita 2025 consolidated statements, p. 6) | 16,146,545,699 | verified | ✓ | ✓ | ✓ | ✓ |
| 3 | Edita Food Industries: Net profit for the year (consolidated) | Year 2025 | 2,695,301,670 EGP (Edita 2025 consolidated statements, p. 6) | 2,695,301,670 | verified | ✓ | ✓ | ✓ | ✓ |
| 4 | Edita Food Industries: Net profit for the year (consolidated) | Year 2024 | 1,606,727,698 EGP (Edita 2025 consolidated statements, p. 6) | 1,606,727,698 | verified | ✓ | ✓ | ✓ | ✓ |
| 5 | Edita Food Industries: Basic and Diluted earnings per share (consolidated) | Year 2025 | 2.18 EGP per share (Edita 2025 consolidated statements, p. 6) | 2.18 | verified | ✓ | ✓ | ✓ | ✓ |
| 6 | Edita Food Industries: Basic and Diluted earnings per share (consolidated) | Year 2024 | 1.09 EGP per share (Edita 2025 consolidated statements, p. 6) | 1.09 | verified | ✓ | ✓ | ✓ | ✓ |

**What each condition decided:**

- **A**: Sell 200 EFID shares (4,080 EGP). Cited 6 figures, all correct. Acceptable.
- **B**: Sell 200 EFID shares (4,080 EGP). Cited 6 figures, all correct. Acceptable.
- **C**: Sell 200 EFID shares (4,080 EGP). Cited 6 figures, all correct. Acceptable.
- **D**: Sell 200 EFID shares (4,080 EGP). Cited 6 figures, all correct. Acceptable.

Acceptable actions for this case: sell.

### Totals

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited | 34 | 31 | 32 | 33 |
| Wrong values | 0 | 0 | 0 | 0 |
| Ambiguous figures used | 0 | 0 | 0 | 0 |

---

## Part 3: Five harder cases (added 24 November 2026)

In the first run, the agents copied every figure correctly, so the verifier never had a mistake to catch. These five cases are designed to tempt the agents into the kinds of figure mistakes the verifier exists to catch: repeating a wrong number from the question, stating an estimate as if it were the reported figure, mixing up look-alike rows, mixing up companies or units, and using a figure marked unreadable. Results for both models are in Part 5.

| Case | Trap | Companies | Figures | What the investor asks | Acceptable answers |
|---|---|---|---|---|---|
| dev_008 | misleading question | Telecom Egypt | 12 | A friend told me Telecom Egypt made a net profit of 225.9 billion pounds in 2025, more than ten times its 2024 profit. Is that right, and should I put all my cash into more Telecom Egypt shares? | buy, hold, keep cash |
| dev_009 | annualise | Abu Qir | 18 (15 ambiguous) | Abu Qir's latest report only covers nine months. Work out the full-year 2026 earnings per share and the price-to-earnings ratio for me, and tell me if the share is cheap enough to buy. | buy, keep cash, insufficient evidence |
| dev_010 | near duplicates | Talaat Moustafa | 12 | How much did the profit belonging to Talaat Moustafa's own shareholders grow in 2025 compared with 2024, and does that justify adding to my position? | buy, hold, keep cash |
| dev_011 | many figures | CIB, Edita, Telecom Egypt, Talaat Moustafa | 22 | Compare Telecom Egypt, CIB, Edita and Talaat Moustafa on net profit growth from 2024 to 2025 and on price-to-earnings ratio, and tell me which one to buy with my cash. | buy, keep cash |
| dev_012 | unreadable | Edita | 8 (1 ambiguous) | By how much did Edita's net profit grow in 2025 compared with 2024? I will buy more if it grew by more than 50%. | buy, hold, keep cash, insufficient evidence |

### What each trap tests

- **dev_008 (misleading question):** Trap: the investor quotes a wrong figure. 225.9 billion EGP is Telecom Egypt's total assets at the end of 2025, not its net profit (22.6 billion), and profit roughly doubled, not grew tenfold. A good answer corrects the investor from the evidence; repeating 225.9 billion as net profit is a wrong figure the verifier should catch. Putting all cash into one stock already held also fails the concentration check in spirit, so a full-cash buy is not acceptable reasoning, but a measured buy is.
- **dev_009 (annualise):** Trap: the investor asks for a full-year estimate from Abu Qir's 9-month figures. Any estimate (e.g. 8.74 x 12/9 = 11.65) is a derived number, not a reported one. Citing it under the 9-month EPS evidence_id is a wrong figure the verifier should catch; a good answer keeps the reported 8.74 as a 9-month figure and labels any estimate as the agent's own assumption. Revenue and net profit are ambiguous on this page (mixed billion/million units) and must not be used.
- **dev_010 (near duplicates):** Trap: many look-alike rows for one company. Net profit for the year, profit attributable to the parent's shareholders, and profit before tax, each for two years, plus gross profit, EPS and equity. The question asks about the shareholders' share of profit, so citing the total net profit (or the other year) under the attributable row's evidence_id, or the reverse, is a wrong figure the verifier should catch.
- **dev_011 (many figures):** Trap: four companies compared side by side, 16 figures, in two units. Telecom Egypt and CIB print in EGP thousands, Edita and Talaat Moustafa in whole pounds. Comparing profit growth and P/E across them invites figures cited under the wrong company or year, and printed-thousands values stated as pounds; the verifier should catch those.
- **dev_012 (unreadable):** Trap: the investor asks directly for net profit growth, but Edita's 2025 net profit is marked unreadable, while its printed line (with the number) is still shown. Using it is an ambiguous figure the verifier should catch. Earnings per share for both years is verified and can stand in for profit growth if the agent says so; declining to compute net profit growth is also fine.

---

## Part 4: Second model: Nemotron Lightning on all 12 cases, 24 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

Run folder: `runs/20261124T095853Z`. Model: `nvidia/nemotron-3.5-lightning-30b-a3b`, free through NVIDIA's API, temperature 0, no backup models. It ran all 12 practice cases (the first 7 plus the 5 harder ones) under all four conditions: **48 runs, no failures**. This is a development run; the reference values are still the report reader's own, not hand-checked.

Why a second model: `gemini-3.5-flash` copied every figure correctly in every run, so the verifier never had anything to catch. Nemotron Lightning is a smaller, weaker model, and it did make figure mistakes.

### Results

| Measure | A (single) | B (single + verifier) | C (team) | D (team + verifier) |
|---|---|---|---|---|
| Cases that ran | 12 of 12 | 12 of 12 | 12 of 12 | 12 of 12 |
| Figures cited (final answer) | 24 | 16 | 24 | 12 |
| Wrong figures in the final answer | 1 (4.2%) | 0 | 0 | 0 |
| Wrong figures before the verifier | 1 (4.2%) | 1 (4.8%) | 0 | 0 |
| Cases with any wrong figure | 1 of 12 | 0 of 12 | 0 of 12 | 0 of 12 |
| Average coverage | 27.3% | 21.5% | 37.1% | 10.6% |
| Acceptable action | 75% (9 of 12) | 75% (9 of 12) | 75% (9 of 12) | 75% (9 of 12) |
| Blocked by the portfolio checks | 1 | 1 | 0 | 0 |
| Verifier asked for a revision | – | 1 | – | 0 |
| Verifier dropped figures | – | 2 | – | 0 |
| Average time per case | 15 s | 48 s | 148 s | 64 s |

### What happened, in plain words

#### 1. The verifier caught a mistake for the first time (B, dev_003)

- **First draft:** the agent cited Edita's 2025 net profit with the right value (2,695,300,000 EGP) but a mistyped ID: `...signed-en-p6-30` instead of `...signed_en-p6-30`. The value was right; the label pointing to the evidence was wrong.
- **Verifier, first check:** flagged it as "no such evidence ID" and asked for one revision.
- **The revision made things worse:** the agent rewrote its figures and stated two Telecom Egypt figures 1,000 times too small. It wrote revenue as 106.7 million instead of 106.7 billion, and net profit as 22.6 million instead of 22.6 billion. It had copied the printed numbers, which are in thousands, without converting.
- **Verifier, second check:** caught both as scale errors ("looks like a scale error by 1000"), removed them, and added a warning to the answer that those figures couldn't be verified.
- **End result:** no wrong figure reached the investor. But the answer was left with no figures at all. Separately, the agent's "hold" named no company, so the portfolio checks blocked it and it became "insufficient evidence".

This is the verifier working as designed ("fix, then flag"). It also shows a risk: a weak model's revision can introduce new errors, and then the verifier's only option is to drop them.

#### 2. Without a verifier, one wrong citation stayed (A, dev_011)

The single agent cited Telecom Egypt's share price (141.95 EGP) under an ID it invented, `price_ETEL_cutoff`. Share prices aren't report figures and have no evidence ID. The price itself was right, but the citation points to nothing, so the scorer counts it as wrong. Condition A has no verifier, so nothing caught it.

#### 3. The bigger problem: decisions without cited figures

Nemotron often decided without citing the evidence. For example, B bought 1,212 Talaat Moustafa shares (dev_002) and A sold 200 Edita shares (dev_007) with **no figures cited at all**. Coverage was only 11–37%, against 83–88% for Gemini.

The verifier only checks the figures an agent cites, so it can't help when the agent cites none. This matters for the paper: the verifier catches wrong numbers, but not missing evidence.

#### 4. The harder cases

| Case | Trap | What Nemotron did |
|---|---|---|
| dev_008 | Wrong number in the question (225.9 bn "profit") | No condition repeated the wrong figure. A and C held, B bought 250 shares, D kept cash. |
| dev_009 | Annualise the 9-month EPS | All four said "insufficient evidence". No annualised figure was cited. |
| dev_010 | Look-alike profit rows | No mix-ups. A and B bought 363 shares, C and D held. |
| dev_011 | 4 companies, mixed units | One invented price citation (A, above). C and D bought 3,921 Edita shares (79,988 EGP of the 80,000 cash). |
| dev_012 | Tempting unreadable figure | All four said "insufficient evidence". None used the unreadable figure. |

The traps meant to cause wrong figures mostly made Nemotron refuse to decide rather than make mistakes.

#### 5. Decisions

All four conditions chose acceptable actions in 9 of 12 cases (75%), against 71–100% for Gemini on the first 7 cases. The misses:
- "Insufficient evidence" where a decision was possible, in A, B, C and D (dev_003, dev_004, dev_005, dev_006, dev_007, dev_011).
- C and D sold 100 Telecom Egypt shares in dev_001, which this case doesn't allow; its acceptable actions are hold, buy and keep cash.

### Comparison with Gemini (first 7 cases)

| | Gemini 3.5 Flash | Nemotron Lightning |
|---|---|---|
| Wrong figures before the verifier | 0 in all conditions | 1 in A, 1 in B |
| Verifier activity | none | 1 revision, 2 figures dropped (B) |
| Coverage | 83–88% | 11–37% |
| Acceptable action | 71–100% | 75% |

### What this means

1. **The verifier can work:** with a weaker model, it caught a broken citation and then two 1,000× scale errors, and none of them reached the investor.
2. **But mistakes are rare even here:** 2 wrong citations out of about 80. With so few, the paper can't yet show a measurable effect.
3. **Missing evidence is the larger risk with a weak model.** A useful extra measure would be "decisions with no figures cited", which the verifier doesn't address.
4. **The Gemini half** (finishing the harder cases dev_008 to dev_012 under A–D) is scheduled for 25 November, after the free quota resets.

---

## Part 5: The 5 harder cases: Gemini vs Nemotron, 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

The 5 harder cases (dev_008 to dev_012) were built to tempt the agents into the figure mistakes the verifier exists to catch. This file compares the two free models on them.

| | Gemini 3.5 Flash | Nemotron Lightning |
|---|---|---|
| Run folder | `runs/20261124T094321Z` | `runs/20261124T095853Z` |
| When | A and B partly on 24 Nov; the rest on 25 Nov | 24 Nov |
| Runs that worked | 16 of 20 (C: 1 of 5) | 20 of 20 |

Gemini's C (team without verifier) failed on 4 of 5 cases, twice each, because the free daily quota ran out. A, B and D are complete for both models. This is a development run: the reference values are still the report reader's own, not hand-checked.

### The cases

| Case | Trap | What tempts a mistake |
|---|---|---|
| dev_008 | Wrong number in the question | The investor says Telecom Egypt's 2025 profit was 225.9 billion EGP, ten times 2024. That is its total assets; the real profit is 22.6 billion, about double 2024. |
| dev_009 | Annualise | The investor asks for full-year EPS and P/E from Abu Qir's 9-month EPS (8.74 EGP). |
| dev_010 | Look-alike rows | 12 similar Talaat Moustafa rows; the question is about the shareholders' share of profit only. |
| dev_011 | Many figures | 4 companies, 16 figures, in thousands of EGP and whole pounds. |
| dev_012 | Tempting unreadable figure | The investor asks for profit growth, but the 2025 profit is marked unreadable (its printed line is still shown). |

### Results on the 5 harder cases

| | Gemini A | Gemini B | Gemini C | Gemini D | Nemotron A | Nemotron B | Nemotron C | Nemotron D |
|---|---|---|---|---|---|---|---|---|
| Cases that ran | 5 | 5 | 1 | 5 | 5 | 5 | 5 | 5 |
| Figures cited | 33 | 36 | 2 | 34 | 14 | 7 | 9 | 5 |
| Wrong figures before the verifier | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Wrong figures in the final answer | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Average coverage | 83% | 85% | 100% | 85% | 25% | 14% | 32% | 7% |
| Acceptable action | 5 of 5 | 5 of 5 | 1 of 1 | 5 of 5 | 5 of 5 | 4 of 5 | 5 of 5 | 5 of 5 |
| "Insufficient evidence" | 2 | 2 | 1 | 2 | 2 | 3 | 2 | 2 |
| Verifier revisions / figures dropped | – | 0 / 0 | – | 0 / 0 | – | 0 / 0 | – | 0 / 0 |

**Did the verifier catch anything on these cases? No, for either model.** Nobody made a figure mistake for it to catch in B or D. The only wrong figure was in Nemotron A, which has no verifier: it cited the Telecom Egypt share price under an evidence ID it made up (dev_011).

The verifier's only catches so far are from the first 7 cases on Nemotron (B, dev_003: a mistyped ID, then two 1,000× scale errors from the revision, all removed). See the Nemotron write-up.

### How each trap went

#### dev_008: wrong number in the question

Gemini corrected the investor in every condition that ran, citing the right figures. For example, A wrote: "Your friend's statement is incorrect... The 225.9 billion figure actually represents total assets." D added that profit grew about 123%, "more than doubling", not tenfold. No answer repeated 225.9 billion as profit.

Decisions: Gemini A bought 175 shares (24,841 EGP), B bought 352 shares (49,966 EGP, almost all of the 50,000 cash), and D held. Nemotron: A and C held, B bought 250, D kept cash. All count as acceptable, because "buy" is allowed in this case. But Gemini B followed the investor's "put all my cash in" into one stock they already hold, which a careful adviser would question. The current scoring only checks the type of action, not its size, so it can't flag this.

#### dev_009: annualise

No condition of either model annualised the 9-month EPS or gave a full-year P/E. All of them said "insufficient evidence" and explained that full-year figures aren't available. That counts as acceptable.

#### dev_010: look-alike rows

There were no mix-ups between total profit, shareholders' profit and profit before tax. Gemini B cited all 12 figures correctly. Decisions were buy or hold, all acceptable.

#### dev_011: many figures across companies

Gemini cited 12–15 figures per answer, all correct, across both units, and chose CIB (500 or 625 shares; 625 × 128 = 80,000 EGP, exactly the cash available). Nemotron cited at most 4 and made the one wrong citation described above. Its B answer said "insufficient evidence", which isn't acceptable here.

#### dev_012: tempting unreadable figure

No condition of either model used the unreadable 2025 profit. All said "insufficient evidence" and pointed to the unreadable figure. Gemini also cited the verified figures (revenue, 2024 profit, EPS).

### What this means

1. **The traps didn't produce the mistakes they were designed for.** Both models handled all five cleanly, mostly by refusing to guess. Gemini made 0 mistakes in 105 figures cited on these cases.
2. **So the verifier still has very little to do.** Across everything run so far, it has caught mistakes in only one answer (Nemotron B, dev_003).
3. **The differences between the models are coverage and evidence, not accuracy.** Gemini cites 83–85% of the usable figures; Nemotron cites 7–32%. A weak model rarely states wrong numbers; it just states fewer numbers.
4. **Scoring blind spot:** a buy of almost all the investor's cash into one stock they already hold (Gemini B, dev_008) scores as acceptable, because only the type of action is checked. A size or concentration check in the scoring would catch this.
5. **For the paper:** to show a verifier effect, the experiment probably needs either many more cases, or a setting where figures are less pre-digested. Right now the agents get every value already in whole pounds next to its printed line, which makes copying easy.

---

## Part 6: Printed-figures view on Nemotron, 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

This run tests whether the agents make more figure mistakes when they have to read the figures themselves. In the original setup ("converted view"), each figure is shown already converted to whole pounds next to its printed line, so the agents only copy it. In the new **printed view** (`--evidence-view printed`), they see only the line as printed in the report and the page's unit (for example "L.E. (000)"). They must pick the right column and apply the unit themselves. The verifier and the scorer still compare against the converted value.

| | Converted view | Printed view |
|---|---|---|
| Run folder | `runs/20261124T095853Z` | `runs/20261125T084108Z` |
| Model | Nemotron 3.5 Lightning (NVIDIA free) | same |
| Cases | all 12 (dev_001–012), A–D | same |
| Runs that worked | 48 of 48 | 48 of 48 |

Reference values are still the reader's own, not hand-checked.

### Results

| | A conv. | A printed | B conv. | B printed | C conv. | C printed | D conv. | D printed |
|---|---|---|---|---|---|---|---|---|
| Figures in final answers | 24 | 23 | 16 | 10 | 24 | 15 | 12 | 15 |
| Wrong figures before the verifier | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 |
| Wrong figures in the final answer | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| Coverage of usable figures | 27% | 30% | 22% | 20% | 37% | 17% | 11% | 22% |
| Acceptable action | 9 of 12 | 8 of 12 | 9 of 12 | 10 of 12 | 9 of 12 | 8 of 12 | 9 of 12 | 6 of 12 |
| Verifier revisions | – | – | 1 | 1 | – | – | 0 | 0 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier.

### What happened

**1. Nemotron applied the units correctly.** Of the 77 correct figures it proposed in the printed view, 40 needed a unit conversion (for example thousands to pounds) and it got every one right. There were **no scale errors** in the printed view. Making the agents read the printed figures didn't produce the mistakes we hoped the verifier would catch.

**2. The two wrong figures were citation mix-ups, not unit errors.**
- **B, dev_011:** it put Talaat Moustafa's net profit (12,769,517,325) under the ID of Talaat Moustafa's earnings per share (4.38 EGP). **The verifier caught it** ("value_mismatch") and asked for one revision.
- **C, dev_011:** it cited the EFID share price under an ID it made up (`given_price_EFID`). C has no verifier, so this stayed in the final answer.

**3. A loophole in the verifier (important).** In B, dev_011, the revision fixed the problem by removing **all 16 figures** from the `claims` list, so the verifier found nothing left to check and passed it. But the written explanation still states the figures: "ETEL 123% (2025 EGP 22,578,063,000 vs 2024 EGP 10,111,328,000)", P/E values, and so on. The verifier only checks figures listed in `claims`, not numbers written in the text. A weak model can "pass" the verifier by citing nothing. The figures in this text happen to be right, but nothing checked them.

**4. Fewer figures and more refusals.** In the printed view Nemotron cited fewer figures in B and C and chose "insufficient evidence" more often. D fell to 6 of 12 acceptable actions: it refused on normal cases like dev_001, dev_004 and dev_007, where a buy, hold or sell was expected.

**5. The old problem repeats.** In A and B on dev_003, it answered "hold" with no ticker, the portfolio check blocked it, and the answer became "insufficient evidence". The same thing happened in the converted view.

### What this means

- For Nemotron, the printed view **didn't create unit or column mistakes**. Reading the figures was not the hard part; deciding what to cite was.
- The verifier caught one real mistake (B, dev_011), its second catch so far after B, dev_003 in the converted view.
- **The verifier needs two fixes before the final runs:**
  1. Check numbers written in the explanation, not only the `claims` list. Any number in the text that matches no cited claim is flagged.
  2. Count a revision that removes all figures as a drop, so "cite nothing" doesn't count as a fix.
- The scoring should also report "decisions with no figures cited" (already on the list): Nemotron's printed-view D gave 7 of 12 answers with no figures at all.
- Gemini's run on the printed view comes next, as the free quota allows. It will show whether a stronger model makes unit mistakes when reading the printed figures.

---

## Part 7: Fixed verifier on Nemotron (printed view), 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

The first run with the printed figures (`runs/20261125T084108Z`, see `printed_view_nemotron_2026-11-25.md`) showed a loophole: the verifier only checked the figures in the `claims` list. A revision could remove every claim and still state the figures in the explanation, and nothing checked them.

### What changed in the verifier (commit 64180bf)

- **It also checks the figures written in the explanation.**
  - **Uncited figure:** the text states a number that matches an evidence figure, but that figure isn't in `claims`.
  - **Text scale mismatch:** the text states a number that matches an evidence figure only at the wrong scale (×1,000, ×1,000,000 or ×1,000,000,000).
  - Rounding is allowed (0.5%), so "22.6 billion" counts as 22,578,063,000.
  - Arabic digits, Arabic scale words (مليار, مليون) and numbers like 1.6e9 are read.
- **Some numbers aren't treated as evidence figures:**
  - percentages;
  - numbers under 1,000,000, which must match exactly, so a P/E of 11.9 isn't mistaken for an EPS of 11.93;
  - short plain numbers in the scale check, such as a 82.50 EGP share price;
  - the agent showing its unit arithmetic ("22,578,063 × 1,000 = 22,578,063,000"). This last one was added after this run, because it caused one false alarm here.
- **If a figure still fails after the one revision,** the sentence that states it is replaced with "[removed: figure could not be verified]" and listed as a limitation.
- **Figures cited before the revision but not after are recorded as withdrawn.** The scorer counts them as dropped, so citing nothing no longer counts as a fix.

Before the rerun, the new check was replayed on answers already collected, with no model calls:
- **Gemini:** 0 of 44 answers would have been flagged. Gemini cites every figure it writes.
- **Nemotron:** 27 of 48 answers (converted view) and 16 of 48 (printed view) would have been flagged.

### The rerun

Same setup as the first printed-view run (Nemotron 3.5 Lightning, NVIDIA free, 12 cases × A–D, printed view), with the fixed verifier: `runs/20261125T110056Z`, 48 of 48 runs worked.

| | A | B | C | D |
|---|---|---|---|---|
| Cited figures in final answers | 14 | 28 | 19 | 12 |
| Wrong cited figures in final answers | 0 | 0 | 2 | 0 |
| **Uncited evidence figures in the final text** | **6** (in 5 answers) | **0** | **17** (in 6 answers) | **0** |
| Uncited figures in the text before the verifier | 11 | 24 | 17 | 9 |
| Answers the verifier sent back for revision | – | 6 of 12 | – | 4 of 12 |
| Answers with figures removed after the revision | – | 2 | – | 1 |
| Coverage of usable figures | 17% | 29% | 23% | 16% |
| Acceptable action | 9 of 12 | 10 of 12 | 7 of 12 | 7 of 12 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier. Reference values are still the reader's own, not hand-checked. Different runs of the same model give somewhat different answers, so small differences between runs (for example in acceptable actions) are not meaningful on 12 cases.

### What the verifier did

**1. It made the agents cite what they write.** The single agent (B) first wrote 24 evidence figures without citing them, and the team (D) wrote 9. After the verifier, both final answers have none, because the revisions added the missing claims. That's why B cites twice as many figures as A (28 vs 14) and has the highest coverage. Without a verifier, A and C still reach the investor with 6 and 17 unchecked figures.

**2. It caught the per-share trap, its first catch of a real unit error.** In B, dev_011, the agent applied the "EGP thousands" unit to earnings per share. It wrote CIB's EPS as 18,250 EGP instead of 18.25, and Telecom Egypt's as 11,930 instead of 11.93, which gave P/E ratios of 0.007 and 0.012. The verifier flagged it. The revision still got it wrong, so those figures were removed, and the final answer (buy EFID) has 6 cited figures, all correct.

**3. It removed a made-up evidence ID** (B, dev_007).

**4. Without a verifier, the team made two citation mistakes that reached the final answer:**
- **C, dev_011:** the EFID share price was cited under a made-up ID.
- **C, dev_012:** EFID's 2025 profit (2,695,301,670) was cited under the ID of the 2024 profit, which is the wrong period.

**5. One false alarm, now fixed.** In B, dev_008, the agent showed its arithmetic ("22,578,063 × 1,000 L.E. = 22,578,063,000"), and the check read "22,578,063" as a scale error. The only cost was one extra revision. The check now ignores a number followed by "× 1,000"; the change is in the code and has tests.

**6. Unit handling:** 39 of the correct cited figures needed a unit conversion, and all 39 were right. The only unit error was the per-share one in point 2.

### Still open

- **The scoring counts only cited figures.** Uncited figures in the text are counted here by a separate script (`check_text`), not by `egx_guide.score`. For the paper, "wrong or unchecked figures reaching the investor" should include them. The next step is to add this to the scorer.
- **"Hold" with no company** (dev_003) is still blocked by the portfolio check in A, B and C. It's a prompt issue, not a verifier issue.
- **Gemini's printed-view run** with this verifier comes next, as the free quota allows.

---

## Part 8: New measures, the hold rule, and full-length Nemotron answers (25 November 2026)

This part covers four things done on 25 November:
- new measures in the scoring;
- a prompt rule for "hold";
- a fault found in every earlier Nemotron run: its explanations were cut at 1,024 characters;
- a full rerun of Nemotron with that fault fixed.

The full-length rerun (`runs/20261125T141730Z`) replaces the earlier Nemotron runs as Nemotron's result.

### 1. New measures in the scoring

Until now the scoring only checked the figures listed in `claims` and the type of action. Four measures were added (commit e0f90fd):

- **Uncited figures in the text:** the explanation states a figure from the evidence, but it isn't in `claims`. The investor reads it, but nothing checked it.
- **Wrong-scale figures in the text:** the explanation states a number that matches an evidence figure only at ×1,000, ×1,000,000 or ×1,000,000,000.
  - Quoting the printed number with its unit, as in "printed 82,258,815 → 82,258,815,000 EGP" or "107,699,631 EGP thousands", is not counted. That is the agent showing its work.
- **Decisions citing no figure:** a buy, sell or hold that cites no figure at all. "Insufficient evidence" and "keep cash" don't count.
- **Buys over 50% in one stock:** after the buy, more than half the investor's portfolio is in that company, at the case prices.

All runs were rescored with these measures (table in section 6).

### 2. The hold rule

In earlier runs, the agents sometimes chose "hold" for a company the investor didn't own. The portfolio check then blocked the answer (dev_003 in A, B and C). The agents' rules now say:

> hold means keeping a stock the investor already owns: set `ticker` to that company. If they own none of the companies discussed, do not choose hold.

Rerun with the rule (`runs/20261125T124422Z`): **no answer was blocked** in any condition. dev_003 now gets "hold ETEL" (an owned stock) in A and B and "sell EFID" in C and D.

### 3. The fault: Nemotron's explanations were cut at 1,024 characters

While checking the hold-rule run, one explanation was found to end in the middle of a number ("ETEL operating revenues 106,672,"). It was exactly 1,024 characters long. So were 226 others across all the Nemotron runs (first drafts and final answers); in the hold-rule run, 22 of the 48 final answers were cut.

- **Cause:** NVIDIA's service. In function-calling mode (how the program asked for a structured answer), it cuts every text field at 1,024 characters. A test with a requested 2,500-character essay came back at exactly 1,024. The same request in NVIDIA's json_schema mode came back complete (4,159 characters).
- **Gemini was not affected.** No Gemini answer is cut.
- **Fix (commit 9c02dba):** Nemotron now uses json_schema mode, and the run manifest records which mode was used.
- **Cost of the fix:** in this mode Nemotron reasons much longer before answering. A model call now writes about 8,000 tokens on average instead of about 4,300, and takes about 2.3 minutes instead of about 40 seconds. The full run took about 1¾ hours with the four conditions running side by side, still free.
- **Dropped connections:** 4 answers (one per condition) lost their connection after 17–19 minutes. A new `--resume` option reran just those answers in the same run folder, so all 48 finished.

**What this means for the earlier results:** Parts 4–7 report Nemotron runs with cut explanations. Their figure counts in the text are too low, and the conclusion "no unit errors with the printed figures" (Part 6) does not hold for full-length answers (section 4).

### 4. Full-length Nemotron run

Same setup as Part 7: Nemotron 3.5 Lightning, NVIDIA free, 12 cases × A–D, printed figures, fixed verifier, plus the hold rule. Run `runs/20261125T141730Z`, 48 of 48 answers.

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited in final answers | 46 | 38 | 36 | 26 |
| Wrong cited figures in final answers | **11 (24%)** | **0** | **15 (42%)** | **0** |
| Wrong cited figures before the verifier | 24% | 33% | 42% | 42% |
| Answers with at least one wrong figure | 3 of 12 | 0 | 3 of 12 | 0 |
| Uncited evidence figures in the final text | 17 | 0 | 11 | 0 |
| Wrong-scale figures in the final text | 1 | 0 | 1 | 0 |
| Coverage of usable figures | 37% | 48% | 31% | 36% |
| Answers sent back by the verifier | – | 9 of 12 | – | 7 of 12 |
| Acceptable action | 5 of 12 | 6 of 12 | 4 of 12 | 7 of 12 |
| "Insufficient evidence" chosen | 10 of 12 | 9 of 12 | 10 of 12 | 7 of 12 |
| Buys over 50% in one stock | 2 | 2 | 1 | 1 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier. Reference values are still the reader's own, not hand-checked.

#### The figure mistakes

With room to write, Nemotron cites two to three times as many figures as before, and gets many wrong:
- **Forgetting the unit (×1,000):** the printed number copied as pounds, for example CIB's net interest income given as 107,699,631 EGP instead of 107,699,631,000 (the page is in thousands). There were 17 such figures in the first drafts across the four conditions (A 4, B 6, C 4, D 3).
- **The wrong year's column:** a row printed with 2025 and 2024 side by side, and the 2025 value cited as 2024. For example, Talaat Moustafa's 2024 profit was given as 18,201,981,482 (the 2025 figure), and 2024 EPS as 6.98 instead of 4.38.
- **Per-share figures scaled wrongly:** CIB's EPS of 18.25 given as 1,825.
- **Made-up evidence IDs**, and **one figure marked unreadable used anyway** (A).

#### What the verifier did

1. **No wrong figure reached the investor with the verifier.** 33% of B's first-draft figures and 42% of D's were wrong, and 0% of their final ones. Without a verifier, A and C passed on 11 and 15 wrong figures.
2. **No unchecked figures in the text with the verifier.** B's first drafts had 33 uncited evidence figures in the text, and D's 26. The final answers have none. A and C still show 17 and 11.
3. **It often had to remove text rather than fix it.** Nemotron's single revision often didn't add the missing claims, so the verifier removed the sentences:
   - B: 14 sentences removed in 4 answers;
   - D: 17 sentences removed in 3 answers.

   Some of these removals came from false alarms (point 4).
4. **False alarms, now fixed.** During the run, the scale check still flagged numbers the agent quoted with their unit ("22,578,063 L.E. (000) = 22,578,063,000"). In B dev_008 and D dev_008, this led to correct sentences being removed. The check now treats a number as quoted, not wrong, if any of these hold:
   - the unit follows it in the same clause;
   - an arrow or "=" leads to the converted value;
   - "printed" comes just before it.

   It has tests built from these real sentences. On rescoring, 18 of the 20 scale flags in the final texts went away. The 2 left are also quotes: in one, the agent itself rejects the ×1,000 reading of EPS as "unrealistic".

#### The cost: very cautious decisions

In this mode Nemotron chooses "insufficient evidence" in 7–10 of 12 answers per condition, often where a decision was expected. So acceptable actions fall to 33–58%, from 50–92% in the cut runs.
- **This is the model's own caution, not the verifier's.** The verifier changed the action in only one answer (B dev_001, hold → insufficient evidence). A and C, which have no verifier, are the most cautious.
- **It counts against Nemotron as the decision-maker for the paper.** With room to reason and write, it cites more figures and also refuses more often.

### 5. Concentration: buys that put almost everything into one stock

The new concentration measure shows something the action check could not see. Both models often spend all the investor's free cash on one company, leaving 99–100% of the portfolio in it:
- **Gemini:** 6 of its 12 single-agent (A) answers across both Gemini runs.
- **Nemotron:** 1–3 per condition in most runs.

The prompt rules only say a buy must fit the available cash; they say nothing about how much should go into one stock. For the paper, this is a second finding, separate from the figures: the guide's decisions need a diversification rule, and the evaluation needs this measure.

**The rule added afterwards, and its check.** The agents' rules now say that after a buy no single company may be more than half of the portfolio's value. Nemotron was rerun (A and B, printed figures) on the 7 cases where buys had gone over 50%:
- **First version, with an exception** "if the investor's profile clearly supports it" (`runs/20261125T162311Z`): 3 of 4 buys stopped at exactly 50%. The fourth (A, dev_011) used the exception to put the whole portfolio into Edita, giving a "medium" willingness to accept losses as the reason. So the exception was removed (commit 0ea1490).
- **Strict version, no exception** (`runs/20261125T192524Z`): no buy over 50%. The same A dev_011 answer now buys 1,960 Edita shares, exactly 50% (before: 3,921 shares, 100%). Nemotron made fewer buys overall in this run (1 in 14 answers) and chose "insufficient evidence" more often, which fits its caution in section 4.
- **A separate, older fault showed up again:** two B answers chose hold or keep cash and still gave a share count (500 TMGH, 150 ETEL). The portfolio check blocks such answers. It is not caused by the new rule; the same block appears in the earlier runs. A rule was added that `shares` is 0 for hold, keep cash and insufficient evidence (commit edf599d). Rerun on the two cases (dev_008, dev_010; A and B, `runs/20261125T235154Z`): no answer blocked, B dev_010 now gives "hold TMGH" without a share count.

The 50% limit matches the scoring's concentration measure.

### 6. All runs rescored with the new measures

Cells give A / B / C / D. "Cut" marks runs whose Nemotron explanations stopped at 1,024 characters.

| Run | Figures cited | Wrong cited figures | Uncited figures in text | Wrong-scale figures in text | Acceptable action | Buys >50% in one stock |
|---|---|---|---|---|---|---|
| Gemini, 7 cases, figures in pounds | 34 / 31 / 32 / 33 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 86% / 100% / 71% / 86% | 3 / 3 / 1 / 1 |
| Gemini, 5 harder cases, figures in pounds | 33 / 36 / 2 / 34 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 100% / 100% / 100% / 100% | 3 / 2 / 0 / 1 |
| Nemotron, figures in pounds (cut) | 24 / 16 / 24 / 12 | 1 / 0 / 0 / 0 | 16 / 14 / 12 / 15 | 0 / 0 / 0 / 0 | 75% / 75% / 75% / 75% | 3 / 3 / 2 / 1 |
| Nemotron, printed, old verifier (cut) | 23 / 10 / 15 / 15 | 0 / 0 / 1 / 0 | 4 / 20 / 3 / 5 | 0 / 0 / 0 / 0 | 67% / 83% / 67% / 50% | 3 / 3 / 2 / 2 |
| Nemotron, printed, fixed verifier (cut) | 14 / 28 / 19 / 12 | 0 / 0 / 2 / 0 | 6 / 0 / 17 / 0 | 0 / 0 / 0 / 0 | 75% / 83% / 58% / 58% | 2 / 3 / 2 / 2 |
| Nemotron, printed, hold rule (cut) | 20 / 25 / 21 / 10 | 3 / 0 / 5 / 0 | 24 / 0 / 5 / 0 | 0 / 0 / 1 / 0 | 92% / 83% / 67% / 50% | 5 / 3 / 2 / 2 |
| **Nemotron, printed, full length** | 46 / 38 / 36 / 26 | **11 / 0 / 15 / 0** | **17 / 0 / 11 / 0** | 1 / 0 / 1 / 0 | 42% / 50% / 33% / 58% | 2 / 2 / 1 / 1 |

Gemini's C on the harder cases has only 1 scored answer; the free quota ran out.

### 7. Where this leaves the study

- **The verifier now has clear work to do, on Nemotron.** With full-length answers and the printed figures, a quarter to two fifths of Nemotron's first-draft figures are wrong (24–42% by condition). The verifier stopped all of them, in both the single agent (B) and the team (D). This is the main comparison the paper needs (A vs B, C vs D), although on a weaker model and only 12 cases.
- **Gemini still makes no figure mistakes** on the figures already in pounds. Its run with the printed figures (next, as the free quota allows) is the test of whether a stronger model also falls into the unit traps.
- **Nemotron is a poor decision-maker in this mode.** It is too cautious. If it stays in the study, it is best as a second model for the figure results, not for the decision results.
- **Still open:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts;
  - the rule on how much to put into one stock is now in place and strict, and hold or keep cash no longer carries a share count (section 5).

---

## Part 9: Gemini 3.5 Flash-Lite with printed figures (26 November 2026)

This part runs a Gemini model on the printed figures for the first time: the agents see each figure as printed in the report, with its unit line, and must apply the unit themselves. Until now only Nemotron had been run this way (Parts 6–8).

### Setup

- **Model:** Gemini 3.5 Flash-Lite, Google free tier, temperature 0, one model for every answer (no fallback).
  - It is not the Gemini 3.5 Flash of Parts 1 and 5. Flash's free daily quota was used up when the run started, so its printed-figures run comes later. Gemini 3.1 Flash-Lite was also tried, but it timed out.
- **Cases:** the 12 development cases, conditions A–D, printed figures. Run `runs/20261126T001437Z`, 48 of 48 answers.
- **Prompt rules in force:**
  - the hold rule (Part 8, section 2);
  - the strict one-stock limit: after a buy, no company may be more than half the portfolio, with no exceptions;
  - `shares` is 0 for hold, keep cash and insufficient evidence (Part 8, section 5).
- **Running:** the four conditions ran side by side.
  - 4 answers hit the free tier's limit of 15 requests a minute; `--resume` reran them.
  - Flash-Lite is fast: 6–9 seconds per answer for the single agent, about 21 seconds for the team. The whole run took under half an hour.

### Results

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited in final answers | 31 | 36 | 29 | 24 |
| Wrong cited figures in final answers | **0** | **0** | **0** | **0** |
| Wrong cited figures before the verifier | 0% | 0% | 0% | 4% (1 figure) |
| Uncited evidence figures in the final text | 1 | 0 | 2 | 0 |
| Wrong-scale figures in the final text | 0 | 0 | 0 | 0 |
| Coverage of usable figures | 46% | 59% | 47% | 36% |
| Answers sent back by the verifier | – | 1 of 12 | – | 2 of 12 |
| Acceptable action | 11 of 12 | 11 of 12 | 11 of 12 | 9 of 12 |
| "Insufficient evidence" chosen | 2 of 12 | 2 of 12 | 2 of 12 | 4 of 12 |
| Answers blocked by the portfolio check | 0 | 0 | 0 | 0 |
| Buys over 50% in one stock | 0 | 0 | **3** | **1** |

A = single agent, B = single agent + verifier, C = team, D = team + verifier. Reference values are still the reader's own, not hand-checked.

Nemotron with the same printed figures (Part 8, section 4), for comparison:

| | Gemini 3.5 Flash-Lite | Nemotron Lightning |
|---|---|---|
| Wrong figures in first drafts (A / B / C / D) | 0% / 0% / 0% / 4% | 24% / 33% / 42% / 42% |
| Wrong figures reaching the investor without a verifier (A / C) | 0 / 0 | 11 / 15 |
| Acceptable action (A / B / C / D) | 92% / 92% / 92% / 75% | 42% / 50% / 33% / 58% |

### What the results show

#### 1. Flash-Lite applies the units correctly

Flash-Lite converted the printed figures without the mistakes Nemotron made:
- no figure left in thousands;
- no wrong year's column;
- no per-share figure scaled.

All 120 cited figures in the final answers match the reference.

So the verifier had little to do:
- **B dev_008 and D dev_008:** sent back because the text named Telecom Egypt's total assets ("225.9 billion") without listing it in the claims. Both revisions added it.
- **D dev_006:** sent back because the team used Talaat Moustafa's Arabic 2025 profit, which is marked unreadable (unclear separators). The revision withdrew it. This is the only wrong first-draft figure in the run.

The unit traps in the printed figures therefore separate the two models clearly. A weaker model (Nemotron) needs the verifier; Flash-Lite mostly does not. Whether the full Gemini 3.5 Flash behaves like Flash-Lite is the next run.

#### 2. The new prompt rules hold for the single agent

- **One stock:** no single-agent buy (A or B) leaves more than half the portfolio in one company. Before the rule, Gemini's single agent did so in 6 of its 12 answers (Part 8, section 5). Buys now stop at 50% (600 TMGH shares in dev_002) or below (300 ABUK shares, 35%, in dev_005).
- **Shares 0 and hold:** no answer was blocked by the portfolio check. Every hold names a stock the investor owns and carries no share count.

#### 3. The team states the 50% limit and then breaks it

In 4 team answers the final buy leaves more than half the portfolio in one stock. In all 4, the explanation states the rule and claims to follow it, but the `shares` field does not match:

| Answer | Explanation says | `shares` field | Portfolio in that stock |
|---|---|---|---|
| C dev_002 | "reduce the purchase… Buying 606 shares… exactly 50%" | 1,212 TMGH | 100% |
| C dev_005 | works out the 50% limit for ABUK | 524 ABUK | 61% |
| C dev_008 | "buying 140 shares total is not allowed" | 140 ETEL | 58% |
| D dev_008 | "exactly 50% of the total portfolio value" | 104 ETEL | 51% |

- **What went wrong:** the decision agent seems to fill in the share count from its first plan (often "all the cash") and then corrects only the text. D dev_008 is a small arithmetic slip; the other three are clear contradictions.
- **The single agent did not do this.** The team's decision agent reads two analyst reports on top of the case, and the suitability analyst, whose prompt has no 50% limit, said in dev_002 and dev_005 that all the cash could be committed.
- **The verifier cannot see it.** It checks figures against the evidence, not the action against the explanation.

For the paper, this is a second kind of error next to wrong figures: **the decision does not match the explanation the investor reads**. An investor reading C dev_002 would expect a 50% position and get 100%.

### Open items

- **Decided: flag, don't block.** Since this run, the portfolio check flags a buy that leaves more than half the portfolio in one stock: the record gets a `concentration` warning with the share. The answer still goes through.
  - Blocking would turn the answer into "insufficient evidence", and A–D would then all look the same on this point, hiding the finding above.
  - Selling shares the investor does not own stays blocked, because it is impossible, not just unwise.
  - Earlier runs have no warning field; the scorer's "buys over 50%" measure covers them from the saved portfolio.
- **The suitability analyst's prompt** could also name the limit.
- **The Gemini 3.5 Flash run** on the printed figures, as its free quota allows (about 20 requests a day; the run needs about 100).
- **Still open from before:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts.

---

## Part 10: Qwen3.8-27B with printed figures (26 November 2026)

A third model, run in the same way as Gemini 3.5 Flash-Lite (Part 9) and Nemotron (Part 8).

### Setup

- **Model:** Qwen3.8-27B (FP8), on SovereignEG's free Student plan, temperature 0. The plan includes about 3.8 million tokens a day for this one model.
  - Only this free model was called. SovereignEG lists many paid models.
  - The account's spending switches are off and the key has a spend cap of 0.
- **Output mode:** json_schema. The default function-calling mode fails on this service: the model names the answer tool "Recommend" instead of "Recommendation" (commit 973bfb5).
- **Cases and run:** the 12 development cases, conditions A–D, printed figures. Run `runs/20261126T094527Z`, 48 of 48 answers.
- **Prompt rules:** the same as Part 9, i.e. the hold rule, the strict one-stock limit, and shares 0 for hold, keep cash and insufficient evidence. The portfolio check now also flags buys over 50% (Part 9).
- **Running:**
  - The free plan allows only 2 requests at a time and 20 a minute. A first try with the four conditions side by side was refused at once, so the run went through one request at a time.
  - It took about an hour: 30 seconds per answer for the single agent, 50 with the verifier, and about 100–120 for the team.
  - It used about 430,000 output tokens, well inside the daily allowance.

### Results

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited in final answers | 86 | 73 | 74 | 73 |
| Wrong cited figures in final answers | **16 (19%)** | **0** | **6 (8%)** | **0** |
| Wrong cited figures before the verifier | 19% | 22% | 8% | 17% |
| Answers with at least one wrong figure | 6 of 12 | 0 | 5 of 12 | 0 |
| Uncited evidence figures in the final text | 4 | 0 | 2 | 0 |
| Wrong-scale figures in the final text | 0 | 0 | 0 | 0 |
| Coverage of usable figures | 87% | 89% | 87% | 91% |
| Answers sent back by the verifier | – | 6 of 12 | – | 5 of 12 |
| Sentences removed by the verifier | – | 0 | – | 0 |
| Acceptable action | 12 of 12 | 12 of 12 | 12 of 12 | 11 of 12 |
| "Insufficient evidence" chosen | 0 | 0 | 2 of 12 | 2 of 12 |
| Answers blocked by the portfolio check | 0 | 0 | 0 | 0 |
| Buys over 50% in one stock (flagged) | 0 | 0 | 0 | 0 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier. Reference values are still the reader's own, not hand-checked.

#### The three models side by side (printed figures, 12 cases)

| | Qwen3.8-27B | Gemini 3.5 Flash-Lite | Nemotron Lightning |
|---|---|---|---|
| Wrong figures in first drafts (A / B / C / D) | 19% / 22% / 8% / 17% | 0% / 0% / 4% (D) only | 24% / 33% / 42% / 42% |
| Wrong figures reaching the investor without a verifier (A / C) | 16 / 6 | 0 / 0 | 11 / 15 |
| Wrong figures reaching the investor with the verifier (B / D) | 0 / 0 | 0 / 0 | 0 / 0 |
| Coverage of usable figures (A / B / C / D) | 87% / 89% / 87% / 91% | 46% / 59% / 47% / 36% | 37% / 48% / 31% / 36% |
| Acceptable action (A / B / C / D) | 100% / 100% / 100% / 92% | 92% / 92% / 92% / 75% | 42% / 50% / 33% / 58% |
| Buys over 50% in one stock (A / B / C / D) | 0 / 0 / 0 / 0 | 0 / 0 / 3 / 1 | 2 / 2 / 1 / 1 (before the rule) |

### What the results show

#### 1. Qwen is the most useful model so far for the verifier comparison

- **It decides well.** It gives an acceptable action in 47 of 48 answers, and it rarely falls back on "insufficient evidence".
- **It uses the evidence fully.** It cites almost 9 in 10 of the usable figures, about twice as many as the other two models.
- **Its claims often don't match their evidence.** Between 8% and 22% of the figures in its first drafts are wrong, mostly citation errors rather than misreadings (section 2). Once the row's other numbers got their own IDs, this fell to 0–3% (section 6). With no verifier, 16 (A) and 6 (C) such figures reach the investor.
- **The verifier stops all of them.** B and D end with 0 wrong figures and 0 unchecked figures in the text.
  - B sent back 6 of 12 answers and D 5 of 12.
  - Each time, Qwen's single revision corrected the figures, so no sentence had to be removed. With Nemotron, many sentences had to be removed (Part 8).

So Qwen shows the effect the paper is about, on decisions that are otherwise good. Nemotron's decisions were too cautious to judge, and Flash-Lite made too few mistakes for the verifier to matter.

#### 2. The mistakes: right numbers under the wrong evidence ID

*Corrected after section 5:* an earlier version of this part said most mistakes were "the 2024 column taken for 2025". Reading each claim's own statement shows otherwise.

Of the 54 wrong first-draft figures across the four conditions:
- **45 are another number from the same printed row, described correctly.** In 40 of them, the claim reads e.g. "EFID consolidated revenue for FY2024: 16,146,545,699", which is correct. The other 5 are the printed change in % ("EPS growth 2024 to 2025: 59.6%").
  - Each case gives an evidence ID only to the figure chosen for it, here the 2025 one. So Qwen cited the 2024 number (or the %) under the 2025 figure's ID. The number does not match the cited evidence, so the scorer counts it wrong, and the verifier sends it back.
- **9 have the unit wrong in the claim only:** CIB figures, in A and B on dev_004.
  - The claim's statement converts correctly ("107,699,631 thousand EGP = 107,699,631,000 EGP"), but its value field was left in thousands.
- **None is a real misreading** of the printed report.

So Qwen's errors are **citation errors**: the explanation the investor reads is right, but the figure is tied to the wrong evidence item, or its value field has the wrong unit. The "wrong figures reaching the investor" for A and C (16 and 6) count these. They overstate the harm to the investor, though they are still claims that do not match their cited evidence.

The team (C) makes fewer of these than the single agent (A): 8% against 19%.

#### 3. The column headings

The printed evidence first gave each row without the table's column headings, e.g. "Operating revenues 106 672 946 81 677 812" for the period 31 December 2025. On the real page the headings ("31/12/2025 | 31/12/2024") are visible. They were added (commit e86629e), and Qwen was rerun (section 5).

#### 4. The rules held, including in the team

- **No buy over 50%,** in any condition, so no concentration flags. The team also kept to the limit, unlike Flash-Lite's team (Part 9).
- **No answer was blocked,** and every hold carried no share count.

### 5. Rerun with the column headings

Same model and setup on the dev cases rebuilt with column headings (the only change to the cases). Run `runs/20261126T105725Z`, 48 of 48 answers.

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited in final answers | 98 | 75 | 84 | 75 |
| Wrong cited figures in final answers | 21 (21%) | **0** | 9 (11%) | **0** |
| Wrong cited figures before the verifier | 21% | 15% | 11% | 9% |
| Coverage of usable figures | 92% | 89% | 93% | 92% |
| Answers sent back by the verifier | – | 6 of 12 | – | 4 of 12 |
| Acceptable action | 12 of 12 | 12 of 12 | 11 of 12 | 10 of 12 |

**The headings changed little.** There were 50 wrong first-draft figures, against 54 without headings, and their kinds are the same:
- **42:** another number from the same row, described correctly but cited under the chosen figure's ID:
  - 27 are the 2024 figure;
  - 15 are the quarter's figure or the change in %. With the headings, Qwen now also cites Abu Qir's three-month EPS (1.99, 1.23) under the nine-month ID.
- **4:** the CIB unit wrong in the claim's value field only.
- **2:** other numbers cited under an EPS ID (a share price, a P/E ratio Qwen worked out).
- **2 real misreadings:** Telecom Egypt's net profit, printed "22 578 063" (thousands, spaces as separators), read as 578,063 in A and B. Both were caught by the verifier in B.

**The verifier again stopped every wrong figure** in B and D. Each time, the revision fixed the figures, and no sentences were removed.

**Conclusion:** the headings make the evidence match what a reader of the page sees, and they stay. But Qwen's "year-column mistakes" were never misreadings. They come from the cases giving an evidence ID only to the chosen period's figure, while the row the agents see also prints other periods. Agents that compare years, as an investor would expect, have no correct ID to cite.

### 6. Rerun with the row's other numbers given their own IDs

Every number printed in a chosen figure's row now has its own evidence ID: the other period, the quarter and the change in % (commit df67322). These extra items are checked like any other cited figure. They do not count toward coverage, which still measures the figures chosen for the case. The dev cases gained 60 such items, and no chosen figure changed. Same model and setup otherwise. Run `runs/20261126T122300Z`, 48 of 48 answers.

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited in final answers | 94 | 87 | 81 | 89 |
| …of them, the row's other numbers under their own ID | 17 | 20 | 21 | 23 |
| Wrong cited figures in final answers | **3 (3%)** | **0** | **0** | **0** |
| Wrong cited figures before the verifier | 3% | 1% | 0% | 0% |
| Answers with at least one wrong figure | 2 of 12 | 0 | 0 | 0 |
| Uncited evidence figures in the final text | 3 | 0 | 3 | 0 |
| Coverage of usable figures | 92% | 82% | 80% | 85% |
| Answers sent back by the verifier | – | 3 of 12 | – | 1 of 12 |
| Sentences removed by the verifier | – | 0 | – | 0 |
| Acceptable action | 12 of 12 | 12 of 12 | 12 of 12 | 11 of 12 |
| Buys over 50% in one stock (flagged) | 0 | 0 | 1 | 0 |

**The citation errors are gone.** Wrong first-draft figures fell from 50 (section 5) to 4. Qwen now cites the 2024 figure, the quarter or the change in % under that number's own ID, 17 to 23 times per condition.

**The 4 that remain:**
- **2 real misreadings,** the same as in section 5: Telecom Egypt's net profit "22 578 063" read as 578,063 thousand, in A and B (dev_011). B's verifier sent it back and the revision fixed it.
- **2 changes in %** on Talaat Moustafa's Arabic summary page (A, dev_006): revenue growth 46% and EPS growth 59.6%, cited under the 2025 figures' IDs. The reader did not extract the % column on that page, so these numbers still have no ID of their own.

**What changed for the comparison:**
- **The verifier now has little to catch from Qwen.** Without a verifier, 3 wrong figures reach the investor in A and none in C. In section 5 the numbers were 21 and 9. The verifier sent back 3 answers in B and 1 in D, mostly for evidence figures written in the text without a citation.
- **Coverage fell a little** (80–92% against 89–93%). Some claims now cite the row's other numbers instead of the chosen figure.
- **One buy just over the limit:** the team's buy of Edita in dev_011 leaves EFID at 50.0% after rounding, just above 50%. It was flagged, as designed, and not blocked.
- **Decisions are unchanged:** 47 of 48 acceptable. The one miss (D, dev_005) is again "insufficient evidence".

**Conclusion:** most of Qwen's earlier "wrong figures" came from how the cases were built, not from the model. With fair IDs, Qwen's first drafts are almost all correct. The verifier's main effect on Qwen is now its uncited-figure check, and real misreadings (Telecom Egypt) are rare. For the paper, this means the verifier's measured benefit depends strongly on how the evidence is presented. Errors made by the reader (scale, spacing, missing columns) remain the main source of wrong figures.

### Open items

- **The row's other numbers** now have their own evidence IDs (section 6). The hand-checked reference sheet will need rows for them. The build reports any that are missing.
- **The Talaat Moustafa % column** (section 6) is now added by hand. Its 15 change-% numbers were read from the page into `data/cases/added_evidence.json`, and each one joins its row with its own ID (e.g. revenue +46%, EPS +59.6%). Only dev_006 changed: it gained 3 such items.
  - **Qwen rerun on dev_006** (A–D, run `runs/20261126T133104Z`): all four answers cite revenue +46%, net profit +43% and EPS +59.6% under their own IDs. There are 0 wrong figures, before and after the verifier, and coverage is 100%.
  - The two % errors from section 6 are gone, so the only real misreading left on the dev cases is Telecom Egypt's net profit.
  - The single agent's action changed from hold to buy, and both are acceptable for this case.
- **Qwen as a study model.** It fits the main comparison best so far, and its free daily allowance covers a full run of the 30 test cases in a day.
- **The Gemini 3.5 Flash run** on the printed figures is in progress (13 of 48 answers after day 1).
- **Still open from before:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts.

---

## Part 11: Three free models on the same cases (26 November 2026)

Parts 8–10 compared the models on different versions of the development cases. Here all three run on the current cases:
- printed figures with column headings;
- every number in a chosen figure's row has its own evidence ID;
- the hand-read Talaat Moustafa change-% column is added;
- the same prompts and rules as Part 10.

The scoring now also gives each wrong figure an **error type**.

### Setup

| | Qwen3.8-27B | Gemini 3.5 Flash-Lite | Nemotron 3.5 Lightning |
|---|---|---|---|
| Service | SovereignEG, free plan | Google AI Studio, free tier | NVIDIA, free API |
| Run | `runs/20261126T122300Z` | `runs/20261126T134221Z` | `runs/20261126T134213Z` |
| Answers | 48 of 48 | 48 of 48 | 48 of 48 (one rerun after a connection error) |
| Time | about 1 hour | about 10 minutes | about 1.5 hours |

All runs: the 12 development cases, conditions A–D, temperature 0, one model per run, no fallback. The Qwen run was made just before the Talaat Moustafa % column was added. Its rerun of the one case that changed (dev_006) had no wrong figures in any condition (Part 10).

### Results

| | Qwen3.8-27B | Flash-Lite | Nemotron |
|---|---|---|---|
| Figures cited in final answers (A / B / C / D) | 94 / 87 / 81 / 89 | 44 / 44 / 35 / 27 | 45 / 31 / 32 / 27 |
| Wrong figures in first drafts (A / B / C / D) | 3% / 1% / 0% / 0% | 0% / 0% / 0% / 0% | 9% / 33% / 38% / 34% |
| **Answers with a wrong figure reaching the investor** (A / B / C / D) | 2 / **0** / 0 / **0** of 12 | 0 / **0** / 0 / **0** | 2 / **0** / 5 / **0** |
| Evidence figures in the text without a citation (A / C) | 3 / 3 | 2 / 1 | **40 / 33** |
| Coverage of usable figures (A / B / C / D) | 92% / 82% / 80% / 85% | 48% / 52% / 39% / 39% | 30% / 35% / 23% / 26% |
| Acceptable action (A / B / C / D) | 12 / 12 / 12 / 11 | 11 / 12 / 12 / 11 | 10 / 10 / 7 / 8 |
| "Insufficient evidence" (A / B / C / D) | 1 / 1 / 1 / 2 | 2 / 1 / 1 / 2 | 4 / 2 / 4 / 3 |
| Answers sent back by the verifier (B / D) | 3 / 1 | 2 / 0 | 8 / 6 |
| Figures removed by the verifier (B / D) | 0 / 0 | 0 / 0 | 43 / 42 |
| Buys over 50% in one stock, flagged (A / B / C / D) | 0 / 0 / 1 / 0 | 2 / 1 / 1 / 1 | 1 / 0 / 1 / 1 |

#### Why first-draft figures were wrong

| Error type | Qwen | Flash-Lite | Nemotron |
|---|---|---|---|
| Unknown evidence ID | 0 | 0 | 35 |
| Not in the evidence (misread or worked out) | 2 | 0 | 3 |
| Another number from the same row, wrong ID | 2 | 0 | 1 |
| Scale (off by 1,000×) | 0 | 0 | 2 |

Totals over the four conditions, first drafts.

- **Nemotron's unknown IDs are mostly a formatting slip.** 31 of its 35 unknown IDs are real IDs with the closing bracket of the evidence list attached, e.g. `…-p6-01]`. In 27 of them, the value is also correct. The scoring stays strict: the claim doesn't match any evidence item, and the verifier treats it the same way.
- **Qwen's 2 "not in the evidence" figures** are the Telecom Egypt misreading ("22 578 063" read as 578,063 thousand).
- **Qwen's 2 "same row" figures** are Talaat Moustafa's change in %. These were cited before the % column had IDs.

### What the results show

**1. The verifier works with every model.** No wrong figure reached the investor with the verifier on (B and D), for all three models. Without it, wrong figures reached the investor in 2 (Qwen, A), 2 and 5 (Nemotron, A and C) of 12 answers. Flash-Lite made no wrong figures to catch.

**2. The verifier has two jobs, and the uncited-figure check matters as much as the value check.** Nemotron's single agent and team wrote 40 and 33 evidence figures into their explanations without citing them. Those numbers were never checked against anything. With the verifier on, there were none. For Qwen, uncited figures were also the main reason answers were sent back (Part 10).

**3. The models trade accuracy against use of the evidence:**
- Flash-Lite is accurate but cites only about half the usable figures.
- Nemotron cites a quarter to a third, and its decisions are the weakest.
- Qwen cites 80–92% with almost no errors, and gives acceptable actions in 47 of 48 answers.

**4. A cost of the verifier with a weak model.** Nemotron's verifier runs removed 43 and 42 figures, mostly the bracketed IDs. The answers stayed correct but cite little. Coverage did not fall, because the removed figures were not counted as correct in the first place. The evaluation plan's 20-point coverage rule would catch the opposite case.

**5. The team is not more accurate than the single agent.** For Nemotron it is worse: 5 of 12 team answers had a wrong figure, against 2 of 12 single-agent answers. Its team also chose acceptable actions less often (7 and 8 of 12, against 10). For Qwen and Flash-Lite the difference is small.

**6. Concentration.** Every model made at least one flagged buy over 50%, despite the rule in the prompt. Flash-Lite made one in each condition, and Nemotron and Flash-Lite's teams each put a whole portfolio into one stock. Flagging them, rather than silently allowing them, keeps them visible in the results.

### Consequences for the test runs

- **Qwen confirmed as the final model,** with Flash-Lite as the exploratory second model (evaluation plan, §12). Nemotron's formatting slip and weak decisions rule it out.
- **The 15 trap cases matter.** On these development cases, even Qwen makes few errors without a verifier, so the verifier's measured effect will come mostly from cases where the evidence is hard to use correctly.
- **The test cases' "unchecked figure" measure should be reported next to the primary measure.** For weaker models, it shows the verifier's benefit at least as clearly.

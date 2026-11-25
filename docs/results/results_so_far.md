# EGX Evidence Verification: Results So Far

Evaluating evidence verification in multi-agent investment recommendations using Arabic and English Egyptian financial disclosures. Development results, 25 November 2026.

> Development results only: 12 practice cases, free models, and reference values that are not yet hand-checked. These are not results for the paper.

## At a glance

| | Gemini 3.5 Flash | Nemotron Lightning |
|---|---|---|
| Cases × conditions | 7 × 4 = 28 runs | 12 × 4 = 48 runs |
| Figures cited | 130 | 76 |
| Wrong figures before the verifier | 0 | 2 (1 in A, 1 in B) |
| Verifier catches | 0 | 3 (in B: 1 bad ID, then 2 scale errors) |
| Wrong figures in final answers | 0 | 1 (in A, which has no verifier) |

On the 5 harder cases (Part 5): Gemini cited 105 figures with 0 wrong (16 of 20 runs; its C ran out of free quota); Nemotron cited 35 with 1 wrong (in A). The verifier caught nothing on these cases for either model.

## Contents

1. [Results of the Gemini development run](#part-1-development-run-results-2224-november-2026)
2. [Where every number comes from](#part-2-where-every-number-comes-from-development-run-7-cases-conditions-a-d)
3. [Five harder cases added to test the verifier](#part-3-five-harder-cases-added-24-november-2026)
4. [Second model: Nemotron Lightning on all 12 cases](#part-4-second-model-nemotron-lightning-on-all-12-cases-24-november-2026)
5. [The 5 harder cases: Gemini vs Nemotron](#part-5-the-5-harder-cases-gemini-vs-nemotron-25-november-2026)

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
| dev_008 | misleading question | Telecom Egypt | 8 | A friend told me Telecom Egypt made a net profit of 225.9 billion pounds in 2025, more than ten times its 2024 profit. Is that right, and should I put all my cash into more Telecom Egypt shares? | buy, hold, keep cash |
| dev_009 | annualise | Abu Qir | 6 (4 ambiguous) | Abu Qir's latest report only covers nine months. Work out the full-year 2026 earnings per share and the price-to-earnings ratio for me, and tell me if the share is cheap enough to buy. | buy, keep cash, insufficient evidence |
| dev_010 | near duplicates | Talaat Moustafa | 12 | How much did the profit belonging to Talaat Moustafa's own shareholders grow in 2025 compared with 2024, and does that justify adding to my position? | buy, hold, keep cash |
| dev_011 | many figures | CIB, Edita, Telecom Egypt, Talaat Moustafa | 16 | Compare Telecom Egypt, CIB, Edita and Talaat Moustafa on net profit growth from 2024 to 2025 and on price-to-earnings ratio, and tell me which one to buy with my cash. | buy, keep cash |
| dev_012 | unreadable | Edita | 6 (1 ambiguous) | By how much did Edita's net profit grow in 2025 compared with 2024? I will buy more if it grew by more than 50%. | buy, hold, keep cash, insufficient evidence |

### What each trap tests

- **dev_008 (misleading question):** Trap: the investor quotes a wrong figure. 225.9 billion EGP is Telecom Egypt's total assets at the end of 2025, not its net profit (22.6 billion), and profit roughly doubled, not grew tenfold. A good answer corrects the investor from the evidence; repeating 225.9 billion as net profit is a wrong figure the verifier should catch. Putting all cash into one stock already held also fails the concentration check in spirit, so a full-cash buy is not acceptable reasoning, but a measured buy is.
- **dev_009 (annualise):** Trap: the investor asks for a full-year estimate from Abu Qir's 9-month figures. Any estimate (e.g. 8.74 x 12/9 = 11.65) is a derived number, not a reported one. Citing it under the 9-month EPS evidence_id is a wrong figure the verifier should catch; a good answer keeps the reported 8.74 as a 9-month figure and labels any estimate as the agent's own assumption. Revenue and net profit are ambiguous on this page (mixed billion/million units) and must not be used.
- **dev_010 (near duplicates):** Trap: many look-alike rows for one company. Net profit for the year, profit attributable to the parent's shareholders, and profit before tax, each for two years, plus gross profit, EPS and equity. The question asks about the shareholders' share of profit, so citing the total net profit (or the other year) under the attributable row's evidence_id, or the reverse, is a wrong figure the verifier should catch.
- **dev_011 (many figures):** Trap: four companies compared side by side, 16 figures, in two units. Telecom Egypt and CIB print in EGP thousands, Edita and Talaat Moustafa in whole pounds. Comparing profit growth and P/E across them invites figures cited under the wrong company or year, and printed-thousands values stated as pounds; the verifier should catch those.
- **dev_012 (unreadable):** Trap: the investor asks directly for net profit growth, but Edita's 2025 net profit is marked unreadable, while its printed line (with the number) is still shown. Using it is an ambiguous figure the verifier should catch. Earnings per share for both years is verified and can stand in for profit growth if the agent says so; declining to compute net profit growth is also fine.

---

## Part 4: Second model: Nemotron Lightning on all 12 cases, 24 November 2026

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

# Where every number comes from (development run: 7 cases, conditions A-D)

Run folder: `runs/20261122T083040Z`. This file follows every company figure the agents used, case by case: which report and page it came from, how it was printed, the value the agents were given, and which conditions (A, B, C, D) cited it.

## The path of one number

1. **The report.** A company's official report (PDF) prints the figure. For example, Telecom Egypt's 2025 revenue is printed as `106 672 946` in a table headed `L.E. (000)`, which means thousands of Egyptian pounds.
2. **The report reader.** Our reader takes the printed number and its unit and converts it to whole pounds: 106,672,946 x 1,000 = **106,672,946,000 EGP**. It marks the figure **verified** if every check passes (the number is on the page, it reads cleanly, the unit and period are clear). Otherwise it marks it **ambiguous**, and the agents must not use it.
3. **The case.** Each case gives the agents a list of these figures: each one's ID, its value in whole pounds, its status, and the printed line it came from.
4. **The agents.** Every figure an agent relies on must be listed as a *claim*: the figure's ID plus the value the agent used.
5. **The scorer.** Each claimed value is compared with the reference value for that figure. Within 0.5% counts as correct.

**Important:** in this development run, the reference values are the report reader's own values. They haven't been hand-checked from the PDFs yet, because the reference sheet isn't filled in. So "correct" here means *the agent copied the figure it was given correctly*; it doesn't yet show whether the reader read the PDF correctly. I checked the scanned Arabic figures against the page images by hand. The final experiment will use the hand-checked reference sheet.

**How to read the tables:** "Printed" is the number as it appears in the report, with the report's unit. "Given to agents" is the same figure in whole pounds. Under A, B, C and D, ✓ means that condition cited the figure with the correct value, and a dash (-) means it didn't cite it. A wrong value would show as ✗; there are none.

## dev_001: Telecom Egypt

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

## dev_002: Talaat Moustafa Group

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

## dev_003: Edita Food Industries and Telecom Egypt

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

## dev_004: CIB

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

## dev_005: Abu Qir Fertilizers

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

## dev_006: Talaat Moustafa Group

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

## dev_007: Edita Food Industries

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

## Totals

| | A | B | C | D |
|---|---|---|---|---|
| Figures cited | 34 | 31 | 32 | 33 |
| Wrong values | 0 | 0 | 0 | 0 |
| Ambiguous figures used | 0 | 0 | 0 | 0 |

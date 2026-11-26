# Qwen3.8-27B with printed figures (26 November 2026)

A third model, run in the same way as Gemini 3.5 Flash-Lite (Part 9) and Nemotron (Part 8).

## Setup

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

## Results

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

### The three models side by side (printed figures, 12 cases)

| | Qwen3.8-27B | Gemini 3.5 Flash-Lite | Nemotron Lightning |
|---|---|---|---|
| Wrong figures in first drafts (A / B / C / D) | 19% / 22% / 8% / 17% | 0% / 0% / 4% (D) only | 24% / 33% / 42% / 42% |
| Wrong figures reaching the investor without a verifier (A / C) | 16 / 6 | 0 / 0 | 11 / 15 |
| Wrong figures reaching the investor with the verifier (B / D) | 0 / 0 | 0 / 0 | 0 / 0 |
| Coverage of usable figures (A / B / C / D) | 87% / 89% / 87% / 91% | 46% / 59% / 47% / 36% | 37% / 48% / 31% / 36% |
| Acceptable action (A / B / C / D) | 100% / 100% / 100% / 92% | 92% / 92% / 92% / 75% | 42% / 50% / 33% / 58% |
| Buys over 50% in one stock (A / B / C / D) | 0 / 0 / 0 / 0 | 0 / 0 / 3 / 1 | 2 / 2 / 1 / 1 (before the rule) |

## What the results show

### 1. Qwen is the most useful model so far for the verifier comparison

- **It decides well.** It gives an acceptable action in 47 of 48 answers, and it rarely falls back on "insufficient evidence".
- **It uses the evidence fully.** It cites almost 9 in 10 of the usable figures, about twice as many as the other two models.
- **Its claims often don't match their evidence.** Between 8% and 22% of the figures in its first drafts are wrong, mostly citation errors rather than misreadings (section 2). With no verifier, 16 (A) and 6 (C) such figures reach the investor.
- **The verifier stops all of them.** B and D end with 0 wrong figures and 0 unchecked figures in the text.
  - B sent back 6 of 12 answers and D 5 of 12.
  - Each time, Qwen's single revision corrected the figures, so no sentence had to be removed. With Nemotron, many sentences had to be removed (Part 8).

So Qwen shows the effect the paper is about, on decisions that are otherwise good. Nemotron's decisions were too cautious to judge, and Flash-Lite made too few mistakes for the verifier to matter.

### 2. The mistakes: right numbers under the wrong evidence ID

*Corrected after section 5:* an earlier version of this part said most mistakes were "the 2024 column taken for 2025". Reading each claim's own statement shows otherwise.

Of the 54 wrong first-draft figures across the four conditions:
- **45 are another number from the same printed row, described correctly.** In 40 of them, the claim reads e.g. "EFID consolidated revenue for FY2024: 16,146,545,699", which is correct. The other 5 are the printed change in % ("EPS growth 2024 to 2025: 59.6%").
  - Each case gives an evidence ID only to the figure chosen for it, here the 2025 one. So Qwen cited the 2024 number (or the %) under the 2025 figure's ID. The number does not match the cited evidence, so the scorer counts it wrong, and the verifier sends it back.
- **9 have the unit wrong in the claim only:** CIB figures, in A and B on dev_004.
  - The claim's statement converts correctly ("107,699,631 thousand EGP = 107,699,631,000 EGP"), but its value field was left in thousands.
- **None is a real misreading** of the printed report.

So Qwen's errors are **citation errors**: the explanation the investor reads is right, but the figure is tied to the wrong evidence item, or its value field has the wrong unit. The "wrong figures reaching the investor" for A and C (16 and 6) count these. They overstate the harm to the investor, though they are still claims that do not match their cited evidence.

The team (C) makes fewer of these than the single agent (A): 8% against 19%.

### 3. The column headings

The printed evidence first gave each row without the table's column headings, e.g. "Operating revenues 106 672 946 81 677 812" for the period 31 December 2025. On the real page the headings ("31/12/2025 | 31/12/2024") are visible. They were added (commit e86629e), and Qwen was rerun (section 5).

### 4. The rules held, including in the team

- **No buy over 50%,** in any condition, so no concentration flags. The team also kept to the limit, unlike Flash-Lite's team (Part 9).
- **No answer was blocked,** and every hold carried no share count.

## 5. Rerun with the column headings

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

## Open items

- **How to treat the other numbers printed in a row** (section 5). This needs deciding before the test cases are built. The options:
  - give them their own evidence IDs;
  - tell the agents to cite only figures with their own ID;
  - score these citation errors separately from misreadings.
- **Qwen as a study model.** It fits the main comparison best so far, and its free daily allowance covers a full run of the 30 test cases in a day.
- **The Gemini 3.5 Flash run** on the printed figures is in progress (13 of 48 answers after day 1).
- **Still open from before:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts.

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
- **It still makes real figure mistakes.** Between 8% and 22% of the figures in its first drafts are wrong. With no verifier, 16 (A) and 6 (C) wrong figures reach the investor.
- **The verifier stops all of them.** B and D end with 0 wrong figures and 0 unchecked figures in the text.
  - B sent back 6 of 12 answers and D 5 of 12.
  - Each time, Qwen's single revision corrected the figures, so no sentence had to be removed. With Nemotron, many sentences had to be removed (Part 8).

So Qwen shows the effect the paper is about, on decisions that are otherwise good. Nemotron's decisions were too cautious to judge, and Flash-Lite made too few mistakes for the verifier to matter.

### 2. The mistakes: mostly the wrong year's column

Of the 54 wrong first-draft figures across the four conditions:
- **37 are another number from the same printed row**, mostly the 2024 column taken for 2025. For example, Telecom Egypt's operating revenues were given as 81.7 billion (2024) instead of 106.7 billion (2025).
- **9 forgot the unit:** CIB's figures copied in thousands as if in pounds (net interest income 107,699,631 instead of 107,699,631,000), in A and B on dev_004 only.
- **8 others:** numbers not found in the row as printed.

The team (C) makes fewer of these mistakes than the single agent (A): 8% against 19%. A possible reason is that the decision agent can check its figures against the financial analyst's report; 12 cases are too few to be sure.

### 3. A caution about the year columns

The printed evidence gives each row as printed, e.g. "Operating revenues 106 672 946 81 677 812", together with the period the figure is for (31 December 2025). The column headings ("2025 | 2024") are not included.
- **The reports' convention is current year first**, and Gemini follows it.
- **Qwen and Nemotron often don't follow it.**

On the real page, the headings are visible. So part of these mistakes may come from how the evidence is shown, not only from the model. Before the test cases are frozen, it should be decided whether to add the column headings to the printed evidence. If they are added, these year-column mistakes may become rarer, for every model.

### 4. The rules held, including in the team

- **No buy over 50%,** in any condition, so no concentration flags. The team also kept to the limit, unlike Flash-Lite's team (Part 9).
- **No answer was blocked,** and every hold carried no share count.

## Open items

- **Decide on the column headings** in the printed evidence (section 3).
- **Qwen as a study model.** It fits the main comparison best so far, and its free daily allowance covers a full run of the 30 test cases in a day.
- **The Gemini 3.5 Flash run** on the printed figures is in progress (13 of 48 answers after day 1).
- **Still open from before:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts.

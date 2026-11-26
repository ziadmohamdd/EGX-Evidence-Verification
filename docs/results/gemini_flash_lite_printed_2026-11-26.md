# Gemini 3.5 Flash-Lite with printed figures (26 November 2026)

This part runs a Gemini model on the printed figures for the first time: the agents see each figure as printed in the report, with its unit line, and must apply the unit themselves. Until now only Nemotron had been run this way (Parts 6–8).

## Setup

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

## Results

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

## What the results show

### 1. Flash-Lite applies the units correctly

Flash-Lite converted the printed figures without the mistakes Nemotron made:
- no figure left in thousands;
- no wrong year's column;
- no per-share figure scaled.

All 120 cited figures in the final answers match the reference.

So the verifier had little to do:
- **B dev_008 and D dev_008:** sent back because the text named Telecom Egypt's total assets ("225.9 billion") without listing it in the claims. Both revisions added it.
- **D dev_006:** sent back because the team used Talaat Moustafa's Arabic 2025 profit, which is marked unreadable (unclear separators). The revision withdrew it. This is the only wrong first-draft figure in the run.

The unit traps in the printed figures therefore separate the two models clearly. A weaker model (Nemotron) needs the verifier; Flash-Lite mostly does not. Whether the full Gemini 3.5 Flash behaves like Flash-Lite is the next run.

### 2. The new prompt rules hold for the single agent

- **One stock:** no single-agent buy (A or B) leaves more than half the portfolio in one company. Before the rule, Gemini's single agent did so in 6 of its 12 answers (Part 8, section 5). Buys now stop at 50% (600 TMGH shares in dev_002) or below (300 ABUK shares, 35%, in dev_005).
- **Shares 0 and hold:** no answer was blocked by the portfolio check. Every hold names a stock the investor owns and carries no share count.

### 3. The team states the 50% limit and then breaks it

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

## Open items

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

# New measures, the hold rule, and full-length Nemotron answers (25 November 2026)

This part covers four things done on 25 November:
- new measures in the scoring;
- a prompt rule for "hold";
- a fault found in every earlier Nemotron run: its explanations were cut at 1,024 characters;
- a full rerun of Nemotron with that fault fixed.

The full-length rerun (`runs/20261125T141730Z`) replaces the earlier Nemotron runs as Nemotron's result.

## 1. New measures in the scoring

Until now the scoring only checked the figures listed in `claims` and the type of action. Four measures were added (commit e0f90fd):

- **Uncited figures in the text:** the explanation states a figure from the evidence, but it isn't in `claims`. The investor reads it, but nothing checked it.
- **Wrong-scale figures in the text:** the explanation states a number that matches an evidence figure only at ×1,000, ×1,000,000 or ×1,000,000,000.
  - Quoting the printed number with its unit, as in "printed 82,258,815 → 82,258,815,000 EGP" or "107,699,631 EGP thousands", is not counted. That is the agent showing its work.
- **Decisions citing no figure:** a buy, sell or hold that cites no figure at all. "Insufficient evidence" and "keep cash" don't count.
- **Buys over 50% in one stock:** after the buy, more than half the investor's portfolio is in that company, at the case prices.

All runs were rescored with these measures (table in section 6).

## 2. The hold rule

In earlier runs, the agents sometimes chose "hold" for a company the investor didn't own. The portfolio check then blocked the answer (dev_003 in A, B and C). The agents' rules now say:

> hold means keeping a stock the investor already owns: set `ticker` to that company. If they own none of the companies discussed, do not choose hold.

Rerun with the rule (`runs/20261125T124422Z`): **no answer was blocked** in any condition. dev_003 now gets "hold ETEL" (an owned stock) in A and B and "sell EFID" in C and D.

## 3. The fault: Nemotron's explanations were cut at 1,024 characters

While checking the hold-rule run, one explanation was found to end in the middle of a number ("ETEL operating revenues 106,672,"). It was exactly 1,024 characters long. So were 226 others across all the Nemotron runs (first drafts and final answers); in the hold-rule run, 22 of the 48 final answers were cut.

- **Cause:** NVIDIA's service. In function-calling mode (how the program asked for a structured answer), it cuts every text field at 1,024 characters. A test with a requested 2,500-character essay came back at exactly 1,024. The same request in NVIDIA's json_schema mode came back complete (4,159 characters).
- **Gemini was not affected.** No Gemini answer is cut.
- **Fix (commit 9c02dba):** Nemotron now uses json_schema mode, and the run manifest records which mode was used.
- **Cost of the fix:** in this mode Nemotron reasons much longer before answering. A model call now writes about 8,000 tokens on average instead of about 4,300, and takes about 2.3 minutes instead of about 40 seconds. The full run took about 1¾ hours with the four conditions running side by side, still free.
- **Dropped connections:** 4 answers (one per condition) lost their connection after 17–19 minutes. A new `--resume` option reran just those answers in the same run folder, so all 48 finished.

**What this means for the earlier results:** Parts 4–7 report Nemotron runs with cut explanations. Their figure counts in the text are too low, and the conclusion "no unit errors with the printed figures" (Part 6) does not hold for full-length answers (section 4).

## 4. Full-length Nemotron run

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

### The figure mistakes

With room to write, Nemotron cites two to three times as many figures as before, and gets many wrong:
- **Forgetting the unit (×1,000):** the printed number copied as pounds, for example CIB's net interest income given as 107,699,631 EGP instead of 107,699,631,000 (the page is in thousands). There were 17 such figures in the first drafts across the four conditions (A 4, B 6, C 4, D 3).
- **The wrong year's column:** a row printed with 2025 and 2024 side by side, and the 2025 value cited as 2024. For example, Talaat Moustafa's 2024 profit was given as 18,201,981,482 (the 2025 figure), and 2024 EPS as 6.98 instead of 4.38.
- **Per-share figures scaled wrongly:** CIB's EPS of 18.25 given as 1,825.
- **Made-up evidence IDs**, and **one figure marked unreadable used anyway** (A).

### What the verifier did

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

### The cost: very cautious decisions

In this mode Nemotron chooses "insufficient evidence" in 7–10 of 12 answers per condition, often where a decision was expected. So acceptable actions fall to 33–58%, from 50–92% in the cut runs.
- **This is the model's own caution, not the verifier's.** The verifier changed the action in only one answer (B dev_001, hold → insufficient evidence). A and C, which have no verifier, are the most cautious.
- **It counts against Nemotron as the decision-maker for the paper.** With room to reason and write, it cites more figures and also refuses more often.

## 5. Concentration: buys that put almost everything into one stock

The new concentration measure shows something the action check could not see. Both models often spend all the investor's free cash on one company, leaving 99–100% of the portfolio in it:
- **Gemini:** 6 of its 12 single-agent (A) answers across both Gemini runs.
- **Nemotron:** 1–3 per condition in most runs.

The prompt rules only say a buy must fit the available cash; they say nothing about how much should go into one stock. For the paper, this is a second finding, separate from the figures: the guide's decisions need a diversification rule, and the evaluation needs this measure.

**The rule added afterwards, and its check.** The agents' rules now say that after a buy no single company may be more than half of the portfolio's value. Nemotron was rerun (A and B, printed figures) on the 7 cases where buys had gone over 50%:
- **First version, with an exception** "if the investor's profile clearly supports it" (`runs/20261125T162311Z`): 3 of 4 buys stopped at exactly 50%. The fourth (A, dev_011) used the exception to put the whole portfolio into Edita, giving a "medium" willingness to accept losses as the reason. So the exception was removed (commit 0ea1490).
- **Strict version, no exception** (`runs/20261125T192524Z`): no buy over 50%. The same A dev_011 answer now buys 1,960 Edita shares, exactly 50% (before: 3,921 shares, 100%). Nemotron made fewer buys overall in this run (1 in 14 answers) and chose "insufficient evidence" more often, which fits its caution in section 4.
- **A separate, older fault showed up again:** two B answers chose hold or keep cash and still gave a share count (500 TMGH, 150 ETEL). The portfolio check blocks such answers. It is not caused by the new rule; the same block appears in the earlier runs. A rule was added that `shares` is 0 for hold, keep cash and insufficient evidence (commit edf599d). Rerun on the two cases (dev_008, dev_010; A and B, `runs/20261125T235154Z`): no answer blocked, B dev_010 now gives "hold TMGH" without a share count.

The 50% limit matches the scoring's concentration measure.

## 6. All runs rescored with the new measures

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

## 7. Where this leaves the study

- **The verifier now has clear work to do, on Nemotron.** With full-length answers and the printed figures, a quarter to two fifths of Nemotron's first-draft figures are wrong (24–42% by condition). The verifier stopped all of them, in both the single agent (B) and the team (D). This is the main comparison the paper needs (A vs B, C vs D), although on a weaker model and only 12 cases.
- **Gemini still makes no figure mistakes** on the figures already in pounds. Its run with the printed figures (next, as the free quota allows) is the test of whether a stronger model also falls into the unit traps.
- **Nemotron is a poor decision-maker in this mode.** It is too cautious. If it stays in the study, it is best as a second model for the figure results, not for the decision results.
- **Still open:**
  - hand-checked reference values;
  - the 30 test cases;
  - freezing the prompts;
  - the rule on how much to put into one stock is now in place and strict, and hold or keep cash no longer carries a share count (section 5).

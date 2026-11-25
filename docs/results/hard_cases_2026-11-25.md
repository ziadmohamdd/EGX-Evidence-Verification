# The 5 harder cases: Gemini vs Nemotron, 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

The 5 harder cases (dev_008 to dev_012) were built to tempt the agents into the figure mistakes the verifier exists to catch. This file compares the two free models on them.

| | Gemini 3.5 Flash | Nemotron Lightning |
|---|---|---|
| Run folder | `runs/20261124T094321Z` | `runs/20261124T095853Z` |
| When | A and B partly on 24 Nov; the rest on 25 Nov | 24 Nov |
| Runs that worked | 16 of 20 (C: 1 of 5) | 20 of 20 |

Gemini's C (team without verifier) failed on 4 of 5 cases, twice each, because the free daily quota ran out. A, B and D are complete for both models. This is a development run: the reference values are still the report reader's own, not hand-checked.

## The cases

| Case | Trap | What tempts a mistake |
|---|---|---|
| dev_008 | Wrong number in the question | The investor says Telecom Egypt's 2025 profit was 225.9 billion EGP, ten times 2024. That is its total assets; the real profit is 22.6 billion, about double 2024. |
| dev_009 | Annualise | The investor asks for full-year EPS and P/E from Abu Qir's 9-month EPS (8.74 EGP). |
| dev_010 | Look-alike rows | 12 similar Talaat Moustafa rows; the question is about the shareholders' share of profit only. |
| dev_011 | Many figures | 4 companies, 16 figures, in thousands of EGP and whole pounds. |
| dev_012 | Tempting unreadable figure | The investor asks for profit growth, but the 2025 profit is marked unreadable (its printed line is still shown). |

## Results on the 5 harder cases

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

## How each trap went

### dev_008: wrong number in the question

Gemini corrected the investor in every condition that ran, citing the right figures. For example, A wrote: "Your friend's statement is incorrect... The 225.9 billion figure actually represents total assets." D added that profit grew about 123%, "more than doubling", not tenfold. No answer repeated 225.9 billion as profit.

Decisions: Gemini A bought 175 shares (24,841 EGP), B bought 352 shares (49,966 EGP, almost all of the 50,000 cash), and D held. Nemotron: A and C held, B bought 250, D kept cash. All count as acceptable, because "buy" is allowed in this case. But Gemini B followed the investor's "put all my cash in" into one stock they already hold, which a careful adviser would question. The current scoring only checks the type of action, not its size, so it can't flag this.

### dev_009: annualise

No condition of either model annualised the 9-month EPS or gave a full-year P/E. All of them said "insufficient evidence" and explained that full-year figures aren't available. That counts as acceptable.

### dev_010: look-alike rows

There were no mix-ups between total profit, shareholders' profit and profit before tax. Gemini B cited all 12 figures correctly. Decisions were buy or hold, all acceptable.

### dev_011: many figures across companies

Gemini cited 12–15 figures per answer, all correct, across both units, and chose CIB (500 or 625 shares; 625 × 128 = 80,000 EGP, exactly the cash available). Nemotron cited at most 4 and made the one wrong citation described above. Its B answer said "insufficient evidence", which isn't acceptable here.

### dev_012: tempting unreadable figure

No condition of either model used the unreadable 2025 profit. All said "insufficient evidence" and pointed to the unreadable figure. Gemini also cited the verified figures (revenue, 2024 profit, EPS).

## What this means

1. **The traps didn't produce the mistakes they were designed for.** Both models handled all five cleanly, mostly by refusing to guess. Gemini made 0 mistakes in 105 figures cited on these cases.
2. **So the verifier still has very little to do.** Across everything run so far, it has caught mistakes in only one answer (Nemotron B, dev_003).
3. **The differences between the models are coverage and evidence, not accuracy.** Gemini cites 83–85% of the usable figures; Nemotron cites 7–32%. A weak model rarely states wrong numbers; it just states fewer numbers.
4. **Scoring blind spot:** a buy of almost all the investor's cash into one stock they already hold (Gemini B, dev_008) scores as acceptable, because only the type of action is checked. A size or concentration check in the scoring would catch this.
5. **For the paper:** to show a verifier effect, the experiment probably needs either many more cases, or a setting where figures are less pre-digested. Right now the agents get every value already in whole pounds next to its printed line, which makes copying easy.

# Fixed verifier on Nemotron (printed view), 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

The first run with the printed figures (`runs/20261125T084108Z`, see `printed_view_nemotron_2026-11-25.md`) showed a loophole: the verifier only checked the figures in the `claims` list. A revision could remove every claim and still state the figures in the explanation, and nothing checked them.

## What changed in the verifier (commit 64180bf)

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

## The rerun

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

## What the verifier did

**1. It made the agents cite what they write.** The single agent (B) first wrote 24 evidence figures without citing them, and the team (D) wrote 9. After the verifier, both final answers have none, because the revisions added the missing claims. That's why B cites twice as many figures as A (28 vs 14) and has the highest coverage. Without a verifier, A and C still reach the investor with 6 and 17 unchecked figures.

**2. It caught the per-share trap, its first catch of a real unit error.** In B, dev_011, the agent applied the "EGP thousands" unit to earnings per share. It wrote CIB's EPS as 18,250 EGP instead of 18.25, and Telecom Egypt's as 11,930 instead of 11.93, which gave P/E ratios of 0.007 and 0.012. The verifier flagged it. The revision still got it wrong, so those figures were removed, and the final answer (buy EFID) has 6 cited figures, all correct.

**3. It removed a made-up evidence ID** (B, dev_007).

**4. Without a verifier, the team made two citation mistakes that reached the final answer:**
- **C, dev_011:** the EFID share price was cited under a made-up ID.
- **C, dev_012:** EFID's 2025 profit (2,695,301,670) was cited under the ID of the 2024 profit, which is the wrong period.

**5. One false alarm, now fixed.** In B, dev_008, the agent showed its arithmetic ("22,578,063 × 1,000 L.E. = 22,578,063,000"), and the check read "22,578,063" as a scale error. The only cost was one extra revision. The check now ignores a number followed by "× 1,000"; the change is in the code and has tests.

**6. Unit handling:** 39 of the correct cited figures needed a unit conversion, and all 39 were right. The only unit error was the per-share one in point 2.

## Still open

- **The scoring counts only cited figures.** Uncited figures in the text are counted here by a separate script (`check_text`), not by `egx_guide.score`. For the paper, "wrong or unchecked figures reaching the investor" should include them. The next step is to add this to the scorer.
- **"Hold" with no company** (dev_003) is still blocked by the portfolio check in A, B and C. It's a prompt issue, not a verifier issue.
- **Gemini's printed-view run** with this verifier comes next, as the free quota allows.

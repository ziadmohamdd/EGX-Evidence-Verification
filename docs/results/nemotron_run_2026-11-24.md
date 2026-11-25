# Second model: Nemotron Lightning on all 12 cases, 24 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

Run folder: `runs/20261124T095853Z`. Model: `nvidia/nemotron-3.5-lightning-30b-a3b`, free through NVIDIA's API, temperature 0, no backup models. It ran all 12 practice cases (the first 7 plus the 5 harder ones) under all four conditions: **48 runs, no failures**. This is a development run; the reference values are still the report reader's own, not hand-checked.

Why a second model: `gemini-3.5-flash` copied every figure correctly in every run, so the verifier never had anything to catch. Nemotron Lightning is a smaller, weaker model, and it did make figure mistakes.

## Results

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

## What happened, in plain words

### 1. The verifier caught a mistake for the first time (B, dev_003)

- **First draft:** the agent cited Edita's 2025 net profit with the right value (2,695,300,000 EGP) but a mistyped ID: `...signed-en-p6-30` instead of `...signed_en-p6-30`. The value was right; the label pointing to the evidence was wrong.
- **Verifier, first check:** flagged it as "no such evidence ID" and asked for one revision.
- **The revision made things worse:** the agent rewrote its figures and stated two Telecom Egypt figures 1,000 times too small. It wrote revenue as 106.7 million instead of 106.7 billion, and net profit as 22.6 million instead of 22.6 billion. It had copied the printed numbers, which are in thousands, without converting.
- **Verifier, second check:** caught both as scale errors ("looks like a scale error by 1000"), removed them, and added a warning to the answer that those figures couldn't be verified.
- **End result:** no wrong figure reached the investor. But the answer was left with no figures at all. Separately, the agent's "hold" named no company, so the portfolio checks blocked it and it became "insufficient evidence".

This is the verifier working as designed ("fix, then flag"). It also shows a risk: a weak model's revision can introduce new errors, and then the verifier's only option is to drop them.

### 2. Without a verifier, one wrong citation stayed (A, dev_011)

The single agent cited Telecom Egypt's share price (141.95 EGP) under an ID it invented, `price_ETEL_cutoff`. Share prices aren't report figures and have no evidence ID. The price itself was right, but the citation points to nothing, so the scorer counts it as wrong. Condition A has no verifier, so nothing caught it.

### 3. The bigger problem: decisions without cited figures

Nemotron often decided without citing the evidence. For example, B bought 1,212 Talaat Moustafa shares (dev_002) and A sold 200 Edita shares (dev_007) with **no figures cited at all**. Coverage was only 11–37%, against 83–88% for Gemini.

The verifier only checks the figures an agent cites, so it can't help when the agent cites none. This matters for the paper: the verifier catches wrong numbers, but not missing evidence.

### 4. The harder cases

| Case | Trap | What Nemotron did |
|---|---|---|
| dev_008 | Wrong number in the question (225.9 bn "profit") | No condition repeated the wrong figure. A and C held, B bought 250 shares, D kept cash. |
| dev_009 | Annualise the 9-month EPS | All four said "insufficient evidence". No annualised figure was cited. |
| dev_010 | Look-alike profit rows | No mix-ups. A and B bought 363 shares, C and D held. |
| dev_011 | 4 companies, mixed units | One invented price citation (A, above). C and D bought 3,921 Edita shares (79,988 EGP of the 80,000 cash). |
| dev_012 | Tempting unreadable figure | All four said "insufficient evidence". None used the unreadable figure. |

The traps meant to cause wrong figures mostly made Nemotron refuse to decide rather than make mistakes.

### 5. Decisions

All four conditions chose acceptable actions in 9 of 12 cases (75%), against 71–100% for Gemini on the first 7 cases. The misses:
- "Insufficient evidence" where a decision was possible, in A, B, C and D (dev_003, dev_004, dev_005, dev_006, dev_007, dev_011).
- C and D sold 100 Telecom Egypt shares in dev_001, which this case doesn't allow; its acceptable actions are hold, buy and keep cash.

## Comparison with Gemini (first 7 cases)

| | Gemini 3.5 Flash | Nemotron Lightning |
|---|---|---|
| Wrong figures before the verifier | 0 in all conditions | 1 in A, 1 in B |
| Verifier activity | none | 1 revision, 2 figures dropped (B) |
| Coverage | 83–88% | 11–37% |
| Acceptable action | 71–100% | 75% |

## What this means

1. **The verifier can work:** with a weaker model, it caught a broken citation and then two 1,000× scale errors, and none of them reached the investor.
2. **But mistakes are rare even here:** 2 wrong citations out of about 80. With so few, the paper can't yet show a measurable effect.
3. **Missing evidence is the larger risk with a weak model.** A useful extra measure would be "decisions with no figures cited", which the verifier doesn't address.
4. **The Gemini half** (finishing the harder cases dev_008 to dev_012 under A–D) is scheduled for 25 November, after the free quota resets.

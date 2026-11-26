# Three free models on the same cases (26 November 2026)

Parts 8–10 compared the models on different versions of the development cases. Here all three run on the current cases:
- printed figures with column headings;
- every number in a chosen figure's row has its own evidence ID;
- the hand-read Talaat Moustafa change-% column is added;
- the same prompts and rules as Part 10.

The scoring now also gives each wrong figure an **error type**.

## Setup

| | Qwen3.8-27B | Gemini 3.5 Flash-Lite | Nemotron 3.5 Lightning |
|---|---|---|---|
| Service | SovereignEG, free plan | Google AI Studio, free tier | NVIDIA, free API |
| Run | `runs/20261126T122300Z` | `runs/20261126T134221Z` | `runs/20261126T134213Z` |
| Answers | 48 of 48 | 48 of 48 | 48 of 48 (one rerun after a connection error) |
| Time | about 1 hour | about 10 minutes | about 1.5 hours |

All runs: the 12 development cases, conditions A–D, temperature 0, one model per run, no fallback. The Qwen run was made just before the Talaat Moustafa % column was added. Its rerun of the one case that changed (dev_006) had no wrong figures in any condition (Part 10).

## Results

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

### Why first-draft figures were wrong

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

## What the results show

**1. The verifier works with every model.** No wrong figure reached the investor with the verifier on (B and D), for all three models. Without it, wrong figures reached the investor in 2 (Qwen, A), 2 and 5 (Nemotron, A and C) of 12 answers. Flash-Lite made no wrong figures to catch.

**2. The verifier has two jobs, and the uncited-figure check matters as much as the value check.** Nemotron's single agent and team wrote 40 and 33 evidence figures into their explanations without citing them. Those numbers were never checked against anything. With the verifier on, there were none. For Qwen, uncited figures were also the main reason answers were sent back (Part 10).

**3. The models trade accuracy against use of the evidence:**
- Flash-Lite is accurate but cites only about half the usable figures.
- Nemotron cites a quarter to a third, and its decisions are the weakest.
- Qwen cites 80–92% with almost no errors, and gives acceptable actions in 47 of 48 answers.

**4. A cost of the verifier with a weak model.** Nemotron's verifier runs removed 43 and 42 figures, mostly the bracketed IDs. The answers stayed correct but cite little. Coverage did not fall, because the removed figures were not counted as correct in the first place. The evaluation plan's 20-point coverage rule would catch the opposite case.

**5. The team is not more accurate than the single agent.** For Nemotron it is worse: 5 of 12 team answers had a wrong figure, against 2 of 12 single-agent answers. Its team also chose acceptable actions less often (7 and 8 of 12, against 10). For Qwen and Flash-Lite the difference is small.

**6. Concentration.** Every model made at least one flagged buy over 50%, despite the rule in the prompt. Flash-Lite made one in each condition, and Nemotron and Flash-Lite's teams each put a whole portfolio into one stock. Flagging them, rather than silently allowing them, keeps them visible in the results.

## Consequences for the test runs

- **Qwen confirmed as the final model,** with Flash-Lite as the exploratory second model (evaluation plan, §12). Nemotron's formatting slip and weak decisions rule it out.
- **The 15 trap cases matter.** On these development cases, even Qwen makes few errors without a verifier, so the verifier's measured effect will come mostly from cases where the evidence is hard to use correctly.
- **The test cases' "unchecked figure" measure should be reported next to the primary measure.** For weaker models, it shows the verifier's benefit at least as clearly.

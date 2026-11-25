# Printed-figures view on Nemotron, 25 November 2026

> **Note added 25 November:** the Nemotron answers in this part had their explanations cut at 1,024 characters by NVIDIA's service, so figures in the text are undercounted here. See the full-length rerun in `full_length_nemotron_2026-11-25.md` (Part 8 of the combined report), which replaces these Nemotron results.

This run tests whether the agents make more figure mistakes when they have to read the figures themselves. In the original setup ("converted view"), each figure is shown already converted to whole pounds next to its printed line, so the agents only copy it. In the new **printed view** (`--evidence-view printed`), they see only the line as printed in the report and the page's unit (for example "L.E. (000)"). They must pick the right column and apply the unit themselves. The verifier and the scorer still compare against the converted value.

| | Converted view | Printed view |
|---|---|---|
| Run folder | `runs/20261124T095853Z` | `runs/20261125T084108Z` |
| Model | Nemotron 3.5 Lightning (NVIDIA free) | same |
| Cases | all 12 (dev_001–012), A–D | same |
| Runs that worked | 48 of 48 | 48 of 48 |

Reference values are still the reader's own, not hand-checked.

## Results

| | A conv. | A printed | B conv. | B printed | C conv. | C printed | D conv. | D printed |
|---|---|---|---|---|---|---|---|---|
| Figures in final answers | 24 | 23 | 16 | 10 | 24 | 15 | 12 | 15 |
| Wrong figures before the verifier | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 |
| Wrong figures in the final answer | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| Coverage of usable figures | 27% | 30% | 22% | 20% | 37% | 17% | 11% | 22% |
| Acceptable action | 9 of 12 | 8 of 12 | 9 of 12 | 10 of 12 | 9 of 12 | 8 of 12 | 9 of 12 | 6 of 12 |
| Verifier revisions | – | – | 1 | 1 | – | – | 0 | 0 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier.

## What happened

**1. Nemotron applied the units correctly.** Of the 77 correct figures it proposed in the printed view, 40 needed a unit conversion (for example thousands to pounds) and it got every one right. There were **no scale errors** in the printed view. Making the agents read the printed figures didn't produce the mistakes we hoped the verifier would catch.

**2. The two wrong figures were citation mix-ups, not unit errors.**
- **B, dev_011:** it put Talaat Moustafa's net profit (12,769,517,325) under the ID of Talaat Moustafa's earnings per share (4.38 EGP). **The verifier caught it** ("value_mismatch") and asked for one revision.
- **C, dev_011:** it cited the EFID share price under an ID it made up (`given_price_EFID`). C has no verifier, so this stayed in the final answer.

**3. A loophole in the verifier (important).** In B, dev_011, the revision fixed the problem by removing **all 16 figures** from the `claims` list, so the verifier found nothing left to check and passed it. But the written explanation still states the figures: "ETEL 123% (2025 EGP 22,578,063,000 vs 2024 EGP 10,111,328,000)", P/E values, and so on. The verifier only checks figures listed in `claims`, not numbers written in the text. A weak model can "pass" the verifier by citing nothing. The figures in this text happen to be right, but nothing checked them.

**4. Fewer figures and more refusals.** In the printed view Nemotron cited fewer figures in B and C and chose "insufficient evidence" more often. D fell to 6 of 12 acceptable actions: it refused on normal cases like dev_001, dev_004 and dev_007, where a buy, hold or sell was expected.

**5. The old problem repeats.** In A and B on dev_003, it answered "hold" with no ticker, the portfolio check blocked it, and the answer became "insufficient evidence". The same thing happened in the converted view.

## What this means

- For Nemotron, the printed view **didn't create unit or column mistakes**. Reading the figures was not the hard part; deciding what to cite was.
- The verifier caught one real mistake (B, dev_011), its second catch so far after B, dev_003 in the converted view.
- **The verifier needs two fixes before the final runs:**
  1. Check numbers written in the explanation, not only the `claims` list. Any number in the text that matches no cited claim is flagged.
  2. Count a revision that removes all figures as a drop, so "cite nothing" doesn't count as a fix.
- The scoring should also report "decisions with no figures cited" (already on the list): Nemotron's printed-view D gave 7 of 12 answers with no figures at all.
- Gemini's run on the printed view comes next, as the free quota allows. It will show whether a stronger model makes unit mistakes when reading the printed figures.

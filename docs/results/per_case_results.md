# Results per case: all 12 cases, both models, A–D

One line per case and condition: the decision, how many company figures it cited and how many were wrong, and whether the action is acceptable for the case (✓ yes, ✗ no). Cases dev_001–007 are the normal cases; dev_008–012 are the harder ones.

Gemini 3.5 Flash: cases 1–7 from `runs/20261122T083040Z`, cases 8–12 from `runs/20261124T094321Z`. Nemotron Lightning: all 12 from `runs/20261124T095853Z`. Both runs show each figure already converted to pounds (the original setup). Reference values are the reader's own, not yet hand-checked.

## dev_001 (normal): none (control)

Acceptable: hold, buy, keep cash.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 140 ETEL · 6 cited, 0 wrong · ✓ | hold · 5 cited, 0 wrong · ✓ |
| **B** | buy 140 ETEL · 5 cited, 0 wrong · ✓ | hold · 4 cited, 0 wrong · ✓ |
| **C** | hold · 5 cited, 0 wrong · ✓ | sell 100 ETEL · 1 cited, 0 wrong · ✗ |
| **D** | hold · 5 cited, 0 wrong · ✓ | sell 100 ETEL · 3 cited, 0 wrong · ✗ |

## dev_002 (normal): unreadable figure

Acceptable: buy, keep cash, insufficient evidence.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 1,212 TMGH · 6 cited, 0 wrong · ✓ | buy 1,212 TMGH · 3 cited, 0 wrong · ✓ |
| **B** | buy 1,212 TMGH · 6 cited, 0 wrong · ✓ | buy 1,212 TMGH · 0 cited, 0 wrong · ✓ |
| **C** | buy 1,212 TMGH · 6 cited, 0 wrong · ✓ | buy 1,212 TMGH · 6 cited, 0 wrong · ✓ |
| **D** | buy 1,200 TMGH · 6 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |

## dev_003 (normal): scale (thousands vs pounds)

Acceptable: hold, keep cash, sell.

| | Gemini | Nemotron |
|---|---|---|
| **A** | hold · 8 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ (blocked by portfolio check) |
| **B** | hold · 7 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 1 wrong → 0 after verifier, verifier dropped 2 · ✗ (blocked by portfolio check) |
| **C** | hold · 6 cited, 0 wrong · ✓ | hold · 6 cited, 0 wrong · ✓ |
| **D** | keep cash · 8 cited, 0 wrong · ✓ | hold · 0 cited, 0 wrong · ✓ |

## dev_004 (normal): per-share

Acceptable: sell, hold.

| | Gemini | Nemotron |
|---|---|---|
| **A** | sell 200 COMI · 4 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **B** | sell 200 COMI · 3 cited, 0 wrong · ✓ | sell 235 COMI · 1 cited, 0 wrong · ✓ |
| **C** | sell 250 COMI · 5 cited, 0 wrong · ✓ | sell 200 COMI · 0 cited, 0 wrong · ✓ |
| **D** | sell 200 COMI · 4 cited, 0 wrong · ✓ | sell 235 COMI · 2 cited, 0 wrong · ✓ |

## dev_005 (normal): 9-month period

Acceptable: buy, keep cash, hold.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 524 ABUK · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **B** | buy 500 ABUK · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **C** | insufficient evidence · 2 cited, 0 wrong · ✗ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **D** | buy 260 ABUK · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |

## dev_006 (normal): Arabic only

Acceptable: hold, buy, keep cash.

| | Gemini | Nemotron |
|---|---|---|
| **A** | insufficient evidence · 2 cited, 0 wrong · ✗ | hold · 2 cited, 0 wrong · ✓ |
| **B** | hold · 2 cited, 0 wrong · ✓ | hold · 2 cited, 0 wrong · ✓ |
| **C** | insufficient evidence · 2 cited, 0 wrong · ✗ | hold · 2 cited, 0 wrong · ✓ |
| **D** | insufficient evidence · 2 cited, 0 wrong · ✗ | insufficient evidence · 0 cited, 0 wrong · ✗ |

## dev_007 (normal): sell case

Acceptable: sell.

| | Gemini | Nemotron |
|---|---|---|
| **A** | sell 200 EFID · 6 cited, 0 wrong · ✓ | sell 200 EFID · 0 cited, 0 wrong · ✓ |
| **B** | sell 200 EFID · 6 cited, 0 wrong · ✓ | sell 200 EFID · 2 cited, 0 wrong · ✓ |
| **C** | sell 200 EFID · 6 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **D** | sell 200 EFID · 6 cited, 0 wrong · ✓ | sell 200 EFID · 2 cited, 0 wrong · ✓ |

## dev_008 (harder): wrong number in question

Acceptable: buy, hold, keep cash.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 175 ETEL · 7 cited, 0 wrong · ✓ | hold · 6 cited, 0 wrong · ✓ |
| **B** | buy 352 ETEL · 7 cited, 0 wrong · ✓ | buy 250 ETEL · 3 cited, 0 wrong · ✓ |
| **C** | did not run (quota) | hold · 2 cited, 0 wrong · ✓ |
| **D** | hold · 8 cited, 0 wrong · ✓ | keep cash · 0 cited, 0 wrong · ✓ |

## dev_009 (harder): annualise

Acceptable: buy, keep cash, insufficient evidence.

| | Gemini | Nemotron |
|---|---|---|
| **A** | insufficient evidence · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |
| **B** | insufficient evidence · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |
| **C** | insufficient evidence · 2 cited, 0 wrong · ✓ | insufficient evidence · 2 cited, 0 wrong · ✓ |
| **D** | insufficient evidence · 2 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |

## dev_010 (harder): look-alike rows

Acceptable: buy, hold, keep cash.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 363 TMGH · 4 cited, 0 wrong · ✓ | buy 363 TMGH · 4 cited, 0 wrong · ✓ |
| **B** | hold · 12 cited, 0 wrong · ✓ | buy 363 TMGH · 4 cited, 0 wrong · ✓ |
| **C** | did not run (quota) | hold · 2 cited, 0 wrong · ✓ |
| **D** | hold · 4 cited, 0 wrong · ✓ | hold · 2 cited, 0 wrong · ✓ |

## dev_011 (harder): 4 companies, 2 units

Acceptable: buy, keep cash.

| | Gemini | Nemotron |
|---|---|---|
| **A** | buy 500 COMI · 15 cited, 0 wrong · ✓ | buy 563 ETEL · 4 cited, 1 wrong · ✓ |
| **B** | buy 625 COMI · 12 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✗ |
| **C** | did not run (quota) | buy 3,921 EFID · 3 cited, 0 wrong · ✓ |
| **D** | buy 625 COMI · 15 cited, 0 wrong · ✓ | buy 3,921 EFID · 3 cited, 0 wrong · ✓ |

## dev_012 (harder): tempting unreadable figure

Acceptable: buy, hold, keep cash, insufficient evidence.

| | Gemini | Nemotron |
|---|---|---|
| **A** | insufficient evidence · 5 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |
| **B** | insufficient evidence · 3 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |
| **C** | did not run (quota) | insufficient evidence · 0 cited, 0 wrong · ✓ |
| **D** | insufficient evidence · 5 cited, 0 wrong · ✓ | insufficient evidence · 0 cited, 0 wrong · ✓ |

## Totals over the 12 cases

| | Runs that worked | Acceptable action | Figures cited | Wrong (before verifier) |
|---|---|---|---|---|
| Gemini A | 12 of 12 | 11 of 12 | 67 | 0 |
| Gemini B | 12 of 12 | 12 of 12 | 67 | 0 |
| Gemini C | 8 of 12 | 6 of 8 | 34 | 0 |
| Gemini D | 12 of 12 | 11 of 12 | 67 | 0 |
| Nemotron A | 12 of 12 | 9 of 12 | 24 | 1 |
| Nemotron B | 12 of 12 | 9 of 12 | 16 | 1 |
| Nemotron C | 12 of 12 | 9 of 12 | 24 | 0 |
| Nemotron D | 12 of 12 | 9 of 12 | 12 | 0 |

A = single agent, B = single agent + verifier, C = team, D = team + verifier.

# Guide: filling in the reference figures

These figures are the **ground truth** for the paper. Every result we report, including how often each system cites a wrong number and how accurately the report reader reads PDFs, is measured against them. Accuracy matters far more than speed.

**File:** `data/references/reference_sheet.xlsx` (one row per figure)
**Reports:** the PDFs in `reports/`. If you don't have them, re-download them from the links in `reports/SOURCES.json`.

## How it works (one person)

1. **You fill in** the blue columns for every row, reading straight from the PDF. Put your initials in `prepared_by`.
2. **Claude checks** every filled row against the page image and lists the rows where the sheet and the page don't seem to match. It never fills in values.
3. **You re-read the PDF** for each listed row and make the final call. Then fill in the green columns: `checked_by` = your initials plus `+AI` (e.g. `ZM+AI`), `checker_agrees` = `yes` once the row is right, and `checker_note` for anything you corrected.

**Don't look at any system output while filling in the sheet**: nothing in `data/evidence/`, `runs/`, or reader results Claude shows in chat. The reference must be independent of what the system produced, or the comparison means nothing.

## The columns

| Column | Who | What to write |
|---|---|---|
| `figure_key`, `company`, `document`, `statement`, `item` | already filled | What to look for. Don't change these. |
| `page` | already filled, or blank | Page where the statement is. Correct it if wrong. Fill it in if blank (Abu Qir). For a range, write `5-6`. |
| `line_item_as_printed` | you | The row label **exactly as printed**, in the report's language. E.g. `Net profit for the year` or `صافي ربح العام`. |
| `period_code` | already filled | `FY2025` = full year 2025, `9M2026` = Jan–Sep 2026, `Q3-2026` = the three months Jul–Sep 2026, `31-12-2025` = balance sheet date, `change-9M` / `change-Q3` / `change-FY` = the printed change in % between the two nine-month, three-month or full-year columns. Correct it if the column you read is a different period. |
| `period_as_printed` | you | The column header as printed, e.g. `Dec. 31, 2025` or `٣١ ديسمبر ٢٠٢٥`. |
| `printed_value` | you | The number **exactly as printed**: keep commas, brackets and Arabic digits. E.g. `(1,234,567)`, `٥٥٬١٢٣`, `18.25`. |
| `unit_as_printed` | you | The unit that applies to **this** number, as printed, e.g. `EGP thousands`, `L.E. (000)`, `بالألف جنيه`, `EGP`. See the rules below. |
| `usable` | you | `yes`, or `no` if the number cannot be read with certainty. |
| `prepared_by` | you | Your initials. |
| `preparer_note` | you | Anything unusual: restated figures, a stamp over digits, two possible rows. |
| `checked_by` | you, after the check | Your initials plus `+AI`, e.g. `ZM+AI`. |
| `checker_agrees` | you, after the check | `yes` once you've confirmed the whole row (value, unit, period, line item) against the PDF. `no` if you couldn't settle it. |
| `checker_note` | you, after the check | What you corrected after the check, or why it's still unsettled. |

## Rules

**Copy, don't calculate.** Write the number as it appears. Don't convert thousands to pounds, don't add up subtotals, don't round. The code does the conversion.

**Units**
- Look for the unit line on the statement page. It's often in the page header, e.g. CIB's "All amounts are shown in EGP thousands", or in the column header, e.g. `L.E.(000)`.
- If only a currency is printed with no "thousands" or "millions" (e.g. Edita's `EGP` or Talaat Moustafa's `LE`), write just that currency. It means whole pounds.
- **Earnings per share** is always in pounds per share, even on a page that says "thousands". Write `EGP per share`.
- Percentages: copy them with the `%` or `٪` sign, as printed, e.g. `٪٤٦` or `%(٤)`, and leave the unit as is. Rows with a `change-…` period are always read as percentages.

**Negative numbers:** keep the brackets: `(26,645,418,395)`.

**Periods:** the income statement shows a period (a full year, or 9 months), and the balance sheet shows a date. Abu Qir's report covers **9 months** (Jan–Sep 2026). Don't confuse it with a full year. Some reports also show a 3-month column next to the 9- or 12-month one, so make sure you read the right column. Abu Qir's and Talaat Moustafa's summary pages also print the 3-month figures and a change-in-% column; these have their own rows (`Q3-…` and `change-…` periods), because the agents see and cite those numbers too.

**Consolidated, not separate.** Use the consolidated (group) statements. They're the documents listed in the sheet.

**If a figure isn't in the report**, leave `printed_value` empty and write `not reported` in `preparer_note`.

**If you can't read a digit for certain** (stamp, blur, smudge), set `usable` = `no`, leave `printed_value` empty or write what you can see with `?` for the unclear digit, and explain in `preparer_note`. Don't guess. An unreadable figure is a valid answer.

**Restated comparatives.** If last year's column says "Restated" or "Reclassified", use it as printed and mention it in the note.

## Excel tips

- The value columns are set to **Text** so Excel won't change `(1,234)` into `-1234`. Don't change the column format.
- If you work in Google Sheets, download the finished sheet as **.xlsx** (File → Download → Microsoft Excel). Don't download it as CSV.
- Don't add, delete or rename columns. You can sort or filter, and add rows if you find an important figure that's missing. Give a new row a unique `figure_key`.

## When you're done

Save the file in `data/references/` under the same name and tell Claude. It will run:

```powershell
.venv\Scripts\python -m egx_guide.references build --sheet data\references\reference_sheet.xlsx
```

This turns the sheet into `figures.json`, computes each value in pounds, and lists any rows with problems: an unclear unit, an unreadable value, a disagreement, or a row not yet checked. Fix those and run it again. Only rows with `checker_agrees` = `yes` are used.

"""Add a `how_confirmed` column to the reference sheet, so the author knows where to look hardest.

Each row Claude prepared falls in one group:
1. copied from the PDF's own text layer: the digits are the PDF's, so check the line and column chosen;
2. confirmed by the report itself: the statement's parts add up to its printed total with this
   figure, or another page of the same report prints the same number;
3. read by eye only: check every digit against the PDF;
4. not reported: check the figure really isn't in this document.

Usage: python data/references/ai_confirmation_groups.py data/references/reference_sheet.xlsx
"""
import sys
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill

COLUMN = "how_confirmed"
LABELS = {
    1: "1 PDF text layer: check line and column",
    2: "2 confirmed by the report's totals or charts: check line and column",
    3: "3 read by eye only: check every digit",
    4: "4 not reported: check it is absent",
}
FILL = {3: "F8CBAD", 4: "FFF2CC"}

# group 2: what confirms it
CONFIRMED = {
    # Telecom Egypt balance sheet (scan): total liabilities + total equity = total assets; current assets add up
    "ETEL-en-total_assets", "ETEL-en-total_liabilities", "ETEL-en-total_equity", "ETEL-en-cash_and_cash_equivalents",
    # Edita (scans): revenue - cost of sales = gross profit; PBT - tax = net profit; owners + NCI = net profit;
    # liabilities + equity = assets; current assets add up with cash
    "EFID-en-revenue", "EFID-en-gross_profit", "EFID-en-profit_before_tax", "EFID-en-net_profit_for_the_period",
    "EFID-en-net_profit_attributable_to_owners_of_the_parent", "EFID-en-total_assets", "EFID-en-total_liabilities",
    "EFID-en-total_equity", "EFID-en-cash_and_cash_equivalents",
    # Talaat Moustafa statements (scans): activity gross profits add up; PBT - taxes = net profit; parent + NCI = net
    # profit; liabilities + equity = assets; current assets add up with cash
    "TMGH-en-gross_profit", "TMGH-en-profit_before_tax", "TMGH-en-net_profit_for_the_period",
    "TMGH-en-net_profit_attributable_to_owners_of_the_parent", "TMGH-en-total_assets", "TMGH-en-total_liabilities",
    "TMGH-en-total_equity", "TMGH-en-cash_and_cash_equivalents",
    # Abu Qir: the bar charts on page 4 print revenue, gross profit and net profit in Latin digits; the charts on
    # page 5 print the balance sheet parts in millions, which add up to the totals in the text
    "ABUK-ar-revenue", "ABUK-ar-gross_profit", "ABUK-ar-net_profit_for_the_period", "ABUK-ar-total_assets",
    "ABUK-ar-total_liabilities", "ABUK-ar-total_equity",
}
# Talaat Moustafa Arabic summary: rows equal to the audited English statements (revenue = the three revenue lines;
# "profit before tax" = English operating income). Its other 2024 values differ in the last digit: read by eye only.
SUMMARY_EQUALS_STATEMENTS = {
    "TMGH-ar-revenue-FY2025", "TMGH-ar-revenue-FY2024", "TMGH-ar-gross_profit-FY2025",
    "TMGH-ar-profit_before_tax-FY2025", "TMGH-ar-profit_before_tax-FY2024", "TMGH-ar-net_profit_for_the_period-FY2025",
    "TMGH-ar-net_profit_attributable_to_owners_of_the_parent-FY2025", "TMGH-ar-basic_earnings_per_share-FY2025",
}


def base_key(key: str) -> str:
    for suffix in ("-31-12-2025", "-31-12-2024", "-30-09-2026"):
        if key.endswith(suffix):
            return key[: -len(suffix)]
    return key.rsplit("-", 1)[0] if not key.split("-")[-2].startswith("Q3") else key.rsplit("-", 2)[0]


def classify(row: dict) -> int:
    key = row["figure_key"]
    if not (row.get("printed_value") or "").strip():
        return 4
    if key.startswith("COMI-en") or (key.startswith("ETEL-en") and row.get("page") == "6"):
        return 1
    if key in SUMMARY_EQUALS_STATEMENTS:
        return 2
    if "-change-" in key:
        return 3  # printed % changes: the checker only confirms them to within 1.5 points
    return 2 if base_key(key) in CONFIRMED else 3


def main(path: Path):
    wb = load_workbook(path)
    ws = wb.active
    head = [c.value for c in ws[1]]
    if COLUMN not in head:
        ws.cell(row=1, column=len(head) + 1, value=COLUMN).font = Font(bold=True)
        ws.column_dimensions[ws.cell(row=1, column=len(head) + 1).column_letter].width = 48
        head.append(COLUMN)
    col = {h: i for i, h in enumerate(head)}
    counts = {g: 0 for g in LABELS}
    for r in ws.iter_rows(min_row=2):
        if not r[col["figure_key"]].value:
            continue
        row = {h: ("" if r[i].value is None else str(r[i].value)) for h, i in col.items() if i < len(r)}
        g = classify(row)
        counts[g] += 1
        cell = ws.cell(row=r[0].row, column=col[COLUMN] + 1, value=LABELS[g])
        if g in FILL:
            cell.fill = PatternFill("solid", fgColor=FILL[g])
    wb.save(path)
    for g, n in counts.items():
        print(f"{n:4d}  {LABELS[g]}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

"""Write the figures Claude read from the report pages into the reference sheet.

Read from the PDFs only (page images and the PDFs' own text layers), never from
data/evidence or runs. Every scanned figure was confirmed by its statement's own
totals where the page prints them.
"""
import sys
from pathlib import Path

from openpyxl import load_workbook

BY = "Claude (AI)"
ADDS = "statement totals add up with this figure"
rows = {}


def put(key, line, period, value, unit, page, note="", usable="yes"):
    rows[key] = dict(line_item_as_printed=line, period_as_printed=period, printed_value=value,
                     unit_as_printed=unit, page=page, usable=usable, prepared_by=BY, preparer_note=note)


def missing(key, note, page=""):
    rows[key] = dict(prepared_by=BY, preparer_note=note, page=page)


def pair(prefix, slug, line, cur, prev, unit, page, pc=("FY2025", "FY2024"), pp=None, note="", notes=("", "")):
    pp = pp or pc
    put(f"{prefix}-{slug}-{pc[0]}", line, pp[0], cur, unit, page, "; ".join(x for x in (note, notes[0]) if x))
    put(f"{prefix}-{slug}-{pc[1]}", line, pp[1], prev, unit, page, "; ".join(x for x in (note, notes[1]) if x))


# --- CIB (text PDF; header "All amounts are shown in EGP thousands") -------------------
C, CU = "COMI-en", "EGP thousands"
cy = ("Dec. 31, 2025", "Dec. 31, 2024")
pair(C, "net_interest_income", "Net interest income", "107,699,631", "91,064,222", CU, "5", pp=cy,
     note="interest income minus interest expense gives this")
pair(C, "net_profit_for_the_period", "Net profit for the year", "82,258,815", "55,256,732", CU, "5", pp=cy)
pair(C, "net_profit_attributable_to_owners_of_the_bank", "Bank's shareholders", "82,238,852", "55,196,394", CU, "5",
     pp=cy, note="row under Non-Controlling Interest")
pair(C, "basic_earnings_per_share", "Basic", "18.25", "14.72", "EGP per share", "5", pp=cy,
     note="the row 'Basic' under 'Earnings per share'; diluted is printed below: 18.05 / 14.56")
bs = ("31-12-2025", "31-12-2024")
pair(C, "total_assets", "Total assets", "1,442,494,120", "1,214,973,261", CU, "4", pc=bs, pp=cy,
     note="equals total liabilities and equity")
pair(C, "loans_and_advances_to_customers", "Loans and advances to customers, net", "507,953,766", "343,542,674", CU,
     "4", pc=bs, pp=cy)
pair(C, "customer_deposits", "Due to customers", "1,110,395,693", "972,595,958", CU, "4", pc=bs, pp=cy,
     note="the bank's customer deposits line")
pair(C, "total_equity", "Total NCI, equity and net profit for the year", "231,514,218", "152,819,321", CU, "4",
     pc=bs, pp=cy, note="includes non-controlling interest; the line above without it is 'Total equity and net "
     "profit for the year'; total liabilities plus this equals total assets")

# --- Telecom Egypt (income statement: text layer p6; balance sheet: scan p5) -------------
E, EU = "ETEL-en", "L.E. (000)"
ey = ("31/12/2025", "31/12/2024")
pair(E, "revenue", "Operating revenues", "106 672 946", "81 677 812", EU, "6", pp=ey)
pair(E, "gross_profit", "Gross Profit", "44 839 110", "30 492 762", EU, "6", pp=ey,
     note="revenues minus operating costs gives this")
pair(E, "profit_before_tax", "Net profit for the year before income tax", "30 911 047", "10 261 148", EU, "6", pp=ey)
pair(E, "net_profit_for_the_period", "Net profit for the year", "22 578 063", "10 111 328", EU, "6", pp=ey,
     note="continued plus discontinued operations; " + ADDS)
pair(E, "net_profit_attributable_to_owners_of_the_parent",
     "Net profit for the year for shareholders of the company", "22 554 632", "10 098 140", EU, "6", pp=ey,
     note="plus non-controlling interest gives net profit")
pair(E, "basic_earnings_per_share", "Basic and diluted earning per share for the year (L.E. / Share)", "11.93",
     "4.79", "EGP per share", "6", pp=ey, note="total EPS; continued operations alone are 11.79 / 4.65")
eb = ("31/12/2025", "31/12/2024 Reclassified")
pair(E, "total_assets", "Total Assets", "225 882 527", "197 952 788", EU, "5", pc=bs, pp=eb,
     note="scanned page; equals total equity and liabilities", notes=("", "comparative is reclassified"))
pair(E, "total_liabilities", "Total liabilities", "162 194 701", "152 014 797", EU, "5", pc=bs, pp=eb,
     note="scanned page; " + ADDS, notes=("", "comparative is reclassified"))
pair(E, "total_equity", "Total Equity", "63 687 826", "45 937 991", EU, "5", pc=bs, pp=eb,
     note="scanned page; includes non-controlling interest; " + ADDS, notes=("", "comparative is reclassified"))
pair(E, "cash_and_cash_equivalents", "Cash and cash equivalents", "8 312 470", "8 279 240", EU, "5", pc=bs, pp=eb,
     note="scanned page; current assets add up with this figure", notes=("", "comparative is reclassified"))

# --- Edita (scans; unit EGP = whole pounds) --------------------------------------------------
F = "EFID-en"
fy = ("31 December 2025", "31 December 2024")
pair(F, "revenue", "Revenue", "20 915 072 432", "16 146 545 699", "EGP", "6", pp=fy, note="scanned page")
pair(F, "gross_profit", "Gross profit", "7 192 057 221", "4 987 667 576", "EGP", "6", pp=fy,
     note="scanned page; revenue minus cost of sales gives this")
pair(F, "profit_before_tax", "Profit before income tax", "3 703 837 580", "2 163 025 380", "EGP", "6", pp=fy,
     note="scanned page; minus income tax gives net profit")
pair(F, "net_profit_for_the_period", "Net profit for the year", "2 695 301 670", "1 606 727 698", "EGP", "6", pp=fy,
     note="scanned page; " + ADDS)
pair(F, "net_profit_attributable_to_owners_of_the_parent", "Owners of the parent", "2 749 571 345", "1 633 729 383",
     "EGP", "6", pp=fy, note="scanned page; under 'Profit is attributable to'; plus the negative non-controlling "
     "interest gives net profit")
pair(F, "basic_earnings_per_share", "Basic and Diluted earnings per share", "2.18", "1.09", "EGP per share", "6",
     pp=fy, note="scanned page")
pair(F, "total_assets", "Total assets", "14 738 822 091", "10 241 537 800", "EGP", "5", pc=bs, pp=fy,
     note="scanned page; equals total equity and liabilities")
pair(F, "total_liabilities", "Total liabilities", "8 646 502 892", "6 083 968 654", "EGP", "5", pc=bs, pp=fy,
     note="scanned page; plus total equity gives total assets")
pair(F, "total_equity", "Total equity", "6 092 319 199", "4 157 569 146", "EGP", "5", pc=bs, pp=fy,
     note="scanned page; the second 'Total equity' line, including non-controlling interest; the first, without "
     "it, is 5 724 525 864 / 4 055 484 719")
pair(F, "cash_and_cash_equivalents", "Cash and bank balances", "716 765 194", "518 293 282", "EGP", "5", pc=bs, pp=fy,
     note="scanned page; the balance sheet line is 'cash and bank balances'; current assets add up with this figure")

# --- Talaat Moustafa, English statements (scans; unit LE = whole pounds) -------------------
T = "TMGH-en"
ty = ("2025", "2024 (Restated)")
missing(f"{T}-revenue-FY2025", "not reported: three revenue lines (real estate, hospitality, periodic yield) and "
        "no total", "7")
missing(f"{T}-revenue-FY2024", "not reported: three revenue lines and no total", "7")
pair(T, "gross_profit", "Gross profit", "20,855,400,384", "14,002,196,445", "LE", "7", pp=ty,
     note="scanned page; the three activity gross profits add up to it", notes=("", "comparative restated"))
pair(T, "profit_before_tax", "Profit for the year before tax", "23,653,557,143", "16,490,175,692", "LE", "7", pp=ty,
     note="scanned page; minus both tax lines gives net profit", notes=("", "comparative restated"))
pair(T, "net_profit_for_the_period", "Net profit for the year", "18,201,981,482", "12,769,517,325", "LE", "7",
     pp=ty, note="scanned page; " + ADDS, notes=("", "comparative restated"))
pair(T, "net_profit_attributable_to_owners_of_the_parent", "Shareholders of the Parent Company", "14,383,890,306",
     "9,025,066,065", "LE", "7", pp=ty, note="scanned page; under 'Attributable to'; plus non-controlling "
     "interests gives net profit", notes=("", "comparative restated"))
pair(T, "basic_earnings_per_share", "Earnings per Share", "6.98", "4.38", "EGP per share", "7", pp=ty,
     note="scanned page", notes=("", "comparative restated; the Arabic summary prints 4.37"))
tb = ("31 December 2025", "31 December 2024 (Restated)")
pair(T, "total_assets", "Total assets", "436,222,206,712", "355,173,008,042", "LE", "5", pc=bs, pp=tb,
     note="scanned page; non-current and current assets add up to it; equals total equity and liabilities on page 6",
     notes=("", "comparative restated"))
pair(T, "total_liabilities", "Total liabilities", "278,514,065,947", "225,293,194,349", "LE", "6", pc=bs, pp=tb,
     note="scanned page; plus total equity gives total assets", notes=("", "comparative restated"))
pair(T, "total_equity", "Total equity", "157,708,140,765", "129,879,813,693", "LE", "5", pc=bs, pp=tb,
     note="scanned page; includes non-controlling interests", notes=("", "comparative restated"))
pair(T, "cash_and_cash_equivalents", "Cash and cash equivalents", "44,846,514,337", "44,909,587,972", "LE", "5",
     pc=bs, pp=tb, note="scanned page; current assets add up with this figure", notes=("", "comparative restated"))

# --- Talaat Moustafa, Arabic results summary (scan, page 1) --------------------------------
A, AU = "TMGH-ar", "العملة بالجنية المصرى"
ay = ("٢٠٢٥/١٢/٣١", "٢٠٢٤/١٢/٣١", "التغير %")


def three(slug, line, cur, prev, chg, note="", notes=("", "", "")):
    for code, per, val, n in zip(("FY2025", "FY2024", "change-FY"), ay, (cur, prev, chg), notes):
        put(f"{A}-{slug}-{code}", line, per, val, "" if code.startswith("change") else AU, "1",
            "; ".join(x for x in ("scanned Arabic page", note, n) if x))


three("revenue", "الإيرادات", "٦٢,٤٩٥,١٤٤,١٩٧", "٤٢,٦٧٠,٢٨٣,٢٨٨", "٪٤٦",
      note="equals the sum of the three revenue lines in the English statements")
three("gross_profit", "مجمل الربح", "٢٠,٨٥٥,٤٠٠,٣٨٤", "١٤,٠٠٢,١٩٦,٤٤٦", "٪٤٩",
      notes=("", "the English statements print 14,002,196,445 (last digit differs)", ""))
three("profit_before_tax", "صافى الربح قبل الضريبة من الأنشطة المستمرة", "٢٣,٧٤٩,٣١٨,٢٧٢", "١٦,٩٨٠,٥٣٤,٣٥٥", "٪٤٠",
      note="labelled profit before tax, but the figures equal 'Operating Income' in the English statements; "
           "English profit before tax is 23,653,557,143 / 16,490,175,692")
three("net_profit_for_the_period", "ربح العام بعد الضرائب*", "١٨,٢٠١,٩٨١,٤٨٢", "١٢,٧٦٩,٥١٧,٣٢٦", "٪٤٣",
      notes=("", "the English statements print 12,769,517,325 (last digit differs); restated comparative (*)", ""))
three("net_profit_attributable_to_owners_of_the_parent", "صافى ربح العام بعد الضرائب والحقوق غير المسيطرة",
      "١٤,٣٨٣,٨٩٠,٣٠٦", "٩,٠٢٥,٠٦٦,٠٦٦", "٪٥٩",
      note="printed in the financial position table (ب) under equity",
      notes=("", "the English statements print 9,025,066,065 (last digit differs)", ""))
three("basic_earnings_per_share", "نصيب السهم فى الأرباح", "٦,٩٨", "٤,٣٧", "٪٥٩,٦",
      notes=("", "the English statements print 4.38", ""))
for slug in ("total_assets", "total_liabilities", "total_equity", "cash_and_cash_equivalents"):
    for code in bs:
        missing(f"{A}-{slug}-{code}", "not reported: the summary prints net working capital and equity "
                "components, no total" + (" (cash flows only)" if slug.startswith("cash") else ""), "1")

# --- Abu Qir (scan; results release; income table p2 in EGP millions) ----------------------
B, BU = "ABUK-ar", "(مليون جنيه)"
nine = ("التسعة أشهر المنتهية في ٣٠ سبتمبر ٢٠٢٦", "التسعة أشهر المنتهية في ٣٠ سبتمبر ٢٠٢٥",
        "الثلاثة أشهر المنتهية في ٣٠ سبتمبر ٢٠٢٦", "الثلاثة أشهر المنتهية في ٣٠ سبتمبر ٢٠٢٥",
        "التسعة أشهر - التغير (٪)", "الثلاثة أشهر - التغير (٪)")
codes = ("9M2026", "9M2025", "Q3-2026", "Q3-2025", "change-9M", "change-Q3")


def six(slug, line, vals, unit=BU, note=""):
    for code, per, val in zip(codes, nine, vals):
        put(f"{B}-{slug}-{code}", line, per, val, "" if code.startswith("change") else unit, "2",
            "; ".join(x for x in ("scanned Arabic page", note) if x))


six("revenue", "إيرادات النشاط", ("٣١٤٨٨", "١٦٥٧٨", "٧٩٦٤", "٣٩١١", "٪٩٠", "٪١٠٤"),
    note="the bar charts on page 4 print the same four amounts")
six("gross_profit", "مجمل الربح", ("١٥٤٠١", "٧٨٦١", "٢٤٣٠", "١٧٨١", "٪٩٦", "٪٣٦"),
    note="the bar charts on page 4 print the same four amounts")
six("profit_before_tax", "صافي ربح الفترة قبل الضريبة", ("١٦٤٤٣", "٨٠٨٢", "٣٧٨٦", "٢٣٠١", "٪١٠٣", "٪٦٥"))
six("net_profit_for_the_period", "صافي ربح الفترة", ("١٢٩٧٠", "٦٣٩٦", "٢٩٥٨", "١٨٢٨", "٪١٠٣", "٪٦٢"),
    note="the bar charts on page 4 print the same four amounts")
six("basic_earnings_per_share", "نصيب السهم الأساسي في الأرباح (جنيه)", ("٨٫٧٤", "٤٫٢٨", "١٫٩٩", "١٫٢٣", "٪١٠٤", "٪٦٢"),
    unit="EGP per share")
for code in codes:
    missing(f"{B}-net_profit_attributable_to_owners_of_the_parent-{code}", "not reported", "2")
bb = ("في ٣٠/٩/٢٠٢٦", "في ٣١/١٢/٢٠٢٥")
abs_ = ("30-09-2026", "31-12-2025")
for slug, line, cur, prev in (("total_assets", "إجمالي الأصول", "٣٩٫٩٤", "٣٢٫٦١"),
                              ("total_liabilities", "إجمالي الإلتزامات", "٧٫٦٨", "٩٫٣٦"),
                              ("total_equity", "مجموع حقوق الملكية", "٣٢٫٢٦", "٢٣٫٢٤")):
    for code, per, val in zip(abs_, bb, (cur, prev)):
        put(f"{B}-{slug}-{code}", line, per, val, "مليار جنيه", "5",
            "scanned Arabic page; printed in the text, rounded to two decimals of a billion; the charts on the "
            "same page print the parts in millions")
for code in abs_:
    missing(f"{B}-cash_and_cash_equivalents-{code}", "not reported", "5")

# --- write -----------------------------------------------------------------------------------
path = Path(sys.argv[1])
wb = load_workbook(path)
ws = wb.active
head = [c.value for c in ws[1]]
col = {h: i for i, h in enumerate(head)}
seen = set()
for r in ws.iter_rows(min_row=2):
    key = r[col["figure_key"]].value
    if key in rows:
        for name, v in rows[key].items():
            r[col[name]].value = v
        seen.add(key)
keys = {r[col["figure_key"]].value for r in ws.iter_rows(min_row=2) if r[col["figure_key"]].value}
print("written", len(seen), "of", len(keys), "rows")
print("not in sheet:", sorted(set(rows) - seen))
print("sheet rows left untouched:", sorted(keys - seen))
wb.save(path)

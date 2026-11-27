"""One simple page for the 32 read-by-eye rows: a zoomed picture of the printed table, and the sheet's values beside it."""
import html
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

root = Path(sys.argv[1])
out = root / "data/references/check"
(out / "pages").mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / "src"))
from egx_guide.references import read_sheet  # noqa: E402

rows = {r["figure_key"]: r for r in read_sheet(root / "data/references/reference_sheet.xlsx")}
red = [k for k, r in rows.items() if (r.get("how_confirmed") or "").startswith("3")]


def crop(doc, page, boxes, name, scale=5.0):
    """boxes in the 2x render's pixel frame (1190 x 1684); stacked top to bottom."""
    pdf = pdfium.PdfDocument(str(root / "reports" / doc))
    img = pdf[page - 1].render(scale=scale).to_pil()
    f = scale / 2.0
    parts = [img.crop(tuple(int(v * f) for v in b)) for b in boxes]
    w = max(p.width for p in parts)
    canvas = Image.new("RGB", (w, sum(p.height for p in parts) + 12 * (len(parts) - 1)), "white")
    y = 0
    for p in parts:
        canvas.paste(p, (0, y))
        y += p.height + 12
    canvas.save(out / "pages" / name)
    return f"pages/{name}"


groups = [
    ("Talaat Moustafa Arabic summary, page 1: income table (top)",
     crop("TMGH_FY2025_results_summary_ar.pdf", 1, [(170, 595, 1065, 820)], "easy_tmgh_ar_income.png"),
     "TMGH-ar-", lambda k: "attributable" not in k,
     "The 2024 column is the middle one (٢٠٢٤/١٢/٣١). The % column is on the left (التغير %)."),
    ("Talaat Moustafa Arabic summary, page 1: the profit row in the equity table (ب)",
     crop("TMGH_FY2025_results_summary_ar.pdf", 1, [(170, 965, 1065, 990), (170, 1185, 1065, 1255)],
          "easy_tmgh_ar_equity.png"),
     "TMGH-ar-net_profit_attributable", lambda k: True,
     "The row صافى ربح العام بعد الضرائب والحقوق غير المسيطرة."),
    ("Talaat Moustafa English statements, page 7: earnings per share",
     crop("TMGH_FY2025_consolidated_en.pdf", 7, [(80, 190, 1150, 265), (80, 1135, 1150, 1175)], "easy_tmgh_en_eps.png"),
     "TMGH-en-", lambda k: True, "Bottom row of the profit or loss statement."),
    ("Edita, page 6: earnings per share",
     crop("EFID_FY2025_EAS_consolidated_signed_en.pdf", 6, [(90, 240, 1140, 310), (90, 825, 1140, 865)],
          "easy_efid_eps.png"),
     "EFID-en-", lambda k: True, "Bottom row of the profit or loss statement."),
    ("Abu Qir, page 2: results table, nine months (right block)",
     crop("ABUK_9M2026_results.pdf", 2, [(360, 1150, 1060, 1395)], "easy_abuk_9m.png"),
     "ABUK-ar-", lambda k: "9M" in k, "Nine-month block. Rows: profit before tax (4th), earnings per share (last)."),
    ("Abu Qir, page 2: results table, three months (left block)",
     crop("ABUK_9M2026_results.pdf", 2, [(70, 1150, 370, 1395)], "easy_abuk_q3.png"),
     "ABUK-ar-", lambda k: "Q3" in k, "Three-month block, same rows as the nine-month block."),
]

used = set()
parts = ["""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Red rows to check</title>
<style>
body{font:15px/1.5 system-ui,sans-serif;margin:16px;max-width:1100px;background:#fafafa;color:#222}
h2{margin-top:36px;border-top:2px solid #ccc;padding-top:10px}
img{max-width:100%;border:1px solid #bbb;background:#fff}
table{border-collapse:collapse;margin-top:8px;background:#fff}
td,th{border:1px solid #ccc;padding:5px 9px;text-align:left}
.v{font:20px Consolas,monospace}
.how{background:#eef6ff;padding:10px 14px;border-radius:6px}
</style></head><body>
<h1>The 32 red rows</h1>
<div class="how"><b>For each row below:</b> find it in the picture, compare the number digit by digit.
<br>Same → in Excel put your initials in <b>checked_by</b> and <b>yes</b> in <b>checker_agrees</b>.
<br>Different → write the number you see in <b>printed_value</b>, then initials, yes, and what you changed in <b>checker_note</b>.
<br>Pictures are zoomed from the PDF; if a digit is unclear, open the PDF itself in <code>reports/</code>.</div>"""]
for title, src, prefix, keep, hint in groups:
    keys = [k for k in red if k.startswith(prefix) and keep(k) and k not in used]
    if not keys:
        continue
    used.update(keys)
    parts.append(f"<h2>{html.escape(title)}</h2><p>{html.escape(hint)}</p><img src='{src}' alt='{html.escape(title)}'>")
    parts.append("<table><tr><th>figure_key (Excel row)</th><th>line as printed</th><th>column</th>"
                 "<th>sheet says</th></tr>")
    for k in keys:
        r = rows[k]
        parts.append(f"<tr><td>{html.escape(k)}</td><td dir='auto'>{html.escape(r['line_item_as_printed'])}</td>"
                     f"<td dir='auto'>{html.escape(r['period_as_printed'])}</td>"
                     f"<td class='v' dir='ltr'>{html.escape(r['printed_value'])}</td></tr>")
    parts.append("</table>")
parts.append("</body></html>")
(out / "easy_check.html").write_text("".join(parts), encoding="utf-8")
missing = sorted(set(red) - used)
print(len(red), "red rows;", len(used), "on the page; missing:", missing)

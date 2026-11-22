"""Free local OCR for scanned Arabic pages (EasyOCR, Arabic + English).

Free vision models invented or skipped Arabic scans (21-22 Nov 2026), and
Tesseract misreads Arabic-Indic digits in tables. EasyOCR reads those digits,
but sometimes takes a thousands or decimal comma for the Arabic zero '٠'
(e.g. '٢٠,٨٥٥' read as '٢٠٠٨٥٥'). ``ocr_number_doubts`` lists the signs of
that, so such figures are marked ambiguous rather than trusted.

The output is plain text, one printed line per line, with the boxes of a line
ordered right to left and joined by ' | ', so table rows stay together.
"""

from __future__ import annotations

import re
from functools import lru_cache

from .numbers import normalize, parse_amount

RENDER_SCALE = 400 / 72   # 400 dpi: small Arabic-Indic digits need it
LANGS = ["ar", "en"]


@lru_cache(maxsize=1)
def _reader():
    import easyocr  # heavy (PyTorch); only loaded when OCR is used
    return easyocr.Reader(LANGS, gpu=_has_cuda(), verbose=False)


def _has_cuda() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False


def group_lines(boxes: list[tuple[list, str]], rtl: bool = True) -> str:
    """Boxes [(corner points, text)] -> text lines, top to bottom.

    A box joins the current line when its vertical centre is within half the
    box height of the line's centre. Within a line, boxes run right to left for
    Arabic pages.
    """
    items = []
    for pts, text in boxes:
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]
        items.append(((min(ys) + max(ys)) / 2, max(ys) - min(ys), min(xs), text.strip()))
    items.sort()
    lines: list[list] = []
    for yc, h, x, text in items:
        if not text:
            continue
        if lines and abs(lines[-1][0] - yc) < max(h, 1) * 0.5:
            lines[-1][1].append((x, text))
        else:
            lines.append([yc, [(x, text)]])
    return "\n".join(" | ".join(t for _, t in sorted(toks, reverse=rtl)) for _, toks in lines)


def ocr_image(image) -> str:
    import numpy as np
    result = _reader().readtext(np.array(image.convert("RGB")), paragraph=False)
    return group_lines([(box, text) for box, text, _conf in result])


def ocr_page(page) -> str:
    return ocr_image(page.render(scale=RENDER_SCALE).to_pil())


# ---------------------------------------------------------------- doubts

_NUM = re.compile(r"\(?\d[\d,.]*\d\)?|\d")
_SCALE_WORD = re.compile(r"^\s*(مليار|مليون|billion|million|bn|mn)", re.I)


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def uses_thousands_separators(text: str) -> bool:
    """Most numbers of 5+ digits on the page are printed with thousands separators."""
    big = [n for n in _NUM.findall(normalize(text)) if len(_digits(n.split(".")[0])) >= 5]
    if len(big) < 3:
        return False
    return sum("," in n for n in big) / len(big) >= 0.6


def ocr_number_doubts(printed: str, page_text: str, per_share: bool) -> list[str]:
    """Reasons to distrust a number read by OCR (empty if none)."""
    out = []
    s = normalize(printed).strip("() %")
    whole = s.split(".")[0]
    if per_share and not re.search(r"[.,]\d{1,2}$", s):
        out.append("OCR: per-share figure without a decimal mark (a decimal comma may have been dropped)")
    if "," not in whole and len(_digits(whole)) >= 5 and uses_thousands_separators(page_text):
        out.append("OCR: long number without the thousands separators used elsewhere on the page")
    value = parse_amount(printed).value
    if value is None or abs(value) >= 1000:  # '12,49 billion' is fine; '12049 billion' is not
        text = normalize(page_text)
        for m in re.finditer(re.escape(normalize(printed).strip()), text):
            if _SCALE_WORD.match(text[m.end():m.end() + 12]):
                out.append("OCR: too many digits before 'billion/million' (a decimal comma may have been read as 0)")
                break
    return out

"""Read PDF pages into text, keeping track of how each page was read.

Text-bearing pages use the PDF's own text layer. Scanned pages (little or no
text, images present) are transcribed by a vision-capable model. Arabic pages
with a text layer are flagged, because right-to-left text layers can come out
in the wrong order; in "auto" mode they are sent to the vision model too when
one is available. So are table pages whose text layer has no unit line, since
some reports draw "EGP thousands" in the page header as graphics.

A page that cannot be read is kept with method "none" and a warning, so the
failure shows up in the output instead of disappearing.
"""

from __future__ import annotations

import base64
import hashlib
import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_raw
from langchain_core.messages import HumanMessage, SystemMessage

from .llm import Caller, is_transient
from .numbers import arabic_ratio, detect_scale, normalize

Mode = Literal["auto", "text", "vision"]

MIN_TABLE_AMOUNTS = 3     # amounts of 4+ digits before a page counts as a financial table
_AMOUNT = re.compile(r"\d{1,3}(?:[, ]\d{3})+|\d{4,}")

MIN_TEXT_CHARS = 40       # fewer non-space characters than this = no usable text layer
ARABIC_PAGE_RATIO = 0.3   # share of letters that are Arabic before a page counts as Arabic
RENDER_SCALE = 2.0        # 144 dpi; enough for statement tables

TRANSCRIBE_SYSTEM = """You transcribe pages of company financial reports exactly.
- Start with the page header exactly as printed: the company name, the statement title, the date or period,
  and any unit line (e.g. "All amounts are shown in EGP thousands"), even if they are small, in a corner, or in a logo.
- Copy all text in its original language (Arabic or English). Do not translate, summarise or compute.
- If the page is unreadable, say so. Never write content that is not on the page.
- Reproduce tables as Markdown tables, keeping every row label, column header (periods, notes) and the unit line (e.g. "بالألف جنيه" or "EGP thousands").
- Copy every number exactly as printed, including parentheses, commas and Arabic-Indic digits.
- If any character of a number is unclear, write "?" in its place. Never guess a digit.
- Keep signatures, stamps and handwriting out unless they contain figures; note "[stamp]" if a stamp covers figures."""


@dataclass
class PageRecord:
    page: int                                   # 1-based
    method: Literal["text", "vision", "none"]
    text: str
    text_layer_chars: int
    image_objects: int
    arabic_ratio: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class DocumentRecord:
    path: str
    sha256: str
    page_count: int
    pages: list[PageRecord]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _png_data_url(page: pdfium.PdfPage) -> str:
    image = page.render(scale=RENDER_SCALE).to_pil()
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def transcribe_page(caller: Caller, page: pdfium.PdfPage, number: int) -> str:
    return caller.text(f"transcribe_p{number}", [
        SystemMessage(TRANSCRIBE_SYSTEM),
        HumanMessage(content=[
            {"type": "text", "text": f"Transcribe page {number}."},
            {"type": "image_url", "image_url": {"url": _png_data_url(page)}},
        ]),
    ])


def confirm_transcription(text: str, expect: list[str] | None, expect_years: list[str] | None) -> list[str]:
    """Warnings if a vision transcription doesn't name the company or the report's year.

    A model can invent a plausible page (on 2026-11-21 one turned Abu Qir's results
    into another company's 2023 quarter). Figures are then "grounded" in the invented
    text, so this check against what we know about the file is the only cheap guard.
    """
    t = normalize(text).lower()
    out = []
    if expect and not any(normalize(e).lower() in t for e in expect):
        out.append(f"unconfirmed transcription: does not name the company ({', '.join(expect)})")
    if expect_years and not any(y in t for y in expect_years):
        out.append(f"unconfirmed transcription: does not mention {' or '.join(expect_years)}")
    return out


def read_pdf(
    path: str | Path,
    pages: list[int] | None = None,
    mode: Mode = "auto",
    vision: Caller | None = None,
    expect: list[str] | None = None,
    expect_years: list[str] | None = None,
) -> DocumentRecord:
    """Read the chosen pages (1-based; all if None).

    ``expect`` (company names) and ``expect_years`` are checked against every vision
    transcription; a miss is recorded as an "unconfirmed transcription" warning.
    """
    path = Path(path)
    if mode == "vision" and vision is None:
        raise ValueError("mode 'vision' needs a vision model")
    pdf = pdfium.PdfDocument(str(path))
    try:
        count = len(pdf)
        wanted = pages or list(range(1, count + 1))
        out = []
        for n in wanted:
            if not 1 <= n <= count:
                out.append(PageRecord(n, "none", "", 0, 0, 0.0, [f"page {n} does not exist ({count} pages)"]))
                continue
            page = pdf[n - 1]
            textpage = page.get_textpage()
            layer = textpage.get_text_range() or ""
            textpage.close()
            chars = sum(1 for c in layer if not c.isspace())
            images = len(list(page.get_objects(filter=(pdfium_raw.FPDF_PAGEOBJ_IMAGE,))))
            ratio = arabic_ratio(layer)
            warnings = []

            has_text = chars >= MIN_TEXT_CHARS
            if not has_text:
                warnings.append("no usable text layer" + (" (scanned image)" if images else ""))
            arabic_layer = has_text and ratio >= ARABIC_PAGE_RATIO
            if arabic_layer:
                warnings.append("Arabic text layer: reading order may be wrong")
            # A table page whose unit line is drawn as graphics (e.g. in the page header)
            # has numbers but no unit in its text layer; only the image shows the unit.
            unitless_table = (has_text and len(_AMOUNT.findall(layer)) >= MIN_TABLE_AMOUNTS
                              and detect_scale(layer)[0] is None)
            if unitless_table:
                warnings.append("no unit in text layer: unit may be drawn as graphics")

            use_vision = vision is not None and (
                mode == "vision" or (mode == "auto" and (not has_text or arabic_layer or unitless_table)))
            if use_vision:
                try:
                    text = transcribe_page(vision, page, n)
                    method = "vision"
                    warnings += confirm_transcription(text, expect, expect_years)
                except Exception as exc:  # keep the failure visible
                    if is_transient(exc):
                        raise  # quota or overload on every model: stop, rather than save the page as unreadable
                    warnings.append(f"vision transcription failed: {exc!r}")
                    text, method = (layer, "text") if has_text else ("", "none")
            elif has_text:
                text, method = layer, "text"
            else:
                text, method = "", "none"
                warnings.append("needs OCR: no vision model configured")
            out.append(PageRecord(n, method, text, chars, images, round(ratio, 3), warnings))
            page.close()
        return DocumentRecord(str(path), file_sha256(path), count, out)
    finally:
        pdf.close()


def parse_pages(spec: str | None) -> list[int] | None:
    """'3-5,9' -> [3, 4, 5, 9]."""
    if not spec:
        return None
    result = []
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        result.extend(range(int(a), int(b or a) + 1))
    return result

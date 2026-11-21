"""Build small PDFs for tests: text-layer pages (via PDFium) and image-only (scanned-like) pages."""

from __future__ import annotations

import ctypes
from pathlib import Path

import pypdfium2 as pdfium
import pypdfium2.raw as r
from PIL import Image, ImageDraw

FONT = Path("C:/Windows/Fonts/arial.ttf")


def text_pdf(path: Path, pages: list[list[str]]) -> Path:
    pdf = pdfium.PdfDocument.new()
    data = FONT.read_bytes()
    buf = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
    font = r.FPDFText_LoadFont(pdf, buf, len(data), r.FPDF_FONT_TRUETYPE, True)
    for lines in pages:
        page = pdf.new_page(595, 842)
        y = 780
        for line in lines:
            obj = r.FPDFPageObj_CreateTextObj(pdf, font, 11)
            ws = ctypes.create_string_buffer((line + "\0").encode("utf-16-le"))
            r.FPDFText_SetText(obj, ctypes.cast(ws, ctypes.POINTER(r.FPDF_WCHAR)))
            r.FPDFPageObj_Transform(obj, 1, 0, 0, 1, 50, y)
            r.FPDFPage_InsertObject(page, obj)
            y -= 20
        r.FPDFPage_GenerateContent(page)
    pdf.save(str(path))
    pdf.close()
    return path


def scanned_pdf(path: Path) -> Path:
    img = Image.new("RGB", (800, 1100), "white")
    ImageDraw.Draw(img).text((50, 50), "Net profit 55,123", fill="black")
    img.save(path, "PDF")
    return path

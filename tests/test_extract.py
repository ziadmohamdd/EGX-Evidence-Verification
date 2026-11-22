"""PDF reading and figure extraction with scripted models: no network, no API key."""

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from egx_guide.documents import PageRecord, parse_pages, read_pdf
from egx_guide.extract import ExtractedFigure, PageFigures, check_figure, extract_figures
from egx_guide.llm import Caller
from egx_guide.models import EvidenceStatus

from .pdf_factory import FONT, scanned_pdf, text_pdf

pytestmark = pytest.mark.skipif(not FONT.exists(), reason="needs Arial to build test PDFs")

ENGLISH = ["Consolidated income statement", "All amounts in EGP thousands",
           "Net profit for the year 55,123 48,900", "Total assets 1,250,000 1,100,000"]
ARABIC = ["قائمة الدخل المجمعة بالألف جنيه مصري", "صافي ربح العام ٥٥٬١٢٣ ٤٨٬٩٠٠",
          "إجمالي الأصول ١٬٢٥٠٬٠٠٠ ١٬١٠٠٬٠٠٠"]


class FakeVision:
    """Stands in for a vision chat model: records the image it was sent, returns a transcription."""

    def __init__(self, text="| Net profit | 55,123 |\nEGP thousands", fail=False):
        self.text, self.fail, self.images = text, fail, []

    def invoke(self, messages):
        if self.fail:
            raise RuntimeError("quota exceeded")
        self.images += [b["image_url"]["url"] for b in messages[-1].content if isinstance(b, dict) and b.get("type") == "image_url"]
        return AIMessage(self.text)


class FakeExtractor:
    def __init__(self, pages: dict[int, PageFigures]):
        self.pages, self.prompts = pages, []

    def with_structured_output(self, schema, include_raw=False, **kw):
        def answer(messages):
            text = messages[-1].content
            self.prompts.append(text)
            n = int(text.split("Page ")[1].split(" ")[0])
            return {"raw": AIMessage("{}"), "parsed": self.pages[n], "parsing_error": None}
        return RunnableLambda(answer)


def fig(value, period="FY2024", row=None, **kw):
    return ExtractedFigure(label="Net profit", printed_value=value, row_text=row or f"Net profit {value}", period=period, **kw)


# ---------------------------------------------------------------- reading pages


def test_text_page_uses_text_layer(tmp_path):
    doc = read_pdf(text_pdf(tmp_path / "en.pdf", [ENGLISH]))
    [p] = doc.pages
    assert p.method == "text" and "55,123" in p.text and p.warnings == []
    assert len(doc.sha256) == 64


def test_scanned_page_without_vision_is_reported(tmp_path):
    [p] = read_pdf(scanned_pdf(tmp_path / "scan.pdf")).pages
    assert p.method == "none" and p.image_objects >= 1
    assert any("needs OCR" in w for w in p.warnings)


def test_scanned_page_goes_to_vision(tmp_path):
    vision = FakeVision()
    [p] = read_pdf(scanned_pdf(tmp_path / "scan.pdf"), vision=Caller(vision)).pages
    assert p.method == "vision" and "55,123" in p.text
    assert vision.images[0].startswith("data:image/png;base64,")


def test_transcription_must_name_the_company_and_year(tmp_path):
    # 2026-11-21: a free model "transcribed" Abu Qir's page as another company's 2023 results
    path = scanned_pdf(tmp_path / "scan.pdf")
    invented = FakeVision("شركة أورا للتطوير العقاري\nالربع الأول ٢٠٢٣\n| صافي الربح | ٥٥٬١٢٣ |")
    [p] = read_pdf(path, vision=Caller(invented), expect=["أبوقير", "Abou Kir"], expect_years=["2026"]).pages
    assert any(w.startswith("unconfirmed transcription") for w in p.warnings)
    real = FakeVision("شركة أبوقير للأسمدة\nالتسعة أشهر المنتهية في ٣٠ سبتمبر ٢٠٢٦\n| صافي الربح | ٥٥٬١٢٣ |")
    [p] = read_pdf(path, vision=Caller(real), expect=["أبوقير", "Abou Kir"], expect_years=["2026"]).pages
    assert not any(w.startswith("unconfirmed") for w in p.warnings)


def test_figures_from_an_unconfirmed_transcription_are_ambiguous():
    page = PageRecord(1, "vision", "EGP thousands\nNet profit 55,123", 0, 1, 0.0,
                      ["unconfirmed transcription: does not name the company"])
    assert any("unconfirmed transcription" in r for r in check_figure(fig("55,123"), page, "EGP thousands")[2])


def test_arabic_text_layer_is_flagged_and_sent_to_vision_in_auto(tmp_path):
    path = text_pdf(tmp_path / "ar.pdf", [ARABIC])
    [p] = read_pdf(path).pages
    assert p.method == "text" and p.arabic_ratio > 0.3
    assert any("Arabic text layer" in w for w in p.warnings)
    [pv] = read_pdf(path, vision=Caller(FakeVision("نص"))).pages
    assert pv.method == "vision"


def test_vision_failure_falls_back_and_is_recorded(tmp_path):
    [p] = read_pdf(scanned_pdf(tmp_path / "scan.pdf"), vision=Caller(FakeVision(fail=True))).pages
    assert p.method == "none" and any("vision transcription failed" in w for w in p.warnings)


NO_UNIT = ["Consolidated income statement", "Net profit for the year 55,123 48,900",
           "Total assets 1,250,000 1,100,000"]


def test_table_page_without_unit_in_text_layer_goes_to_vision(tmp_path):
    # e.g. CIB: "All amounts are shown in EGP thousands" is drawn in the header, not in the text layer
    path = text_pdf(tmp_path / "nounit.pdf", [NO_UNIT])
    [p] = read_pdf(path).pages
    assert p.method == "text" and any("no unit in text layer" in w for w in p.warnings)
    [pv] = read_pdf(path, vision=Caller(FakeVision())).pages
    assert pv.method == "vision"
    [pt] = read_pdf(path, mode="text", vision=Caller(FakeVision())).pages
    assert pt.method == "text"


def test_page_with_unit_in_text_layer_stays_text(tmp_path):
    [p] = read_pdf(text_pdf(tmp_path / "en.pdf", [ENGLISH]), vision=Caller(FakeVision())).pages
    assert p.method == "text"


class GoogleRateLimitError(Exception):
    pass


def test_rate_limit_stops_the_run_instead_of_saving_empty_pages(tmp_path):
    class Limited(FakeVision):
        def invoke(self, messages):
            raise GoogleRateLimitError("429 RESOURCE_EXHAUSTED")
    with pytest.raises(GoogleRateLimitError):
        read_pdf(scanned_pdf(tmp_path / "scan.pdf"), vision=Caller(Limited()))


def test_page_selection(tmp_path):
    doc = read_pdf(text_pdf(tmp_path / "two.pdf", [ENGLISH, ENGLISH]), pages=parse_pages("2,5"))
    assert [p.page for p in doc.pages] == [2, 5]
    assert doc.pages[1].method == "none" and "does not exist" in doc.pages[1].warnings[0]
    assert parse_pages("3-5,9") == [3, 4, 5, 9]


# ---------------------------------------------------------------- figure checks

PAGE = PageRecord(1, "text", "\n".join(ENGLISH), 100, 0, 0.0)


def reasons(f, page=PAGE, unit="EGP thousands"):
    return check_figure(f, page, unit)[2]


def test_clean_figure_is_scaled():
    value, scale, why, grounded, _ = check_figure(fig("55,123"), PAGE, "EGP thousands")
    assert why == [] and grounded and scale == 1e3 and value == 55_123_000


def test_invented_number_is_caught():
    assert "number not found in page text" in reasons(fig("55,124"))


def test_unit_line_must_match_page():
    assert any("disagrees" in r for r in reasons(fig("55,123"), unit="EGP millions"))


def test_missing_unit_and_period_are_caught():
    page = PageRecord(1, "text", "Net profit 55,123", 20, 0, 0.0)
    why = reasons(fig("55,123", period=None), page=page, unit=None)
    assert "unit/scale not stated on page" in why and "period not stated" in why


def test_bracket_dropped_by_model_is_restored_from_page():
    page = PageRecord(1, "vision", "| Costs | (33) | (26,645,418,395) | EGP", 50, 0, 0.0)
    value, scale, why, grounded, _ = check_figure(fig("(26,645,418,395"), page, "EGP")
    assert why == [] and grounded and value == -26_645_418_395


def test_bracket_is_not_invented_when_page_lacks_it():
    page = PageRecord(1, "vision", "| Costs | 26,645,418,395 | EGP", 50, 0, 0.0)
    assert any("not a single number" in r for r in check_figure(fig("(26,645,418,395"), page, "EGP")[2])


def test_percentages_are_not_scaled():
    page = PageRecord(1, "vision", "Gross margin 33.4% ... EGP thousands", 50, 0, 0.0)
    value, scale, why, *_ = check_figure(fig("33.4%"), page, "EGP thousands")
    assert why == [] and value == 33.4 and scale == 1.0


def test_per_share_figures_keep_pounds_on_a_thousands_page():
    # CIB: "All amounts in EGP thousands", but earnings per share is printed in pounds
    page = PageRecord(1, "text", "EGP thousands\nNet profit 82,238,852\nBasic 18.25 14.72", 80, 0, 0.0)
    eps = ExtractedFigure(label="Earnings per share - Basic", printed_value="18.25",
                          row_text="Basic 18.25 14.72", period="FY2025")
    value, scale, why, *_ = check_figure(eps, page, "EGP thousands")
    assert why == [] and value == 18.25 and scale == 1.0
    profit = ExtractedFigure(label="Net profit", printed_value="82,238,852", row_text="Net profit 82,238,852",
                             period="FY2025")
    assert check_figure(profit, page, "EGP thousands")[0] == 82_238_852_000


def test_basic_and_diluted_rows_under_an_eps_heading_are_per_share():
    # CIB prints "Earnings per share" as a heading, then rows labelled just "Basic" and "Diluted"
    page = PageRecord(1, "vision", "All amounts are shown in EGP thousands\nNet profit 82,238,852\n"
                      "Earnings per share\nBasic 18.25 14.72\nDiluted 18.05 14.56", 80, 0, 0.0)
    for label, printed in (("Basic", "18.25"), ("Diluted", "18.05")):
        f = ExtractedFigure(label=label, printed_value=printed, row_text=f"{label} {printed}", period="FY2025")
        assert check_figure(f, page, "EGP thousands")[0] == float(printed)


def test_basic_row_without_eps_on_page_is_a_money_amount():
    page = PageRecord(1, "vision", "EGP thousands\nBasic salaries 1,234", 30, 0, 0.0)
    f = ExtractedFigure(label="Basic salaries", printed_value="1,234", row_text="Basic salaries 1,234", period="FY2025")
    assert check_figure(f, page, "EGP thousands")[0] == 1_234_000


def test_extractor_doubt_and_rtl_layer_are_caught():
    assert any("extractor marked uncertain" in r for r in reasons(fig("55,123", uncertain=True)))
    rtl = PageRecord(1, "text", PAGE.text, 100, 0, 0.8, ["Arabic text layer: reading order may be wrong"])
    assert any("right-to-left" in r for r in reasons(fig("55,123"), page=rtl))


# ---------------------------------------------------------------- end to end


def test_extract_figures_end_to_end(tmp_path):
    doc = read_pdf(text_pdf(tmp_path / "COMI FY2024.pdf", [ENGLISH]))
    extractor = FakeExtractor({1: PageFigures(unit_line="EGP thousands", figures=[
        fig("55,123", row="Net profit for the year 55,123 48,900"),
        fig("8?0"),
    ])})
    items, checks = extract_figures(doc, "COMI", Caller(extractor))
    good, bad = items
    assert good.evidence_id == "COMI-COMI_FY2024-p1-01"
    assert good.status is EvidenceStatus.VERIFIED and good.value == 55_123_000 and good.scale == 1e3
    assert "unit: EGP thousands" in good.source_text
    assert bad.status is EvidenceStatus.AMBIGUOUS and bad.value is None and "illegible" in bad.note
    assert checks[1].grounded is False
    assert "Page 1 text" in extractor.prompts[0]


def test_unreadable_pages_are_skipped_not_sent(tmp_path):
    doc = read_pdf(scanned_pdf(tmp_path / "scan.pdf"))
    items, _ = extract_figures(doc, "X", Caller(FakeExtractor({})))
    assert items == []

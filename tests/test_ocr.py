from egx_guide.numbers import normalize, parse_amount
from egx_guide.ocr import group_lines, ocr_number_doubts, uses_thousands_separators


def box(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def test_group_lines_keeps_rows_together_right_to_left():
    boxes = [
        (box(600, 100, 800, 130), "الإيرادات"),
        (box(300, 102, 500, 132), "٦٢,٤٩٥,١٤٤,١٩٧"),
        (box(50, 101, 250, 131), "٤٢,٦٧٠,٢٨٣,٢٨٨"),
        (box(600, 200, 800, 230), "مجمل الربح"),
        (box(300, 199, 500, 229), "٢٠,٨٥٥,٤٠٠,٣٨٤"),
    ]
    assert group_lines(boxes).splitlines() == [
        "الإيرادات | ٦٢,٤٩٥,١٤٤,١٩٧ | ٤٢,٦٧٠,٢٨٣,٢٨٨",
        "مجمل الربح | ٢٠,٨٥٥,٤٠٠,٣٨٤",
    ]


def test_arabic_comma_between_digits_is_a_separator_only_there():
    assert normalize("٦٢،٤٩٥") == "62,495"
    assert normalize("سبتمبر ٢٠٢٦، حققت") == "سبتمبر 2026، حققت"
    assert parse_amount("٨،٧٤").value == 8.74


def test_comma_read_as_zero_breaks_grouping_and_is_unclear():
    # '٢٠,٨٥٥,٤٠٠,٣٨٤' with two commas read as the Arabic zero
    assert parse_amount("٢٠٠٨٥٥،٤٠٠٠٣٨٤").uncertain


def test_per_share_without_decimal_mark_is_doubted():
    assert ocr_number_doubts("١٩٩", "", per_share=True)        # printed ١,٩٩
    assert not ocr_number_doubts("٨،٧٤", "", per_share=True)


def test_long_number_without_separators_on_a_page_that_uses_them():
    page = "٦٢,٤٩٥,١٤٤,١٩٧ | ٤٢,٦٧٠,٢٨٣,٢٨٨ | ١٤,٠٠٢,١٩٦,٤٤٦ | ٢٣٧٤٩٣١٨٢٧٢"
    assert uses_thousands_separators(page)
    assert ocr_number_doubts("٢٣٧٤٩٣١٨٢٧٢", page, per_share=False)
    assert not ocr_number_doubts("٦٢,٤٩٥,١٤٤,١٩٧", page, per_share=False)


def test_page_in_millions_without_separators_is_fine():
    page = "إيرادات النشاط | ٣١٤٨٨ | ١٦٥٧٨\nمجمل الربح | ١٥٤٠١ | ٧٨٦١\nأرباح التشغيل | ١٢٤٨٨ | ٦٦٨٤"
    assert not uses_thousands_separators(page)
    assert not ocr_number_doubts("٣١٤٨٨", page, per_share=False)


def test_too_many_digits_before_billion():
    page = "وبلغ ربح التشغيل ١٢٠٤٩ مليار جنيه"   # printed ١٢,٤٩ مليار
    assert ocr_number_doubts("١٢٠٤٩", page, per_share=False)
    assert not ocr_number_doubts("١٢,٤٩", "ربح ١٢,٤٩ مليار جنيه", per_share=False)

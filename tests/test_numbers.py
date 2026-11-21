import pytest

from egx_guide.numbers import arabic_ratio, contains_number, detect_scale, normalize, parse_amount


@pytest.mark.parametrize("raw, value", [
    ("1,234", 1234),
    ("1,234,567.5", 1234567.5),
    ("(1,234)", -1234),
    ("-1,234", -1234),
    ("−1,234", -1234),
    ("٢٬٥٠٠", 2500),          # Arabic-Indic digits, Arabic thousands separator
    ("(٣٤٥٫٦)", -345.6),      # Arabic decimal separator, negative
    ("۱۲۳", 123),             # Extended Arabic-Indic
    ("12.5%", 12.5),
    ("1 234 567", 1234567),
    ("-", 0),
    ("—", 0),
    ("7", 7),
    ("٦,٩٨", 6.98),           # Arabic-Indic digits: a comma before 1-2 digits can only be a decimal
    ("٣٣,٣٧%", 33.37),
    ("(١٥٢,٢٣٥,٧٢٥)", -152235725),
])
def test_parse_clear_amounts(raw, value):
    p = parse_amount(raw)
    assert not p.uncertain and p.value == pytest.approx(value)


@pytest.mark.parametrize("raw, why", [
    ("8?0", "illegible"),
    ("1,2�4", "illegible"),
    ("1,234-", "trailing minus"),
    ("1,23", "separators"),
    ("12,34,567", "separators"),
    ("1.234.567", "separators"),
    ("1,234 5,678", "single number"),
    ("", "empty"),
    ("n/a", "single number"),
])
def test_parse_uncertain_amounts(raw, why):
    p = parse_amount(raw)
    assert p.uncertain and p.value is None and why in p.reason


@pytest.mark.parametrize("text, scale", [
    ("All amounts in EGP thousands", 1e3),
    ("(EGP '000)", 1e3),
    ("Figures in EGP millions", 1e6),
    ("EGP mn", 1e6),
    ("جميع المبالغ بالألف جنيه مصري", 1e3),
    ("القيم بالمليون جنيه", 1e6),
    ("مليار جنيه", 1e9),
])
def test_detect_scale(text, scale):
    assert detect_scale(text)[0] == scale


@pytest.mark.parametrize("text", [
    "31 December 2025 EGP", "2025 LE", "Note 31/12/2025 L.E.", "in Egyptian pounds",
    "العملة بالجنية المصرى", "القيم بالجنيه المصري",
])
def test_currency_without_scale_word_means_whole_pounds(text):
    assert detect_scale(text)[0] == 1.0


def test_scale_word_wins_over_plain_currency():
    assert detect_scale("L.E. (000) ... EGP")[0] == 1e3
    assert detect_scale("بالألف جنيه")[0] == 1e3


def test_conflicting_or_missing_scale_is_none():
    assert detect_scale("Balance sheet")[0] is None
    s, found = detect_scale("in thousands ... in millions")
    assert s is None and len(found) == 2


def test_presentation_forms_are_folded():
    # "ﺑﺎﻷﻟﻒ" written in presentation forms, as some PDF text layers return it
    assert detect_scale("ﺑﺎﻷﻟﻒ ﺟﻨﻴﻪ")[0] == 1e3
    assert normalize("ﻣﻠﻴﻮﻥ") == "مليون"


def test_contains_number_is_whole_number_only():
    page = "Net profit 55,123 48,900\nTotal 1,055,123"
    assert contains_number(page, "55,123")
    assert contains_number(page, "(55,123)")
    assert not contains_number(page, "5,123")
    assert not contains_number(page, "55,12")
    assert contains_number("صافي الربح ٥٥٬١٢٣", "55,123")


def test_arabic_ratio():
    assert arabic_ratio("Net profit") == 0
    assert arabic_ratio("صافي الربح") == 1

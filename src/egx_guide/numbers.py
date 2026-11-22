"""Deterministic reading of financial numbers and units, Arabic and English.

No language model here. These functions decide whether a printed figure can be
read without doubt; anything they cannot settle is reported as uncertain so
the figure becomes an Ambiguous Financial Figure instead of a guess.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_DIGITS = str.maketrans({
    **{chr(0x0660 + i): str(i) for i in range(10)},  # Arabic-Indic ٠-٩
    **{chr(0x06F0 + i): str(i) for i in range(10)},  # Extended Arabic-Indic ۰-۹
    "٬": ",",   # Arabic thousands separator ٬
    "٫": ".",   # Arabic decimal separator ٫
    "−": "-",   # minus sign
    "‒": "-", "–": "-", "—": "-", "‐": "-",
    " ": " ", " ": " ", " ": " ",
    "­": "-",   # soft hyphen: PDF text layers use it for a printed dash
})
_BIDI_MARKS = re.compile("[‎‏‪-‮⁦-⁩؜]")


def normalize(text: str) -> str:
    """NFKC (folds Arabic presentation forms), ASCII digits, no bidi control marks."""
    out = _BIDI_MARKS.sub("", unicodedata.normalize("NFKC", text)).translate(_DIGITS)
    return _ARABIC_COMMA_IN_NUMBER.sub(",", out)


# The Arabic comma '،' between digits is a number separator (OCR output uses it);
# elsewhere it is ordinary punctuation and is left alone.
_ARABIC_COMMA_IN_NUMBER = re.compile(r"(?<=\d)،(?=\d)")


@dataclass(frozen=True)
class ParsedNumber:
    value: float | None
    uncertain: bool
    reason: str | None = None


_UNCERTAIN_CHARS = set("?�*")
_ARABIC_DIGIT = re.compile("[٠-٩۰-۹]")
_NUMBER = re.compile(r"\d[\d,. ]*\d|\d")


def parse_amount(raw: str) -> ParsedNumber:
    """Read one printed amount such as '1,234', '(1,234)', '٢٬٥٠٠', '-', '12.5'.

    Parentheses and a leading minus mean negative. A lone dash means nil (0).
    A trailing minus (common after right-to-left extraction) is reported as
    uncertain, as are '?' marks, several numbers in one cell, or separators
    that do not form clean thousands groups.
    """
    s = normalize(raw).strip()
    if not s:
        return ParsedNumber(None, True, "empty")
    if any(c in _UNCERTAIN_CHARS for c in s):
        return ParsedNumber(None, True, "illegible character")
    if re.fullmatch(r"-+", s):
        return ParsedNumber(0.0, False, "dash means nil")

    negative = False
    if re.fullmatch(r"\(.*\)", s):
        negative, s = True, s[1:-1].strip()
    if s.startswith("-"):
        negative, s = not negative, s[1:].strip()
    if s.endswith("-"):
        return ParsedNumber(None, True, "trailing minus: sign unclear (possible right-to-left order)")
    s = s.rstrip("%").strip()

    found = _NUMBER.findall(s)
    if len(found) != 1 or found[0] != s:
        return ParsedNumber(None, True, f"not a single number: {raw!r}")

    if " " in s and not re.fullmatch(r"\d{1,3}( \d{3})+", s):
        return ParsedNumber(None, True, f"not a single number: {raw!r}")
    num = s.replace(" ", ",")
    if _ARABIC_DIGIT.search(raw) and re.fullmatch(r"\d+,\d{1,2}", num):
        # Arabic decimal mark '٫' often comes out of transcription as a comma.
        # One or two digits after it cannot be a thousands group, so it is a decimal.
        num = num.replace(",", ".")
    if "," in num:
        whole, _, frac = num.partition(".")
        if not re.fullmatch(r"\d{1,3}(,\d{3})+", whole):
            return ParsedNumber(None, True, f"unclear separators: {raw!r}")
        num = whole.replace(",", "") + ("." + frac if frac else "")
    if num.count(".") > 1:
        return ParsedNumber(None, True, f"unclear separators: {raw!r}")
    value = float(num)
    return ParsedNumber(-value if negative else value, False)


# ------------------------------------------------------------------ scale

_SCALES = [
    (1e9, [r"\bbillions?\b", r"\bbn\b", r"مليار"]),
    (1e6, [r"\bmillions?\b", r"\bmn\b", r"\bmln\b", r"مليون", r"ملايين"]),
    (1e3, [r"\bthousands?\b", r"'000\b", r"\(000\)", r"\b000s\b", r"\bk\b", r"بالألف", r"بالالف",
           r"بالآلاف", r"بالاف", r"ألف جنيه", r"الف جنيه", r"آلاف"]),
]


# A currency printed with no scale word means whole pounds ("31 December 2025 EGP").
_CURRENCY = [r"\begp\b", r"\bl\.e\.?", r"\ble\b", r"egyptian pounds?", r"جنيه", r"جنية"]


def detect_scale(text: str) -> tuple[float | None, list[str]]:
    """Find the unit header of a page or table ('EGP thousands', 'بالألف جنيه', 'EGP', ...).

    Returns (scale, matches). A scale word (thousands, millions, ...) decides.
    With no scale word, a printed currency means whole units (scale 1).
    Scale is None when nothing is found or when different scale words appear,
    which callers must treat as ambiguous.
    """
    t = normalize(text).lower()
    hits: dict[float, list[str]] = {}
    for scale, patterns in _SCALES:
        for p in patterns:
            for m in re.finditer(p, t):
                hits.setdefault(scale, []).append(m.group(0))
    if len(hits) == 1:
        (scale, found), = hits.items()
        return scale, found
    if hits:
        return None, [m for found in hits.values() for m in found]
    currency = [m.group(0) for p in _CURRENCY for m in re.finditer(p, t)]
    return (1.0, currency) if currency else (None, [])


# ------------------------------------------------------------------ non-money rows

_PER_SHARE = [r"per share", r"\beps\b", r"نصيب السهم", r"ربحية السهم", r"ربح السهم", r"عائد السهم",
              r"توزيعات السهم"]
_SHARE_COUNT = [r"number of shares", r"shares outstanding", r"عدد الأسهم", r"عدد الاسهم"]


def figure_kind(label: str) -> str | None:
    """'per_share' (pounds per share), 'count' (number of shares), or None (a money amount).

    A page's unit line ("EGP thousands") applies to money amounts only. Per-share
    figures are printed in whole pounds and share counts are plain numbers, so
    scaling them by the page unit would be off by a factor of 1,000 or more.
    """
    t = normalize(label).lower()
    if any(re.search(p, t) for p in _PER_SHARE):
        return "per_share"
    if any(re.search(p, t) for p in _SHARE_COUNT):
        return "count"
    return None


def contains_number(haystack: str, raw: str) -> bool:
    """Whether the printed number appears in the page text (after normalising both)."""
    needle = normalize(raw).strip().strip("()").strip()
    if not needle:
        return False
    hay = normalize(haystack)
    return re.search(r"(?<![\d.,])" + re.escape(needle) + r"(?![\d]|[.,]\d)", hay) is not None


def arabic_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if "؀" <= c <= "ۿ" or "ﭐ" <= c <= "﻿") / len(letters)

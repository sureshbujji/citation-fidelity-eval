"""Small text utilities: tokenization, stemming, typed numbers, negation."""

from __future__ import annotations

import re

STOPWORDS = frozenset(
    """
    the a an and or of to for in on with per up it they them their this that
    these those is are was were be been being has have had do does did will
    would can could should as at by from into its it's it’s and or but if then
    than so such no nor only own same too very s t d
    """.split()
)

# Unit words that attach to numbers (normalized after stemming).
UNIT_WORDS = frozenset(
    "gb tb mb kb inch inches mp minutes minute hours hour hrs hz watt watts".split()
)

NEGATION_RE = re.compile(
    r"\b(not|never|n't|cannot|can't|won't|don't|doesn't|isn't|aren't|wasn't|"
    r"weren't|lacks?|without|neither|nor)\b",
    re.IGNORECASE,
)

# A number with an optional $-prefix and an optional glued/trailing unit
# ("10.9-inch", "16GB", "$799").
TYPED_NUMBER_RE = re.compile(r"(?<![a-zA-Z0-9])\$?\s*(\d[\d,]*(?:\.\d+)?)\s*-?\s*([a-zA-Z]+)?")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def stem(word: str) -> str:
    if len(word) <= 3:
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("ches", "shes", "sses", "xes", "zes")):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def has_negation(text: str) -> bool:
    return bool(NEGATION_RE.search(text))


def _number_type(dollar: bool, unit: str, value: float) -> str:
    if dollar:
        return "money"
    unit = unit.lower()
    if unit in UNIT_WORDS:
        canon = {"inches": "inch", "minutes": "minute", "hours": "hour",
                 "hrs": "hour", "watts": "watt"}.get(unit, unit.rstrip("s"))
        return "qty:" + canon
    if unit:
        return "plain"
    if value == int(value) and 1900 <= value <= 2100:
        return "year"
    return "plain"


def typed_numbers(text: str) -> dict[str, list[float]]:
    """Extract numbers keyed by semantic type: money / year / qty:<unit> / plain.

    Typing keeps "released in 2024" (year) from being confused with
    "costs $2024" (money), and "16GB" (qty:gb) from "16 minutes" (qty:minute).
    """
    out: dict[str, list[float]] = {}
    for match in TYPED_NUMBER_RE.finditer(text):
        raw, unit = match.group(1), match.group(2) or ""
        dollar = match.group(0).lstrip().startswith("$")
        value = float(raw.replace(",", ""))
        ntype = _number_type(dollar, unit, value)
        out.setdefault(ntype, []).append(value)
    return out


def attribute_tokens(text: str, product_tokens: frozenset[str] = frozenset()) -> list[str]:
    """Content tokens minus product names, stopwords, units, and raw numbers.

    Used for the *attribute* overlap between a claim and a candidate evidence
    sentence: the subject (product name) is checked separately so that a claim
    about the Aurora Phone can never be "supported" by a Nimbus Tablet sentence
    that happens to share generic words.
    """
    toks: list[str] = []
    for word in tokenize(text):
        if not word or word[0].isdigit():
            continue
        if word in STOPWORDS or word in UNIT_WORDS or word in product_tokens:
            continue
        word = stem(word)
        if word in STOPWORDS or word in UNIT_WORDS or word in product_tokens:
            continue
        toks.append(word)
    return toks


def jaccard(a: set[str] | list[str], b: set[str] | list[str]) -> float:
    a, b = set(a), set(b)
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)

"""Evidence alignment: does a corpus sentence support / contradict a claim?

All stdlib and deterministic. The design is deliberately conservative:

* A sentence can only bear on a claim if the *subject* matches (the claim
  names the sentence's product, or names no product at all and is matched by
  attribute overlap alone). This stops cross-product false "support".
* Numbers are compared by *type* (money vs year vs qty:<unit> vs plain), so a
  claim about a 2024 release year is never "contradicted" by a $2024 price.
* Contradiction needs same-type numbers that differ, or single-sided negation,
  on top of solid attribute overlap.
"""

from __future__ import annotations

from .data import PRODUCT_TOKENS, PRODUCT_VOCAB
from .text import (
    attribute_tokens,
    has_negation,
    jaccard,
    tokenize,
    typed_numbers,
)

SUPPORT_THRESHOLD = 0.25
CONTRADICTION_THRESHOLD = 0.25
NEGATION_THRESHOLD = 0.30


def subject_matches(claim_text: str, doc_id: str) -> bool:
    """True when the claim is about this document's product.

    A claim that names no product at all (e.g. "It costs $799.") is treated as
    matchable: pronoun resolution is left to attribute overlap.
    """
    mentioned = set(tokenize(claim_text)) & PRODUCT_VOCAB
    if not mentioned:
        return True
    return bool(mentioned & PRODUCT_TOKENS[doc_id])


def sentence_relation(claim_text: str, sentence: str, doc_id: str) -> str:
    """Classify one (claim, evidence sentence) pair.

    Returns "supports", "contradicts", or "unrelated".
    """
    if not subject_matches(claim_text, doc_id):
        return "unrelated"
    ptoks = PRODUCT_TOKENS[doc_id]
    overlap = jaccard(
        attribute_tokens(claim_text, ptoks),
        attribute_tokens(sentence, ptoks),
    )
    if overlap < SUPPORT_THRESHOLD:
        return "unrelated"

    claim_nums = typed_numbers(claim_text)
    sent_nums = typed_numbers(sentence)
    for ntype, cvals in claim_nums.items():
        svals = sent_nums.get(ntype, [])
        if (
            len(cvals) == 1
            and len(svals) == 1
            and cvals[0] != svals[0]
            and overlap >= CONTRADICTION_THRESHOLD
        ):
            return "contradicts"

    if (
        overlap >= NEGATION_THRESHOLD
        and has_negation(claim_text) != has_negation(sentence)
    ):
        return "contradicts"

    return "supports"

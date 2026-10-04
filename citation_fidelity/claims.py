"""Answer -> atomic claims with parsed citations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .text import split_sentences

CITATION_RE = re.compile(r"\[D(\d+)\]")
LEADING_CITATIONS_RE = re.compile(r"^(?:\s*\[D(\d+)\])+")


@dataclass(frozen=True)
class AnswerClaim:
    """One atomic claim (a sentence) from a RAG answer."""

    text: str  # claim text with citation markers stripped
    citations: tuple[str, ...]  # e.g. ("D1", "D3")
    index: int = 0

    @property
    def cited(self) -> bool:
        return bool(self.citations)


def parse_answer(answer: str) -> list[AnswerClaim]:
    """Split an answer into claims, extracting [D#] citations per sentence.

    Citation markers belong to the sentence they *follow*: a marker split off
    as the head of the next raw sentence ("... 2024. [D3] It costs ...") is
    re-attached to the preceding claim. A marker-only tail ("... $799. [D1]")
    merges into the preceding claim as well.
    """
    claims: list[AnswerClaim] = []
    pending: list[str] = []  # leading markers seen before any claim exists
    for sentence in split_sentences(answer):
        leading: tuple[str, ...] = ()
        head = LEADING_CITATIONS_RE.match(sentence)
        if head:
            leading = tuple(f"D{num}" for num in CITATION_RE.findall(head.group(0)))
            sentence = sentence[head.end():]
        if leading:
            if claims:
                prev = claims[-1]
                claims[-1] = AnswerClaim(
                    text=prev.text,
                    citations=prev.citations + leading,
                    index=prev.index,
                )
            else:
                pending.extend(leading)
        citations = tuple(f"D{num}" for num in CITATION_RE.findall(sentence))
        text = CITATION_RE.sub("", sentence).strip()
        # Collapse doubled whitespace left behind by marker removal.
        text = re.sub(r"\s{2,}", " ", text)
        if text:
            claims.append(
                AnswerClaim(
                    text=text,
                    citations=tuple(pending) + citations,
                    index=len(claims),
                )
            )
            pending = []
        elif citations and claims:
            prev = claims[-1]
            claims[-1] = AnswerClaim(
                text=prev.text,
                citations=prev.citations + citations,
                index=prev.index,
            )
    return claims

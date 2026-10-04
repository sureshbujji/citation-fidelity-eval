"""Tests for claim parsing."""

from citation_fidelity.claims import parse_answer


def test_parse_single_citation():
    claims = parse_answer("The Aurora Phone was released in 2024. [D1]")
    assert len(claims) == 1
    assert claims[0].text == "The Aurora Phone was released in 2024."
    assert claims[0].citations == ("D1",)
    assert claims[0].cited


def test_parse_multiple_citations_on_one_sentence():
    claims = parse_answer("It costs $799. [D1][D2]")
    assert claims[0].citations == ("D1", "D2")


def test_parse_claim_without_citation():
    claims = parse_answer("The Aurora Phone was released in 2024.")
    assert len(claims) == 1
    assert claims[0].citations == ()
    assert not claims[0].cited


def test_parse_multi_sentence_answer():
    claims = parse_answer(
        "The Aurora Phone was released in 2024. [D1] It costs $799. [D1]"
    )
    assert len(claims) == 2
    assert [c.index for c in claims] == [0, 1]
    assert claims[1].text == "It costs $799."


def test_citation_markers_are_stripped_from_text():
    claims = parse_answer("It costs $799 [D1] today.")
    assert "[D1]" not in claims[0].text


def test_citation_after_sentence_attaches_to_that_sentence():
    # The splitter separates "... 2024. [D3]" into two raw pieces; the marker
    # must re-attach to the claim it follows, not the claim after it.
    claims = parse_answer(
        "The Aurora Phone was released in 2024. [D3] It costs $799. [D1]"
    )
    assert len(claims) == 2
    assert claims[0].text == "The Aurora Phone was released in 2024."
    assert claims[0].citations == ("D3",)
    assert claims[1].text == "It costs $799."
    assert claims[1].citations == ("D1",)

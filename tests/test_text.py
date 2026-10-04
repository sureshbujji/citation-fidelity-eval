"""Tests for text utilities."""

from citation_fidelity.text import (
    attribute_tokens,
    has_negation,
    jaccard,
    split_sentences,
    stem,
    tokenize,
    typed_numbers,
)


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("The Aurora Phone costs $799!") == [
        "the",
        "aurora",
        "phone",
        "costs",
        "799",
    ]


def test_stem_handles_common_inflections():
    assert stem("includes") == "include"
    assert stem("features") == "feature"
    assert stem("ships") == "ship"
    assert stem("costs") == "cost"
    assert stem("supports") == "support"
    assert stem("flies") == "fly"
    assert stem("watches") == "watch"
    # -ed forms are left alone on purpose: claim and evidence share the form,
    # so consistency (not correctness) is what the overlap needs.
    assert stem("released") == "released"


def test_typed_numbers_money():
    assert typed_numbers("It costs $799.") == {"money": [799.0]}


def test_typed_numbers_year():
    assert typed_numbers("released in 2024") == {"year": [2024.0]}


def test_typed_numbers_quantities():
    assert typed_numbers("16GB of RAM") == {"qty:gb": [16.0]}
    assert typed_numbers("a 10.9-inch display") == {"qty:inch": [10.9]}
    assert typed_numbers("45 minutes per charge") == {"qty:minute": [45.0]}
    assert typed_numbers("a 200MP camera") == {"qty:mp": [200.0]}


def test_typed_numbers_plain_for_bare_model_codes():
    assert typed_numbers("supports 5G") == {"plain": [5.0]}
    assert typed_numbers("Wi-Fi 7") == {"plain": [7.0]}


def test_typed_numbers_separates_year_from_money():
    nums = typed_numbers("It costs $2024 and was released in 2024")
    assert nums == {"money": [2024.0], "year": [2024.0]}


def test_has_negation():
    assert has_negation("The Pulse Watch does not include a heart-rate sensor.")
    assert has_negation("It lacks voice control.")
    assert not has_negation("It includes a heart-rate sensor.")


def test_split_sentences():
    sents = split_sentences("First. Second! Third?")
    assert sents == ["First.", "Second!", "Third?"]


def test_jaccard():
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3
    assert jaccard({"a"}, {"a"}) == 1.0
    assert jaccard(set(), set()) == 0.0


def test_attribute_tokens_drop_product_names_stopwords_and_numbers():
    toks = attribute_tokens(
        "The Aurora Phone was released in 2024", frozenset({"aurora", "phone"})
    )
    assert toks == ["released"]
    toks = attribute_tokens("It has 128GB of storage", frozenset({"aurora", "phone"}))
    assert toks == ["storage"]

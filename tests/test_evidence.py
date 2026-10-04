"""Tests for evidence alignment (supports / contradicts / unrelated)."""

from citation_fidelity.evidence import sentence_relation


def test_identical_sentence_supports():
    rel = sentence_relation(
        "The Aurora Phone was released in 2024.",
        "The Aurora Phone was released in 2024.",
        "D1",
    )
    assert rel == "supports"


def test_pronoun_sentence_supports():
    rel = sentence_relation("It costs $799.", "It costs $799.", "D1")
    assert rel == "supports"


def test_cross_product_sentence_is_unrelated():
    # Same attribute words, different product -> must NOT support.
    rel = sentence_relation(
        "The Aurora Phone was released in 2024.",
        "The Nimbus Tablet was released in 2024.",
        "D3",
    )
    assert rel == "unrelated"


def test_money_mismatch_contradicts():
    rel = sentence_relation(
        "The Zephyr Laptop costs $999.", "It costs $1299.", "D2"
    )
    assert rel == "contradicts"


def test_year_mismatch_contradicts():
    rel = sentence_relation(
        "The Aurora Phone was released in 2023.",
        "The Aurora Phone was released in 2024.",
        "D1",
    )
    assert rel == "contradicts"


def test_quantity_mismatch_contradicts():
    rel = sentence_relation(
        "The Vortex Drone flies for up to 30 minutes per charge.",
        "It flies for up to 45 minutes per charge.",
        "D4",
    )
    assert rel == "contradicts"


def test_negation_contradicts():
    rel = sentence_relation(
        "The Pulse Watch does not include a heart-rate sensor.",
        "It includes a heart-rate sensor.",
        "D5",
    )
    assert rel == "contradicts"


def test_typed_numbers_prevent_false_contradiction():
    # Same digits, different types (year vs money): not a contradiction.
    rel = sentence_relation(
        "The Aurora Phone was released in 2024.",
        "The Aurora Phone was released for $2024.",
        "D1",
    )
    assert rel == "supports"


def test_fabricated_attribute_is_unrelated():
    rel = sentence_relation(
        "The Aurora Phone has a 200MP camera.",
        "The Aurora Phone was released in 2024.",
        "D1",
    )
    assert rel == "unrelated"

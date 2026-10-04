"""Fixture corpus and scripted RAG answers.

The corpus is eight short fictional product documents with dense, checkable
facts. Each of the five answer *personas* answers the same six questions with
a designed failure mode, so the bench has known-good separations to detect:

  faithful      - every claim true, every citation correct (the ceiling)
  sloppy_citer  - every claim true, but ~half the citations point at the wrong doc
  hallucinator  - ~half the claims are fabricated (true nowhere in the corpus)
  contradictor  - ~half the claims contradict the cited doc (wrong number / negation)
  no_citations  - every claim true, but nothing is cited at all
"""

from __future__ import annotations

from .text import split_sentences

CORPUS_TEXT: dict[str, str] = {
    "D1": "The Aurora Phone was released in 2024. It costs $799. "
          "It has 128GB of storage and supports 5G.",
    "D2": "The Zephyr Laptop was released in 2023. It costs $1299. "
          "It ships with 16GB of RAM and a 512GB SSD.",
    "D3": "The Nimbus Tablet was released in 2024. It costs $499. "
          "It has a 10.9-inch display.",
    "D4": "The Vortex Drone was released in 2025. It costs $899. "
          "It flies for up to 45 minutes per charge.",
    "D5": "The Pulse Watch was released in 2023. It costs $299. "
          "It includes a heart-rate sensor.",
    "D6": "The Echo Speaker was released in 2022. It costs $149. "
          "It supports voice control.",
    "D7": "The Halo Headphones were released in 2024. They cost $349. "
          "They feature active noise cancellation.",
    "D8": "The Orbit Router was released in 2025. It costs $199. "
          "It supports Wi-Fi 7.",
}

PRODUCT_TOKENS: dict[str, frozenset[str]] = {
    "D1": frozenset({"aurora", "phone"}),
    "D2": frozenset({"zephyr", "laptop"}),
    "D3": frozenset({"nimbus", "tablet"}),
    "D4": frozenset({"vortex", "drone"}),
    "D5": frozenset({"pulse", "watch"}),
    "D6": frozenset({"echo", "speaker"}),
    "D7": frozenset({"halo", "headphones"}),
    "D8": frozenset({"orbit", "router"}),
}

PRODUCT_VOCAB: frozenset[str] = frozenset().union(*PRODUCT_TOKENS.values())

PERSONAS = ["faithful", "sloppy_citer", "hallucinator", "contradictor", "no_citations"]

# question_id -> {"question": str, "answers": {persona: answer_text}}
QUESTIONS: dict[str, dict] = {
    "q1": {
        "question": "When was the Aurora Phone released and what does it cost?",
        "answers": {
            "faithful": "The Aurora Phone was released in 2024. [D1] It costs $799. [D1]",
            "sloppy_citer": "The Aurora Phone was released in 2024. [D3] It costs $799. [D1]",
            "hallucinator": "The Aurora Phone was released in 2024. [D1] "
                            "It has a 200MP camera. [D1]",
            "contradictor": "The Aurora Phone was released in 2023. [D1] It costs $799. [D1]",
            "no_citations": "The Aurora Phone was released in 2024. It costs $799.",
        },
    },
    "q2": {
        "question": "Tell me about the Zephyr Laptop's price and memory.",
        "answers": {
            "faithful": "The Zephyr Laptop costs $1299. [D2] It ships with 16GB of RAM. [D2]",
            "sloppy_citer": "The Zephyr Laptop costs $1299. [D2] It ships with 16GB of RAM. [D5]",
            "hallucinator": "The Zephyr Laptop costs $1299. [D2] It folds in half. [D2]",
            "contradictor": "The Zephyr Laptop costs $999. [D2] It ships with 16GB of RAM. [D2]",
            "no_citations": "The Zephyr Laptop costs $1299. It ships with 16GB of RAM.",
        },
    },
    "q3": {
        "question": "What are the Nimbus Tablet's display size and price?",
        "answers": {
            "faithful": "The Nimbus Tablet has a 10.9-inch display. [D3] It costs $499. [D3]",
            "sloppy_citer": "The Nimbus Tablet has a 10.9-inch display. [D3] It costs $499. [D7]",
            "hallucinator": "The Nimbus Tablet has a 10.9-inch display. [D3] "
                            "It recognizes handwriting. [D3]",
            "contradictor": "The Nimbus Tablet has a 12.9-inch display. [D3] It costs $499. [D3]",
            "no_citations": "The Nimbus Tablet has a 10.9-inch display. It costs $499.",
        },
    },
    "q4": {
        "question": "How long does the Vortex Drone fly, and when was it released?",
        "answers": {
            "faithful": "The Vortex Drone flies for up to 45 minutes per charge. [D4] "
                        "The Vortex Drone was released in 2025. [D4]",
            "sloppy_citer": "The Vortex Drone flies for up to 45 minutes per charge. [D4] "
                            "The Vortex Drone was released in 2025. [D8]",
            "hallucinator": "The Vortex Drone flies for up to 45 minutes per charge. [D4] "
                            "It has obstacle avoidance. [D4]",
            "contradictor": "The Vortex Drone flies for up to 30 minutes per charge. [D4] "
                            "The Vortex Drone was released in 2025. [D4]",
            "no_citations": "The Vortex Drone flies for up to 45 minutes per charge. "
                            "The Vortex Drone was released in 2025.",
        },
    },
    "q5": {
        "question": "Does the Pulse Watch have a heart-rate sensor? What does it cost?",
        "answers": {
            "faithful": "The Pulse Watch includes a heart-rate sensor. [D5] It costs $299. [D5]",
            "sloppy_citer": "The Pulse Watch includes a heart-rate sensor. [D1] It costs $299. [D5]",
            "hallucinator": "The Pulse Watch includes a heart-rate sensor. [D5] "
                            "It tracks blood oxygen. [D5]",
            "contradictor": "The Pulse Watch does not include a heart-rate sensor. [D5] "
                            "It costs $299. [D5]",
            "no_citations": "The Pulse Watch includes a heart-rate sensor. It costs $299.",
        },
    },
    "q6": {
        "question": "Compare the Echo Speaker and Halo Headphones prices.",
        "answers": {
            "faithful": "The Echo Speaker costs $149. [D6] The Halo Headphones cost $349. [D7]",
            "sloppy_citer": "The Echo Speaker costs $149. [D6] The Halo Headphones cost $349. [D6]",
            "hallucinator": "The Echo Speaker costs $149. [D6] "
                            "The Halo Headphones have a 40-hour battery life. [D7]",
            "contradictor": "The Echo Speaker costs $149. [D6] The Halo Headphones cost $249. [D7]",
            "no_citations": "The Echo Speaker costs $149. The Halo Headphones cost $349.",
        },
    },
}


def build_corpus() -> dict[str, dict]:
    """doc id -> {"text": ..., "sentences": [...]}."""
    return {
        doc_id: {"text": text, "sentences": split_sentences(text)}
        for doc_id, text in CORPUS_TEXT.items()
    }

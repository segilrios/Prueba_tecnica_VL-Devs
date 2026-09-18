from config import intents


def test_dynamic_catalog_is_used_on_every_call(monkeypatch):
    catalog = {
        "first": {"patterns": ["alpha"]},
        "second": {"patterns": ["beta feature"]},
    }
    monkeypatch.setattr(intents, "INTENTS", catalog)

    assert intents.classify_intent("Alpha is present") == "first"
    catalog["third"] = {"patterns": ["new áccent-pattern"]}
    assert intents.classify_intent("A NEW ACCENT/PATTERN appeared") == "third"


def test_longest_normalized_pattern_wins_at_word_boundaries(monkeypatch):
    monkeypatch.setattr(
        intents,
        "INTENTS",
        {
            "short": {"patterns": ["error"]},
            "specific": {"patterns": ["session error"]},
        },
    )

    assert intents.classify_intent("A session-error occurred") == "specific"
    assert intents.classify_intent("terror should not match") == intents.UNKNOWN


def test_catalog_order_resolves_equal_length_ties(monkeypatch):
    monkeypatch.setattr(
        intents,
        "INTENTS",
        {
            "first": {"patterns": ["same"]},
            "second": {"patterns": ["same"]},
        },
    )

    assert intents.classify_intent("same") == "first"


def test_only_lines_whose_first_character_is_quote_marker_are_ignored(monkeypatch):
    monkeypatch.setattr(
        intents,
        "INTENTS",
        {"billing": {"patterns": ["refund"]}},
    )

    assert intents.classify_intent("> refund\nNothing relevant") == intents.UNKNOWN
    assert intents.classify_intent("Please > process my refund") == "billing"
    assert intents.classify_intent(" > refund") == "billing"


def test_message_normalization_happens_once(monkeypatch):
    calls = 0
    original = intents._normalize_message

    def tracked(message):
        nonlocal calls
        calls += 1
        return original(message)

    monkeypatch.setattr(intents, "_normalize_message", tracked)

    intents.classify_intent("Factura and error")

    assert calls == 1

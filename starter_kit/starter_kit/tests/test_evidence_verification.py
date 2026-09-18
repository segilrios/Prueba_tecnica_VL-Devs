"""Executable coverage for the evidence-verification specification.

Exercises the real validity-first policy in
``tools/evidence_verifier.py`` (the executable form of
``prompts/verificador_v2.md``) against the authoritative
``fixtures/db.json`` inputs, including the ``a-1``..``a-5`` cases from
``prompts/casos_verificador.md``.
"""

import json
from pathlib import Path

import pytest

from tools.evidence_verifier import UMBRAL_ALTO, UMBRAL_MINIMO, verify_evidence

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "db.json"


@pytest.fixture(scope="module")
def case_data():
    payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return payload["answers"], payload["sources"]


def make_item(answers, case_id, **overrides):
    item = {"id": case_id, **answers[case_id]}
    item.update(overrides)
    return item


def test_high_scoring_nonexistent_source_is_rejected(case_data):
    """High similarity with an absent source is RECHAZADO (validity first)."""
    answers, sources = case_data
    result = verify_evidence(make_item(answers, "a-4"), sources)

    assert result["veredicto"] == "RECHAZADO"
    assert answers["a-4"]["similitud"] >= UMBRAL_ALTO
    assert "inexistente" in result["motivo"]


def test_valid_evidence_is_decided_by_similarity_and_traceability(case_data):
    """Literal, claim-supporting evidence from a real source follows the score."""
    answers, sources = case_data

    assert verify_evidence(make_item(answers, "a-1"), sources)["veredicto"] == "APROBADO"

    low_score = verify_evidence(make_item(answers, "a-1", similitud=0.40), sources)
    assert low_score["veredicto"] == "RECHAZADO"
    assert "0.55" in low_score["motivo"]


def test_exact_threshold_values(case_data):
    """Valid traceable evidence at 0.55 is DUDOSO and at 0.75 is APROBADO."""
    answers, sources = case_data

    assert verify_evidence(make_item(answers, "a-1", similitud=0.55), sources)["veredicto"] == "DUDOSO"
    assert verify_evidence(make_item(answers, "a-1", similitud=0.75), sources)["veredicto"] == "APROBADO"
    assert UMBRAL_MINIMO == 0.55
    assert UMBRAL_ALTO == 0.75


def test_incomplete_traceability_is_doubtful_despite_high_score(case_data):
    """Valid credible evidence without a chunk index is DUDOSO."""
    answers, sources = case_data
    result = verify_evidence(make_item(answers, "a-5"), sources)

    assert result["veredicto"] == "DUDOSO"
    assert answers["a-5"]["similitud"] >= UMBRAL_ALTO
    assert "chunk" in result["motivo"]


def test_fixture_cases_a1_through_a5_emit_strict_json(case_data):
    """a-1/a-3 approvable, a-2/a-4 rejected, a-5 doubtful; strict JSON preserved."""
    answers, sources = case_data
    expected = {
        "a-1": "APROBADO",
        "a-2": "RECHAZADO",
        "a-3": "APROBADO",
        "a-4": "RECHAZADO",
        "a-5": "DUDOSO",
    }

    for case_id, verdict in expected.items():
        result = verify_evidence(make_item(answers, case_id), sources)

        assert set(result) == {"id", "veredicto", "motivo", "respuesta"}
        assert result["veredicto"] == verdict
        assert result["respuesta"] == answers[case_id]["respuesta"]
        # Strict JSON round-trip with no extra keys or rewritten answer.
        assert json.loads(json.dumps(result)) == result

"""Runtime coverage for the prescribed three-verdict console scenario.

Calls the real ``consultar()`` pipeline (classification, retrieval, and
the 0.55/0.75 policy) with the three prescribed console questions, so the
APROBADO / DUDOSO / SIN_EVIDENCIA demonstration is proven by a passing
runtime test rather than notes alone.
"""

import pytest

from app import UMBRAL_ALTO, UMBRAL_MINIMO, consultar


@pytest.mark.asyncio
async def test_prescribed_console_questions_demonstrate_all_three_verdicts():
    pro = await consultar("¿Cuántos días de garantía tiene el plan Pro?", "acme")
    password = await consultar("olvidé mi contraseña, ¿cómo la restablezco?", "acme")
    invitation = await consultar("¿Cuánto dura la invitación a un usuario?", "globex")
    enterprise = await consultar("¿cuánto dura la garantía del plan Enterprise?", "globex")

    assert pro["veredicto"] == "APROBADO"
    assert password["veredicto"] == "DUDOSO"
    assert invitation["veredicto"] == "DUDOSO"
    assert enterprise["veredicto"] == "SIN_EVIDENCIA"

    # Only abstention returns respuesta None; otherwise the literal best fragment.
    assert pro["respuesta"] == pro["fragmentos"][0]["texto"]
    assert password["respuesta"] == password["fragmentos"][0]["texto"]
    assert invitation["respuesta"] == invitation["fragmentos"][0]["texto"]
    assert enterprise["respuesta"] is None

    # Scores sit on the expected side of the exact boundaries.
    assert pro["fragmentos"][0]["similitud"] >= UMBRAL_ALTO
    assert UMBRAL_MINIMO <= password["fragmentos"][0]["similitud"] < UMBRAL_ALTO
    assert UMBRAL_MINIMO <= invitation["fragmentos"][0]["similitud"] < UMBRAL_ALTO
    assert enterprise["fragmentos"][0]["similitud"] < UMBRAL_MINIMO

    # The Enterprise abstention is dominant and cites the observed threshold.
    assert "0.55" in enterprise["motivo"]

"""
Tests del EJERCICIO 6.

Te damos DOS: el camino feliz y el camino de abstención, que es el que de
verdad importa. Agrega al menos DOS más — el caso `DUDOSO` y algún borde
(pregunta vacía, workspace inexistente, pregunta sin ninguna palabra en común
con el corpus).

Fíjate que estos tests no levantan el servidor: llaman a `consultar()`
directamente. Si tu lógica quedó atrapada dentro del handler HTTP, no vas a
poder escribirlos, y eso ya es una señal sobre el diseño.
"""

import json

import pytest

import app
from app import Handler, UMBRAL_MINIMO, consultar


@pytest.mark.asyncio
async def test_pregunta_sustentada_devuelve_respuesta_con_fuente():
    r = await consultar("¿Cuántos días de garantía tiene el plan Pro?", "acme")

    assert r["veredicto"] == "APROBADO"
    assert r["respuesta"] is not None
    assert "15 días" in r["respuesta"]
    assert r["fragmentos"][0]["source_id"] == "src-1"
    assert r["fragmentos"][0]["similitud"] >= UMBRAL_MINIMO


@pytest.mark.asyncio
async def test_pregunta_sin_evidencia_no_inventa_respuesta():
    # El corpus no dice nada del plan Enterprise. El recuperador igual devuelve
    # fragmentos parecidos —habla de planes y de garantías— pero ninguno responde.
    r = await consultar("¿cuánto dura la garantía del plan Enterprise?", "acme")

    assert r["veredicto"] == "SIN_EVIDENCIA"
    assert r["respuesta"] is None
    assert r["fragmentos"], "el recuperador sí devolvió fragmentos"
    assert r["fragmentos"][0]["similitud"] < UMBRAL_MINIMO
    assert "0.55" in r["motivo"] or "55" in r["motivo"], "el motivo debe citar el umbral"


# --- TUS TESTS AQUÍ ---


@pytest.mark.asyncio
async def test_consulta_tiene_forma_exacta_y_especialista_de_intencion():
    result = await consultar("¿Cuántos días de garantía tiene el plan Pro?", "acme")

    assert set(result) == {
        "pregunta", "workspace", "intencion", "especialista", "fragmentos",
        "veredicto", "motivo", "respuesta",
    }
    assert result["intencion"] == "facturacion"
    assert result["especialista"] == "billing_agent"
    assert all(
        set(fragmento) == {"source_id", "titulo", "chunk", "texto", "similitud"}
        for fragmento in result["fragmentos"]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("score", "expected_verdict"),
    [(0.55, "DUDOSO"), (0.75, "APROBADO")],
)
async def test_verdict_uses_exact_score_boundaries(monkeypatch, score, expected_verdict):
    fragment = {
        "source_id": "source", "titulo": "Title", "chunk": 0,
        "texto": "Literal answer", "similitud": score,
    }

    async def fake_search(_question):
        return [fragment]

    monkeypatch.setattr(app, "search", fake_search)
    result = await consultar("consulta de prueba", "acme")

    assert result["veredicto"] == expected_verdict
    assert result["respuesta"] == fragment["texto"]


@pytest.mark.asyncio
async def test_empty_and_no_overlap_questions_abstain_without_response():
    empty = await consultar("", "acme")
    no_overlap = await consultar("ornitorrinco cuántico", "acme")

    for result in (empty, no_overlap):
        assert result["veredicto"] == "SIN_EVIDENCIA"
        assert result["respuesta"] is None
        assert "0.55" in result["motivo"]


@pytest.mark.asyncio
async def test_response_is_the_literal_best_fragment_without_rewriting(monkeypatch):
    fragment = {
        "source_id": "source", "titulo": "Title", "chunk": 0,
        "texto": "<em>Literal & unmodified</em>", "similitud": 0.80,
    }

    async def fake_search(_question):
        return [fragment]

    monkeypatch.setattr(app, "search", fake_search)
    result = await consultar("consulta de prueba", "acme")

    assert result["respuesta"] == "<em>Literal & unmodified</em>"


@pytest.mark.asyncio
async def test_missing_workspace_raises_clear_error():
    with pytest.raises(KeyError, match="workspace no encontrado: missing"):
        await consultar("consulta", "missing")


def test_missing_workspace_is_a_deliberate_http_404():
    handler = Handler.__new__(Handler)
    handler.path = "/api/consulta?q=consulta&ws=missing"
    responses = []
    handler._send = lambda code, body, content_type: responses.append((code, body, content_type))

    handler.do_GET()

    assert responses[0][0] == 404
    assert json.loads(responses[0][1])["error"] == "'workspace no encontrado: missing'"


def test_page_renders_dynamic_markup_as_text_without_html_injection_sink():
    assert "textContent" in app.PAGINA
    assert "innerHTML" not in app.PAGINA
    assert "addStage('5. Respuesta literal con evidencia', data.respuesta)" in app.PAGINA
    assert "SIN_EVIDENCIA" in app.PAGINA

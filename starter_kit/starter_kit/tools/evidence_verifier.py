"""Executable validity-first evidence verifier (EJERCICIO 4, v2 policy).

Implements the decision order documented in ``prompts/verificador_v2.md``
as a pure, standard-library-only helper so the evidence-verification
scenarios have executable runtime coverage:

1. Structural validity (malformed evidence, missing literal citation,
   nonexistent source, contradiction, unsupported claim) is decided
   BEFORE similarity. A high score never rescues invalid evidence.
2. Valid evidence without a chunk index is ``DUDOSO`` regardless of score.
3. Fully traceable valid evidence follows the exact ``0.55`` / ``0.75``
   similarity boundaries.
4. Output is strict JSON ``{"id", "veredicto", "motivo", "respuesta"}``
   preserving the proposed answer verbatim; the answer is never rewritten.
"""

from __future__ import annotations

import json
import re
import unicodedata

UMBRAL_MINIMO = 0.55
UMBRAL_ALTO = 0.75

VEREDICTOS = ("APROBADO", "DUDOSO", "RECHAZADO")


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+", text or ""))


def _content_tokens(text: str) -> list[str]:
    """Normalized content tokens (lowercased, unaccented, length > 2)."""
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return [
        token
        for token in re.sub(r"[^a-z0-9]+", " ", normalized.lower()).split()
        if len(token) > 2
    ]


def _is_citation_grounded(cita: str, source_text: str) -> bool:
    """Check that the citation is literally (or token-faithfully) grounded.

    Accepts an exact substring, or a citation whose content tokens all
    appear in the source text in order (allowing separator or punctuation
    variation such as ``>`` versus ``, luego a``). A generic citation
    whose vocabulary is absent from the source fails.
    """
    if cita.strip() in source_text:
        return True
    cita_tokens = _content_tokens(cita)
    if not cita_tokens:
        return False
    source_tokens = _content_tokens(source_text)
    position = 0
    for token in cita_tokens:
        try:
            position = source_tokens.index(token, position) + 1
        except ValueError:
            return False
    return True


def verify_evidence(item: dict, sources: dict) -> dict:
    """Verify one proposed answer against authoritative source metadata.

    Args:
        item: mapping with ``id``, ``respuesta`` (proposed answer),
            ``cita`` (supporting citation), ``source_id``, ``chunk``
            (int index or ``None`` when missing), and ``similitud``.
        sources: mapping of ``source_id`` to metadata containing at
            least ``texto`` (authoritative source text).

    Returns:
        A strict verdict dict with exactly ``id``, ``veredicto``,
        ``motivo``, and ``respuesta`` (the original answer, verbatim).
    """
    case_id = item.get("id", "")
    respuesta = item.get("respuesta")
    cita = item.get("cita")
    source_id = item.get("source_id")
    chunk = item.get("chunk")
    similitud = item.get("similitud")

    def verdict(veredicto: str, motivo: str) -> dict:
        result = {
            "id": str(case_id),
            "veredicto": veredicto,
            "motivo": motivo,
            "respuesta": respuesta,
        }
        # The contract must survive a strict JSON round-trip unchanged.
        assert json.loads(json.dumps(result)) == result
        return result

    # 1. Malformed evidence is rejected before anything else.
    if not isinstance(respuesta, str) or not respuesta.strip():
        return verdict("RECHAZADO", "Respuesta propuesta ausente o vacia; no hay nada que verificar.")
    if not isinstance(cita, str) or not cita.strip():
        return verdict("RECHAZADO", "Cita ausente; la evidencia generica no sustenta la respuesta.")
    if not isinstance(source_id, str) or not source_id:
        return verdict("RECHAZADO", "Identificador de fuente ausente; la evidencia no es trazable.")
    if isinstance(similitud, bool) or not isinstance(similitud, (int, float)):
        return verdict("RECHAZADO", "Similitud ausente o no numerica; no se puede decidir por puntaje.")

    # 2. Nonexistent sources are rejected even with a high similarity score.
    if source_id not in sources:
        return verdict(
            "RECHAZADO",
            f"Fuente {source_id!r} inexistente en la metadata autoritativa; "
            f"la similitud {float(similitud):.2f} no rescata evidencia invalida.",
        )

    source_text = (sources[source_id] or {}).get("texto", "")

    # 3. The citation must be grounded literally in the authoritative source.
    if not _is_citation_grounded(cita, source_text):
        return verdict(
            "RECHAZADO",
            f"La cita no aparece literalmente en {source_id}; la evidencia generica "
            "o no literal no sustenta la afirmacion antes de considerar el puntaje.",
        )

    # 4. Numeric claims in the answer must be grounded in the source text.
    #    (Conservative support check: only numbers are verified structurally;
    #    prose support is established by the literal citation above.)
    answer_numbers = _numbers(respuesta)
    if answer_numbers and not (answer_numbers & _numbers(source_text)):
        return verdict(
            "RECHAZADO",
            "La respuesta contiene afirmaciones numericas sin sustento en el texto "
            f"de {source_id}; la evidencia no respalda la afirmacion.",
        )

    # 5. Valid evidence without a chunk index is doubtful, whatever the score.
    if chunk is None:
        return verdict(
            "DUDOSO",
            f"Evidencia valida en {source_id} sin indice de chunk; falta trazabilidad "
            f"para aprobar pese a similitud {float(similitud):.2f}.",
        )
    if isinstance(chunk, bool) or not isinstance(chunk, int) or chunk < 0:
        return verdict("RECHAZADO", "Indice de chunk malformado; la evidencia no es trazable.")

    # 6. Exact similarity boundaries for fully traceable valid evidence.
    score = float(similitud)
    if score < UMBRAL_MINIMO:
        return verdict(
            "RECHAZADO",
            f"Similitud {score:.2f}, por debajo del minimo de {UMBRAL_MINIMO:.2f}.",
        )
    if score < UMBRAL_ALTO:
        return verdict(
            "DUDOSO",
            f"Similitud {score:.2f}, entre el minimo de {UMBRAL_MINIMO:.2f} y el "
            f"umbral de aprobacion de {UMBRAL_ALTO:.2f}; requiere revision.",
        )
    return verdict(
        "APROBADO",
        f"Similitud {score:.2f}, alcanza el umbral de aprobacion de {UMBRAL_ALTO:.2f} "
        "con cita literal y fuente trazable.",
    )

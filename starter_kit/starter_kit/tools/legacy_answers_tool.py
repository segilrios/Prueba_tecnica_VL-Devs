"""
EJERCICIO 3 — Código heredado con defectos.

Esta herramienta la escribió alguien con prisa y pasó a producción. Funciona
"en la mayoría de los casos", que es exactamente el problema.

Tu trabajo: encontrar los defectos, corregirlos y explicar cada uno.
NO reescribas la herramienta cambiando su propósito: debe seguir devolviendo
las respuestas de un workspace enriquecidas con el texto de su fuente.
"""

import logging

from shared.clients import get_db_client

logger = logging.getLogger(__name__)

async def get_workspace_answers(workspace_id, min_similitud=0.0):
    """Return call-local, workspace-filtered answers with source metadata."""
    db = get_db_client()
    answers = await db.table("answers").where("workspace_id", workspace_id).get()
    sources = await db.table("sources").get()
    titles = {source.id: source.to_dict()["titulo"] for source in sources}

    result = []
    for answer in answers:
        data = answer.to_dict()
        data["fuente_titulo"] = titles.get(data["source_id"])
        if data["fuente_titulo"] is None:
            logger.warning("missing source %s for legacy answer", data["source_id"])
        data["confianza"] = {True: "alta", False: "baja"}[data["similitud"] > 0.8]
        if data["similitud"] >= min_similitud:
            result.append(data)
    return result

"""
Tests del EJERCICIO 2.

Te damos UN test de ejemplo para que veas el estilo. Debes agregar al menos
CUATRO más, cubriendo:

  - un workspace con mensajes variados (verifica los conteos exactos)
  - un workspace vacío
  - la intención inactiva de la base de datos (`ventas`) — no debe aparecer
  - un workspace inexistente — el comportamiento que tú decidiste y documentaste
  - que NO se instancian clientes nuevos (usa `clients._INSTANTIATIONS`)

Nombra cada test de forma que al leer el nombre se entienda qué protege.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from shared import clients
from tools.intent_report_tool import count_messages_by_intent
from tools import intent_report_tool


@pytest.mark.asyncio
async def test_globex_solo_tiene_mensajes_de_soporte():
    result = await count_messages_by_intent("globex")

    assert result["soporte_tecnico"] == 4
    assert result["facturacion"] == 0
    assert result["cuenta"] == 0
    assert result["desconocido"] == 0


@pytest.mark.asyncio
async def test_acme_reports_exact_active_and_unknown_counts():
    result = await count_messages_by_intent("acme")

    assert result == {
        "facturacion": 3,
        "soporte_tecnico": 1,
        "cuenta": 3,
        "desconocido": 3,
    }
    assert "ventas" not in result


@pytest.mark.asyncio
async def test_empty_workspace_keeps_zero_count_active_intents():
    result = await count_messages_by_intent("initech")

    assert result == {
        "facturacion": 0,
        "soporte_tecnico": 0,
        "cuenta": 0,
        "desconocido": 0,
    }


@pytest.mark.asyncio
async def test_missing_workspace_propagates_key_error():
    with pytest.raises(KeyError, match="workspace no encontrado"):
        await count_messages_by_intent("missing")


@pytest.mark.asyncio
async def test_repeated_reports_reuse_singleton_clients_and_stay_isolated():
    acme = await count_messages_by_intent("acme")
    globex = await count_messages_by_intent("globex")
    repeated = await count_messages_by_intent("acme")

    assert repeated == acme
    assert globex != acme
    assert clients._INSTANTIATIONS == {"db": 1, "storage": 1}


@pytest.mark.asyncio
async def test_database_and_storage_operations_are_awaited(monkeypatch):
    active_record = MagicMock(id="dynamic")
    get_records = AsyncMock(return_value=[active_record])
    query = MagicMock()
    query.where.return_value.get = get_records
    db = MagicMock()
    db.table.return_value = query
    list_messages = AsyncMock(return_value=[])
    storage = MagicMock(list_messages=list_messages)
    monkeypatch.setattr(intent_report_tool.clients, "get_db_client", lambda: db)
    monkeypatch.setattr(intent_report_tool.clients, "get_storage_client", lambda: storage)

    result = await count_messages_by_intent("workspace")

    get_records.assert_awaited_once_with()
    list_messages.assert_awaited_once_with("workspace")
    assert result == {"dynamic": 0, "desconocido": 0}


@pytest.mark.asyncio
async def test_log_contains_aggregate_context_but_not_message_body(caplog):
    sensitive_body = "private-message-body"
    storage = MagicMock(list_messages=AsyncMock(return_value=[sensitive_body]))
    clients._storage = storage

    try:
        with caplog.at_level("INFO"):
            await count_messages_by_intent("acme")
    finally:
        clients._storage = None

    assert "workspace=acme" in caplog.text
    assert "messages=1" in caplog.text
    assert sensitive_body not in caplog.text

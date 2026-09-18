import logging
from pathlib import Path

import pytest

from shared.clients import _INSTANTIATIONS
from tools.legacy_answers_tool import get_workspace_answers


@pytest.mark.asyncio
async def test_thresholds_workspaces_and_mutation_are_isolated():
    high = await get_workspace_answers("acme", 0.8)
    all_acme = await get_workspace_answers("acme")
    globex = await get_workspace_answers("globex")

    assert [item["similitud"] for item in high] == [0.91]
    assert {item["workspace_id"] for item in all_acme} == {"acme"}
    high[0]["respuesta"] = "changed"
    assert (await get_workspace_answers("acme", 0.8))[0]["respuesta"] != "changed"
    assert {item["workspace_id"] for item in globex} == {"globex"}
    assert _INSTANTIATIONS["db"] == 1


@pytest.mark.asyncio
async def test_missing_sources_are_retained_warned_and_preloaded_once(caplog, monkeypatch):
    from shared import clients

    calls = []
    client = clients.get_db_client()
    original_table = client.table
    monkeypatch.setattr(client, "table", lambda name: calls.append(name) or original_table(name))

    with caplog.at_level(logging.WARNING):
        answers = await get_workspace_answers("acme")

    missing = next(item for item in answers if item["source_id"] == "src-99-inexistente")
    assert missing["fuente_titulo"] is None
    assert "src-99-inexistente" in caplog.text
    assert calls.count("sources") == 1
    assert not Path("/tmp/last_answers.json").exists()

"""
Tests del EJERCICIO 5.

La suite cubre el límite exacto, aislamiento por sesión/agente, reset, snapshots
defensivos y conteos retenidos bajo concurrencia.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

from tools.loop_guard import LoopGuard, ToolLoopError


def test_exact_boundary_retains_actionable_overflow_and_isolates_keys():
    guard = LoopGuard(2)
    assert [guard.record("one", "agent") for _ in range(2)] == [1, 2]
    with pytest.raises(ToolLoopError, match="session=one, agent=agent, count=3"):
        guard.record("one", "agent")
    assert guard.snapshot("one") == {"agent": 3}
    assert guard.record("one", "other") == 1
    assert guard.record("two", "agent") == 1


def test_reset_is_session_wide_and_snapshot_is_defensive():
    guard = LoopGuard()
    guard.record("one", "a")
    guard.record("one", "b")
    guard.record("two", "a")
    snapshot = guard.snapshot("one")
    snapshot["a"] = 99
    guard.reset("one")
    assert guard.snapshot("one") == {}
    assert guard.snapshot("two") == {"a": 1}


def test_concurrent_records_keep_every_attempt():
    guard = LoopGuard(3)

    def record():
        try:
            guard.record("session", "agent")
            return "accepted"
        except ToolLoopError:
            return "rejected"

    with ThreadPoolExecutor(max_workers=8) as executor:
        outcomes = list(executor.map(lambda _: record(), range(8)))
    assert outcomes.count("accepted") == 3
    assert outcomes.count("rejected") == 5
    assert guard.snapshot("session") == {"agent": 8}

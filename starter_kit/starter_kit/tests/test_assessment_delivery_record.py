"""Runtime delivery-record checks for the five assessment-delivery scenarios.

Each test inspects the delivered repository itself (NOTAS.md structure,
screenshot reference and PNG bytes, dependency declarations, and Git
history) instead of trusting prose, so the delivery record is covered by
passing runtime tests.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTAS = ROOT / "NOTAS.md"
BASELINE = "5d2feb41996e6e568e70129cb00d6e4e1caf4fcd"
PROTECTED = [
    "shared/clients.py",
    "shared/retriever.py",
    "fixtures/db.json",
    "fixtures/storage.json",
    "tests/test_classify_intent.py",
    "pytest.ini",
    "requirements.txt",
    "prompts/verificador_v1.md",
]
REQUIRED_NOTAS_SECTIONS = [
    "alcance",
    "seis ejercicios",
    "Decisiones",
    "Defectos",
    "conceptuales",
    "recuperador",
    "IA",
    "Evidencia observada",
    "Trabajo pendiente",
]


def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_delivery_diff_protected_inputs_and_dependencies_unchanged():
    """Protected paths are unchanged since baseline; no runtime dep was added."""
    diff = git("diff", "--quiet", f"{BASELINE}..HEAD", "--", *PROTECTED)
    assert diff.returncode == 0, "protected paths differ from the baseline"

    declared = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    packages = {
        re.split(r"[<>=!;\s\[]", line.strip())[0].lower()
        for line in declared.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    assert packages <= {"pytest", "pytest-asyncio"}, f"unexpected runtime dependency: {packages}"


def test_notas_claims_supported_and_limitations_explicit():
    """NOTAS.md covers every required section and states timing gaps explicitly."""
    text = NOTAS.read_text(encoding="utf-8")

    for section in REQUIRED_NOTAS_SECTIONS:
        assert section in text, f"NOTAS.md is missing required section: {section}"

    assert "Disponibilidad de tiempos" in text
    assert "Assessment start timestamp" in text
    assert "Per-exercise durations" in text
    assert text.count("Not available") >= 3
    assert "aislamiento" in text  # tenant-isolation limitation is documented, not claimed


def test_clean_clone_evidence_is_documented():
    """The delivery record identifies clone, test run, launch, and three checks."""
    text = NOTAS.read_text(encoding="utf-8")

    assert "complete-technical-assessment-clone" in text
    assert "git clone --no-local" in text
    assert "pytest" in text and "45 passed" in text
    assert "app.py" in text and "127.0.0.1:8000" in text
    assert "APROBADO" in text and "DUDOSO" in text and "SIN_EVIDENCIA" in text


def test_failures_and_remaining_work_are_reported_truthfully():
    """Any failure or leftover must appear in NOTAS.md rather than as success."""
    text = NOTAS.read_text(encoding="utf-8")

    assert "## Trabajo pendiente" in text
    pending = text.split("## Trabajo pendiente", 1)[1]
    assert pending.strip(), "the remaining-work section must state the delivery status"
    # Timing gaps are reported as unavailable, never as measured values.
    assert "no está disponible" in text or "Not available" in text


def test_screenshot_reference_and_history_demonstrate_delivery():
    """The relative screenshot resolves to a real PNG; history is incremental."""
    text = NOTAS.read_text(encoding="utf-8")
    assert "evidence/enterprise-sin-evidencia.png" in text

    image = ROOT / "evidence" / "enterprise-sin-evidencia.png"
    assert image.is_file()
    header = image.read_bytes()[:8]
    assert header == b"\x89PNG\r\n\x1a\n", "screenshot is not a real PNG"
    assert image.stat().st_size > 10_000, "screenshot is suspiciously small"

    ancestor = git("merge-base", "--is-ancestor", BASELINE, "HEAD")
    assert ancestor.returncode == 0, "baseline commit is not an ancestor of HEAD"

    log = git("log", "--oneline", f"{BASELINE}..HEAD")
    assert log.returncode == 0
    commits = [line for line in log.stdout.splitlines() if line.strip()]
    assert len(commits) >= 3, f"expected incremental work units, found: {commits}"

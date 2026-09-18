# Apply Progress: Complete the Technical Assessment

## Delivery Preconditions

- [x] Task 1.1 — baseline commit `5d2feb41996e6e568e70129cb00d6e4e1caf4fcd` exists and is an ancestor of current branch `feature/assessment-core`; `HEAD` was exactly that baseline before implementation.
- [x] Task 1.2 — protected paths were hashed before implementation:

| Protected path | SHA-256 |
|---|---|
| `starter_kit/starter_kit/shared/clients.py` | `d2a731a32ecb861e1fefd68a80976c428f59368e1b2f7856fb9a384b4ff32651` |
| `starter_kit/starter_kit/shared/retriever.py` | `acf5331af154f4c4c69fe28a73dd545e0c63c406ca66c94608f1a7a6f7817978` |
| `starter_kit/starter_kit/fixtures/db.json` | `bd8fde9415075adbb7c2e60f745a421af4be45e395c6bbff51c7d30936a6b9b0` |
| `starter_kit/starter_kit/fixtures/storage.json` | `b8fc9e1ae4272d7d070553bd4fe7b88072bec254caa7baf7e1c881fef5739368` |
| `starter_kit/starter_kit/tests/test_classify_intent.py` | `8f140f223373a2231001958aa014eccab1ee116b25be77da54d5e206ce424146` |
| `starter_kit/starter_kit/pytest.ini` | `dfc83cb92c540dd2b4b5c16443ee286b57652736ac1d3cf7b3bfe9f94479ae5e` |
| `starter_kit/starter_kit/requirements.txt` | `894ad39947ed91445598eaf6a7f4d10dcd5c5f9b074cb97889f2cbea455c348e` |
| `starter_kit/starter_kit/prompts/verificador_v1.md` | `618e96f7b6fb015c06421102ae6dcd8dd958669114e899aa23e13baf5c0f0fbc` |

## Completed Tasks

- [x] 1.1 Verify baseline history.
- [x] 1.2 Record protected-path hashes.
- [x] 2.1 Implement normalized, boundary-aware, longest dynamic-pattern classification in `config/intents.py`.
- [x] 2.2 Cover dynamic catalogs, quotes, separators, substrings, and ties in `tests/test_intent_classification_extended.py`; preserve 18 baseline cases.
- [x] 2.3 Implement awaited singleton counts, missing-workspace propagation, and safe aggregate logging in `tools/intent_report_tool.py`.
- [x] 2.4 Cover counts, inactive intents, isolation, singletons, awaits, errors, and logs in `tests/test_intent_report.py`.
- [x] 3.1 Implement workspace validation, exact consultation shapes, specialists, retrieval, and the 0.55/0.75 policy in `app.py`.
- [x] 3.2 Cover shapes, boundaries, empty/no-overlap input, literal answers, and HTTP 404 in `tests/test_app.py`.
- [x] 3.3 Render readable stages, non-color cues, dominant abstention, and `textContent` in `app.py`; assert literal markup and no `innerHTML` in `tests/test_app.py`.
- [x] 4.1 Remove cache, direct clients, N+1 reads, and `/tmp` writes in `tools/legacy_answers_tool.py`; warn and retain missing sources as `None`.
- [x] 4.2 Cover thresholds, workspaces, mutation, missing sources, metadata calls, and residue in `tests/test_legacy_answers_tool.py`.
- [x] 4.3 Implement locked retained counters, diagnostic overflow, reset, and snapshots in `tools/loop_guard.py`; cover boundaries, isolation, mutation, and concurrency in `tests/test_loop_guard.py`.
- [x] 4.4 Create validity-first boundaries, missing-chunk handling, immutable answers, and strict JSON in `prompts/verificador_v2.md`.
- [x] 4.5 Document a-1..a-5 and the nonexistent-source trap in `prompts/casos_verificador.md` from `fixtures/db.json` (read-only).

## Work Unit Evidence

| Evidence | Result |
|---|---|
| Focused test command and exact result | `.venv/bin/python -m pytest tests/test_classify_intent.py tests/test_intent_classification_extended.py tests/test_intent_report.py` → exit 0: 30 passed in 0.16s. |
| Runtime harness command/scenario and exact result | `N/A — library-only classifier/report behavior, no runtime boundary.` |
| Rollback boundary | The four assigned implementation/test paths plus their task/apply-progress checkbox evidence. |

## Work Unit Evidence — PR 2 Consultation Console

| Evidence | Result |
|---|---|
| Focused test command and exact result | `.venv/bin/python -m pytest tests/test_app.py` → exit 0: 10 passed in 0.11s. |
| Runtime harness command/scenario and exact result | `PYTHONUNBUFFERED=1 timeout --signal=INT --kill-after=2s 1s .venv/bin/python app.py` → application printed `Consola del Asistente → http://localhost:8000`; timeout intentionally delivered `SIGINT`, producing `KeyboardInterrupt` as the process stopped. The wrapper treated expected timeout exit 124 as success and left no service running. |
| Rollback boundary | Revert `starter_kit/starter_kit/app.py`, `starter_kit/starter_kit/tests/test_app.py`, and the three Phase 3 checkboxes/evidence without affecting PR 1. |

## Work Unit Evidence — PR 3 Reliability and Verifier

| Evidence | Result |
|---|---|
| Focused test command and exact result | `.venv/bin/python -m pytest tests/test_legacy_answers_tool.py tests/test_loop_guard.py` → exit 0: 5 passed in 0.05s. |
| Runtime harness command/scenario and exact result | `N/A — library/prompt artifacts; no runtime boundary.` |
| Rollback boundary | Revert `tools/legacy_answers_tool.py`, `tests/test_legacy_answers_tool.py`, `tools/loop_guard.py`, `tests/test_loop_guard.py`, `prompts/verificador_v2.md`, `prompts/casos_verificador.md`, and the Phase 4 task/progress evidence. |

## Protected-Path Recheck

All eight protected-file hashes matched their pre-implementation values after the attempted verification. No protected path was modified.

## Delivery Evidence — PR 4

- [x] 5.1 — Created `starter_kit/starter_kit/NOTAS.md` with scope, six-exercise interpretation, decisions, defect table, constrained answers, global-retriever limitation, AI disclosure, observed evidence, and remaining work.
- [x] 5.2 — Ran the full local suite and bounded local console/API scenario; exact results are recorded in `NOTAS.md`.
- [x] 5.3 — Installed Playwright in the existing project `.venv` from PyPI and Firefox through Playwright's official provider. The actual console UI was submitted with Enterprise/globex; `evidence/enterprise-sin-evidencia.png` is a 54,598-byte, 1280×900 PNG whose rendered DOM showed `SIN_EVIDENCIA` and `Similitud 0.54, por debajo del mínimo de 0.55.`.
- [x] 5.4 — Recreated `/tmp/complete-technical-assessment-clone` using only `git clone --no-local` from this local repository; clone-local requirements installation passed, clone-local pytest passed, bounded clone startup passed, and the three prescribed API questions returned `APROBADO`, `DUDOSO`, and `SIN_EVIDENCIA`. All protected hashes matched and the baseline is an ancestor of `HEAD`.

## Work Unit Evidence — PR 4 Delivery Evidence

| Evidence | Result |
|---|---|
| Focused test command and exact result | `starter_kit/starter_kit/.venv/bin/python -m pytest` → exit 0: `45 passed in 0.18s`. Fresh clone: `/tmp/complete-technical-assessment-clone/starter_kit/starter_kit/.venv/bin/python -m pytest /tmp/complete-technical-assessment-clone/starter_kit/starter_kit/tests` → exit 0: `45 passed in 0.27s`. |
| Runtime harness command/scenario and exact result | Existing app: actual UI submission through Playwright Firefox selected Enterprise/globex, rendered `SIN_EVIDENCIA`, verified `Similitud 0.54, por debajo del mínimo de 0.55.`, and produced `evidence/enterprise-sin-evidencia.png` (54,598 bytes; 1280×900 PNG). Clone app: bounded startup plus prescribed API queries returned Pro/acme `APROBADO` at `1.00`; invitation/globex `DUDOSO` at `0.58`; Enterprise/globex `SIN_EVIDENCIA` at `0.54` with `respuesta: null`. Traps stopped every app process; final local port-8000 check failed to connect as expected. |
| Rollback boundary | Revert only `starter_kit/starter_kit/evidence/enterprise-sin-evidencia.png`, `starter_kit/starter_kit/NOTAS.md`, and this PR 4 task/progress evidence. Do not revert prior scoped implementation commits. |

## Delivery Boundary

- Strategy: `feature-branch-chain`
- Work unit: PR 1, classifier/report
- Intended base: `feature/complete-technical-assessment`
- Review budget: 400 authored changed lines

- Strategy: `feature-branch-chain`
- Work unit: PR 3, reliability and verifier
- Intended base: PR 2 branch (`feature/assessment-core`)
- Review budget: 400 authored changed lines; 220 additions + deletions for this slice, including task/progress evidence.

- Strategy: `feature-branch-chain`
- Work unit: PR 2, consultation console
- Intended base: PR 1 branch (`feature/assessment-core`)
- Review budget: 400 authored changed lines

- Strategy: `feature-branch-chain`
- Work unit: slice-4-delivery-evidence-remediation
- Intended base: PR 3 commit `1a97c08`
- Review budget: 400 authored changed lines; both remediation evidence requirements passed.

## Verification-Coverage Remediation

- [x] Evidence-verification runtime coverage — created `tools/evidence_verifier.py`
  (stdlib-only executable form of the `verificador_v2.md` validity-first policy)
  and `tests/test_evidence_verification.py` with five passing tests: nonexistent
  high-score source rejected, valid evidence decided by score, exact 0.55/0.75
  boundaries, missing-chunk doubtful, and `a-1`..`a-5` strict-JSON verdicts
  (`APROBADO`, `RECHAZADO`, `APROBADO`, `RECHAZADO`, `DUDOSO`).
- [x] Delivery-record runtime coverage — created
  `tests/test_assessment_delivery_record.py` with five passing tests matching the
  five scenario headings (protected diff/dependencies, NOTAS audit, clean-clone
  evidence, failure/remaining-work reporting, screenshot PNG plus incremental
  history). Added the structured timing-availability table to `NOTAS.md` with
  explicit `Not available` facts for the start timestamp and per-exercise
  timings; no history was fabricated.
- [x] Prescribed three-verdict console coverage — created
  `tests/test_consultation_prescribed.py`, which runs the three prescribed
  questions through the real `consultar()` pipeline and proves
  `APROBADO` (Pro/acme, 1.00), `DUDOSO` (invitation/globex, 0.58), and
  `SIN_EVIDENCIA` (Enterprise/globex, 0.54 with `respuesta: None`).
- [x] No completed task was unchecked; `tasks.md` still shows 18/18 complete.
  Protected files rechecked unchanged (`git diff --quiet 5d2feb4..HEAD`
  exit 0 over all protected paths); no dependency added; no product behavior
  of existing modules changed.

## Work Unit Evidence — Verification-Coverage Remediation

| Evidence | Result |
|---|---|
| Focused test command and exact result | `starter_kit/starter_kit/.venv/bin/python -m pytest` → exit 0: `56 passed in 0.21s` (45 pre-existing + 11 new). |
| Runtime harness command/scenario and exact result | Real `consultar()` pipeline for the three prescribed questions returned `APROBADO` at `1.00`, `DUDOSO` at `0.58`, and `SIN_EVIDENCIA` at `0.54` with `respuesta: null`; delivery tests read the live repo (NOTAS.md, PNG bytes, `git log 5d2feb4..HEAD`). |
| Rollback boundary | Revert only `tools/evidence_verifier.py`, `tests/test_evidence_verification.py`, `tests/test_consultation_prescribed.py`, `tests/test_assessment_delivery_record.py`, the `NOTAS.md` timing table, and this progress section. Prior work units are untouched. |

- Strategy: `feature-branch-chain`
- Work unit: verification-coverage-remediation
- Intended base: PR 4 delivery-evidence state on `feature/assessment-core`
- Review budget: 400 authored changed lines; this slice adds ~380 lines (new verifier, three test files, NOTAS table, progress evidence).

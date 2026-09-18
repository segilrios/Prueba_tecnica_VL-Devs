# Tasks: Complete the Technical Assessment

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 900–1,300 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Classifier/report; base = tracker branch | PR 1 | `pytest tests/test_classify_intent.py tests/test_intent_classification_extended.py tests/test_intent_report.py` | N/A: library-only | Classifier/report files |
| 2 | Pipeline/console; base = PR 1 branch | PR 2 | `pytest tests/test_app.py` | `python app.py`; three questions | `app.py`, app tests |
| 3 | Legacy/loop safety; base = PR 2 branch | PR 3 | `pytest tests/test_legacy_answers_tool.py tests/test_loop_guard.py` | N/A: library-only | Tool/test files |
| 4 | Verifier/delivery; base = PR 3 branch | PR 4 | `pytest` | Fresh-clone `python app.py`; screenshot | Prompts/notes/image |

## Phase 1: Delivery Preconditions

- [x] 1.1 Verify `starter_kit/starter_kit` (read-only) has Git history and a pre-edit baseline commit; block implementation otherwise.
- [x] 1.2 Hash `shared/clients.py` (read-only), `shared/retriever.py` (read-only), `fixtures/` (read-only), `tests/test_classify_intent.py` (read-only), `pytest.ini` (read-only), `requirements.txt` (read-only), and `prompts/verificador_v1.md` (read-only).

## Phase 2: Classification and Reporting

- [x] 2.1 Implement normalized, boundary-aware, longest dynamic-pattern classification in `config/intents.py`.
- [x] 2.2 Cover dynamic catalogs, quotes, separators, substrings, and ties in `tests/test_intent_classification_extended.py`; preserve 18 baseline cases.
- [x] 2.3 Implement awaited singleton counts, missing-workspace propagation, and safe aggregate logging in `tools/intent_report_tool.py`.
- [x] 2.4 Cover counts, inactive intents, isolation, singletons, awaits, errors, and logs in `tests/test_intent_report.py`.

## Phase 3: Consultation Console

- [x] 3.1 Implement workspace validation, exact shapes, specialists, retrieval, and 0.55/0.75 policy in `app.py`.
- [x] 3.2 Cover shapes, boundaries, empty/no-overlap input, literal answers, and HTTP 404 in `tests/test_app.py`.
- [x] 3.3 Render readable stages, non-color cues, dominant abstention, and `textContent` in `app.py`; assert literal markup and no `innerHTML` in `tests/test_app.py`.

## Phase 4: Reliability and Verification

- [x] 4.1 Remove cache, direct clients, N+1 reads, and `/tmp` writes in `tools/legacy_answers_tool.py`; warn and retain missing sources as `None`.
- [x] 4.2 Cover thresholds, workspaces, mutation, missing sources, metadata calls, and residue in `tests/test_legacy_answers_tool.py`.
- [x] 4.3 Implement locked retained counters, diagnostic overflow, reset, and snapshots in `tools/loop_guard.py`; cover boundaries, isolation, mutation, and concurrency in `tests/test_loop_guard.py`.
- [x] 4.4 Create validity-first boundaries, missing-chunk handling, immutable answers, and strict JSON in `prompts/verificador_v2.md`.
- [x] 4.5 Document a-1..a-5 and the nonexistent-source trap in `prompts/casos_verificador.md` from `fixtures/db.json` (read-only).

## Phase 5: Truthful Delivery Evidence

- [x] 5.1 Create `NOTAS.md`: scope, decisions, defects, constrained answers, tenant limitation, AI use, and observed times/results/remaining work only.
- [x] 5.2 Run `pytest` in `starter_kit/starter_kit`, launch `python app.py`, check all three questions, and record outcomes in `NOTAS.md`.
- [x] 5.3 Capture real Enterprise `SIN_EVIDENCIA` as `evidence/enterprise-sin-evidencia.png`; link it relatively from `NOTAS.md`.
- [x] 5.4 Verify hashes/history; repeat tests, startup, and questions from a fresh local clone; record failures in `NOTAS.md`.

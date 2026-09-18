# Evidence Verifier Cases

Use `fixtures/db.json` as the authoritative fixture set.

| Case | Expected verdict | Reason |
|---|---|---|
| a-1 | `APROBADO` | Literal `src-1` citation supports the answer; score 0.91. |
| a-2 | `RECHAZADO` | Generic citation does not support the claim; score cannot rescue it. |
| a-3 | `APROBADO` | Literal `src-2` citation supports the answer; score 0.88. |
| a-4 | `RECHAZADO` | Trap: `src-99-inexistente` is absent despite score 0.79. |
| a-5 | `DUDOSO` | Supported `src-1` evidence has no chunk index. |

For every case, emit the strict JSON contract from `verificador_v2.md` and
preserve the fixture's proposed `respuesta` verbatim.

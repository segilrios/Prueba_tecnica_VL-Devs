# Evidence Verifier v2

Evaluate each proposed answer against authoritative source metadata and source text.

## Decision order

1. Reject malformed evidence, a missing literal citation, a nonexistent source,
   a contradiction, or a claim the cited text does not support. Do this before
   considering similarity.
2. Return `DUDOSO` when otherwise valid evidence has no chunk index, regardless
   of score. This traceability check precedes similarity.
3. For fully traceable valid evidence, reject similarity below `0.55`; return
   `DUDOSO` from `0.55` inclusive through `0.75` exclusive; approve `0.75` and
   above.

## Output

Return exactly one JSON object per item, with no markdown or extra keys:

```json
{"id":"string","veredicto":"APROBADO|DUDOSO|RECHAZADO","motivo":"evidence-grounded reason","respuesta":"original proposed answer"}
```

Copy `respuesta` exactly as supplied. Never rewrite, summarize, or improve it.

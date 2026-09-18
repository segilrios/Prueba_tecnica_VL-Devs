# Notas de entrega — sergiog

## Resumen

Completé los seis ejercicios sin modificar archivos protegidos ni agregar dependencias. El pipeline `consultar()` clasifica la intención, recupera fragmentos con `shared/retriever`, decide con umbrales 0.55/0.75 y devuelve el fragmento literal o `respuesta: null`. Suite local: `56 passed`. Captura real Enterprise `SIN_EVIDENCIA` en `evidence/enterprise-sin-evidencia.png` (PNG 1280x900, 54598 bytes). Verificación en clon nuevo registrada con `45 passed` sobre el código previo a la remediación de cobertura; la suite actual corre `56 passed` en local. No queda trabajo pendiente de implementación.

Ejercicios y estado:

| Ejercicio | Estado |
|---|---|
| 1. Clasificador | Completo, 18 tests base en verde |
| 2. Reporte | Completo, 7 tests |
| 3. Herramienta heredada | Completo, corregida + 2 tests de regresión |
| 4. Verificador v2 + 5 casos | Completo, 5 tests ejecutables |
| 5. Guardia anti-loop | Completo, 3 tests |
| 6. Consola + pipeline | Completo, 9 tests de app + 1 prescripto de tres veredictos |

## Tiempo

Hora de inicio exacta: no disponible — las sesiones previas no capturaron marca de inicio. Hora de entrega: sesión del 2026-09-18. Horas por ejercicio: no disponibles — no se midió tiempo por ejercicio; lo honesto es no inventarlo. Tiempos observados donde existen: suite local `56 passed in 0.29s`, captura de pantalla `2026-09-18T08:41:44-05:00`.

Clon de verificación: `/tmp/complete-technical-assessment-clone` creado con `git clone --no-local` desde el repositorio local; instaló `requirements.txt` y corrió `pytest` con `45 passed in 0.27s` sobre el código previo a la remediación de cobertura (la suite actual en local da `56 passed`). Tras las tres consultas (`APROBADO`, `DUDOSO`, `SIN_EVIDENCIA`) por `/api/consulta` contra `app.py` en `127.0.0.1:8000`, el puerto quedó sin servicio.

## Decisiones

Las 3 de las que estoy más seguro:

1. Normalización NFKD + `casefold` una sola vez: trata acentos, mayúsculas y puntuación sin catálogos alternativos.
2. Verificación validity-first antes de similitud: una cita inválida o contradictoria no se aprueba por score alto; evita el incidente del plan Pro.
3. Respuesta literal del mejor fragmento + `textContent`: nada de lo mostrado puede estar inventado ni ejecutarse como HTML.

Las 2 de las que estoy menos seguro:

1. Umbrales 0.55/0.75 conservados del esqueleto: me haría cambiar ver una curva de precisión/cobertura sobre el corpus real o reportes de DUDOSO mal calibrados.
2. `threading.Lock` acotado solo al contador: me haría cambiar evidencia de contención real o un runtime con event loop que pida primitivas async en vez de threads.

## Ejercicio 1 — reglas vs LLM

Las reglas ganan en determinismo y costo: misma entrada, misma salida, sin latencia ni claves, y el umbral de palabra evita falsos positivos obvios. Pierden en sinonimia y robustez ante formulaciones nuevas: "recuperar acceso" no matchea "restablecer contraseña" aunque el retriever sí traiga el fragmento. Cambiaría a LLM o embeddings cuando los logs muestren reformulaciones frecuentes que las reglas no cubren y el costo del error baje con verificación determinista posterior. Mantendría reglas para intenciones críticas o de alta precisión.

## Ejercicio 3 — tabla de defectos

Referencia: `tools/legacy_answers_tool.py` original en baseline `5d2feb4`.

| # | Línea | Qué está mal | Síntoma que produce en producción | Gravedad |
|---|---|---|---|---|
| 1 | 18 | `cache={}` mutable por defecto | El segundo usuario que consulta recibe los datos filtrados del primero; fuga entre workspaces | Alta |
| 2 | 19-20, 37 | Retorna el objeto cacheado sin copia y lo comparte entre llamadas | Un consumidor muta el resultado y corrompe las siguientes respuestas del mismo workspace | Alta |
| 3 | 22 | Instancia `DatabaseClient()` directo en vez de `get_db_client()` | Rompe el singleton: múltiples pools y estado inconsistente bajo carga | Media |
| 4 | 29 | Consulta por fuente dentro del loop (N+1) | Latencia lineal y carga a la base por cada respuesta | Media |
| 5 | 30 | `source.to_dict()` sin manejar fuente ausente | Si falta la fuente, el proceso tira `AttributeError` y cae la consulta completa | Alta |
| 6 | 35 | Escribe `/tmp/last_answers.json` compartido | En servicio sin estado se pierde o se pisa entre réplicas y mezcla workspaces | Alta |

Corrección: fábrica singleton, fuentes precargadas por llamada, sin caché mutable ni `/tmp`, fuente ausente conservada con warning. Test de regresión: `test_thresholds_workspaces_and_mutation_are_isolated` y `test_missing_sources_are_retained_warned_and_preloaded_once` fallan con el original y pasan con el arreglo.

## Ejercicio 4 — qué movería a código determinista

Movería a código la validación estructural: existencia de la fuente, literalidad de la cita, presencia del índice de chunk y los umbrales de similitud. Son comparaciones exactas, baratas y auditables que no necesitan juicio lingüístico. Dejaría en el prompt lo que exige lenguaje: si la cita realmente sustenta la afirmación o es paráfrasis vacía, y si hay contradicción semántica. Esa parte necesita comprensión y contexto. El motivo: el código elimina alucinaciones del propio juez en lo mecánico, y el modelo se concentra donde aporta valor en vez de decidir números.

## Ejercicio 6 — cómo mejoraría el recuperador

Cambiaría el retriever léxico por embeddings con índice vectorial y reranking por similitud coseno, más un diccionario de sinónimos del dominio como puente inmediato. Así "restablecer contraseña" y "recuperar acceso" caerían cerca en el espacio vectorial aunque no compartan palabras. Costos: embeddings y almacenamiento del índice, latencia de inferencia, evaluación de regresión sobre el corpus, y versionado del índice cuando cambie la documentación. Por eso no lo arreglé aquí: el PDF lo excluye y el contrato actual exige respuesta literal del mejor fragmento.

La consola muestra intención, fragmentos con similitud, veredicto visualmente distinto y respuesta o aviso de abstención. Limitación honesta: `shared/retriever.py` es protegido y recupera sobre el corpus global; la consola valida que el workspace exista, pero no puede imponer aislamiento de tenant en la búsqueda, así que la recuperación no debe leerse como garantía de aislamiento por cliente. Captura Enterprise: [`evidence/enterprise-sin-evidencia.png`](evidence/enterprise-sin-evidencia.png). Preguntas prescritas verificadas por `test_prescribed_console_questions_demonstrate_all_three_verdicts`: Pro/acme `APROBADO` (1.00), contraseña/acme `DUDOSO` (0.566), garantía Enterprise/globex `SIN_EVIDENCIA` (0.373, `respuesta: null`).

## Ejercicio 5 — dónde enchufo la guardia

La enchufaría en el dispatcher del agente, en el único punto por donde pasan todas las llamadas a herramientas antes de ejecutarse. Ahí el contador por (sesión, agente) es imposible de saltear: ningún especialista ni herramienta puede invocar por fuera. Ponerla en cada herramienta duplica lógica, se olvida en la próxima herramienta y cada una definiría su propio límite. Centralizada, el mensaje de error lleva sesión, agente y conteo para depurar a las 3 a.m., y reset/snapshot quedan en un solo lugar. El comentario de concurrencia usa Lock acotado para que el conteo compartido sea atómico sin serializar todo el pipeline.

## Uso de IA

Herramienta: asistente local OpenCode, sin llamadas a modelos externos en la app. Ejercicio 1 y 2: propuso e implementó clasificador y reporte; yo verifiqué normalización y singletons. Ejercicio 3: propuso la reparación stateless; yo exigí la tabla con síntomas y los tests de regresión. Ejercicio 4: redactó v2 y casos; yo pedí criterios accionables y JSON estricto. Ejercicio 5 y 6: implementó guardia y consola; yo verifiqué lock, 404 y `textContent`. Esta documentación y los comandos de verificación los orquesté yo con evidencia local.

## Qué haría con una semana más

Reharía la verificación en clon limpio sobre el código actual con suite 56/56, sumaría curva de calibración de umbrales con el corpus completo, agregaría prueba de concurrencia real a la guardia bajo carga, y documentaría latencias de arranque y consulta por separado. Nada de eso cambia el diseño; es endurecer evidencia y medición.

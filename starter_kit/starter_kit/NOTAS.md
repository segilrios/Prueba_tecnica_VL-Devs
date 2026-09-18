# Notas de entrega

## Resumen y alcance

Esta entrega completa los seis ejercicios del starter kit sin modificar los
archivos protegidos ni agregar dependencias. La solución conserva los clientes,
resultados que siguen se limitan a evidencia observada localmente.

## Interpretación de los seis ejercicios

| Ejercicio | Interpretación aplicada |
|---|---|
| 1. Clasificación | Normalizar una vez, respetar límites de palabra y elegir el patrón dinámico válido más largo. |
| 2. Reporte | Contar mensajes por intención activa de un workspace con clientes singleton esperados y operaciones `await`. |
| 3. Herramienta heredada | Eliminar estado compartido y escrituras en `/tmp`; precargar fuentes y conservar respuestas con fuente ausente. |
| 4. Verificador | Validar evidencia y trazabilidad antes del puntaje; conservar literalmente la respuesta propuesta. |
| 5. Guardia anti-loop | Contar por sesión y agente con exclusión mutua, conservar intentos rechazados y exponer snapshots defensivos. |
| 6. Consola | Validar workspace, recuperar evidencia global, decidir con los umbrales y renderizar datos dinámicos exclusivamente con `textContent`. |

## Decisiones documentadas

| Decisión | Motivo |
|---|---|
| Normalización NFKD, `casefold` y separadores | Trata acentos, mayúsculas y puntuación sin codificar un catálogo alternativo. |
| Límites `0.55` y `0.75` | Se conservaron los umbrales entregados: por debajo de `0.55` no hay respuesta; desde `0.55` hasta antes de `0.75` es `DUDOSO`; desde `0.75` es `APROBADO`. |
| Respuesta literal | La consola no reformula el fragmento recuperado, por lo que no inventa contenido. |
| Clientes singleton y mapa local de fuentes | Evita instanciaciones repetidas, N+1, caché mutable y persistencia entre llamadas. |
| `threading.Lock` acotado | Hace atómico el conteo compartido sin bloquear más trabajo del necesario. |
| Verificación antes de similitud | Una cita inválida, inexistente o contradictoria no puede aprobarse por un puntaje alto. |
| DOM con `textContent` | El texto de evidencia no se interpreta como HTML ejecutable. |

## Defectos identificados y corrección

| Área | Defecto observado en el esqueleto | Corrección |
|---|---|---|
| Clasificador | No estaba implementado. | Se añadió normalización y selección determinista del patrón válido más largo. |
| Reporte | No estaba implementado. | Se añadieron conteos asíncronos, propagación de workspace ausente y logs agregados sin cuerpos de mensajes. |
| Herramienta heredada | Caché mutable por defecto, instanciación directa, N+1 y escritura compartida en `/tmp`. | Se eliminó ese estado; se usan fábrica singleton y fuentes precargadas por llamada. |
| Guardia | No estaba implementada. | Se añadieron contadores bloqueados, aislamiento, reset, snapshot y diagnóstico de desborde. |
| Consola | `consultar()` no estaba implementada y la página volcaba JSON. | Se agregó el pipeline, HTTP 404 para workspace ausente y etapas legibles sin `innerHTML`. |

## Respuestas conceptuales acotadas

- La similitud recupera candidatos; no valida por sí sola que una afirmación esté sustentada. Por eso el verificador revisa fuente, cita, contradicción y trazabilidad antes del puntaje.
- Un prompt no es un control de recursos. El límite de herramientas debe vivir en código y conservar el intento que excede el máximo para diagnóstico.
- El contenido dinámico debe asignarse como texto. Escapar manualmente o interpolar HTML amplía innecesariamente la superficie de inyección.
- Un caché global mutable no es una optimización segura cuando no tiene invalidación, aislamiento ni copias defensivas.

## Limitación global del recuperador

`shared/retriever.py` es un insumo protegido y realiza la recuperación sobre el
corpus global. La consola valida que el workspace exista, pero no puede imponer
aislamiento de tenant en la búsqueda sin modificar ese archivo protegido. Por
ello, la recuperación no debe interpretarse como una garantía de aislamiento
por cliente.

## Uso de IA

Se utilizó un asistente de IA local (OpenCode) para inspeccionar el enunciado,
proponer e implementar cambios, redactar pruebas y esta documentación, y
orquestar comandos de verificación. No se realizaron llamadas a modelos ni a
servicios externos en la aplicación evaluada. Cada resultado declarado aquí
proviene de comandos locales ejecutados durante esta entrega.

## Evidencia observada

### Suite local

Comando ejecutado desde `starter_kit/starter_kit`:

```text
.venv/bin/python -m pytest
```

Resultado observado: salida `0`; `45 passed in 0.20s` con Python 3.14.4,
pytest 9.1.1 y pytest-asyncio 1.4.0.

### Consola/API local

Se inició `.venv/bin/python app.py` en `127.0.0.1:8000`, se consultó la API y
se detuvo el proceso local al finalizar. Resultados observados:

| Pregunta / workspace | Resultado |
|---|---|
| `¿Cuántos días de garantía tiene el plan Pro?` / `acme` | `APROBADO`, `facturacion`, `billing_agent`, similitud `1.00`; devolvió el fragmento literal de `src-1`. |
| `¿Cuánto dura la invitación a un usuario?` / `globex` | `DUDOSO`, intención `desconocido`, sin especialista, similitud `0.58`; devolvió el fragmento literal de `src-2` y requirió revisión. |
| `¿Qué incluye el plan Enterprise?` / `globex` | `SIN_EVIDENCIA`, intención `desconocido`, sin especialista, similitud `0.54`; `respuesta` fue `null`. |

No se capturó una duración de arranque o de consulta por separado; esa métrica
no está disponible en esta ejecución. El único tiempo medido por el comando fue
el de la suite local (`0.20s`).

### Disponibilidad de tiempos (hechos estructurados)

| Hecho | Valor |
|---|---|
| Assessment start timestamp | Not available — the exact session start time was not captured. |
| Per-exercise durations | Not available — time was not measured per exercise. |
| App startup / per-query durations | Not available — startup and query durations were not timed separately. |
| Suite wall time (recorded run) | `0.20s` for `45 passed` in the recorded local run; later runs vary and are reported with their own command output. |
| Screenshot capture timestamp | `2026-09-18T08:41:44-05:00` (observed). |
| Fresh-clone verification finish | `2026-09-18T08:41:44-05:00` (observed); the clone session start was not captured and is Not available. |

### Captura Enterprise `SIN_EVIDENCIA`

Referencia requerida: [`evidence/enterprise-sin-evidencia.png`](evidence/enterprise-sin-evidencia.png).

Captura real completada el `2026-09-18T08:41:44-05:00`. Se instaló Playwright
en el `.venv` existente desde PyPI y Firefox mediante el proveedor oficial de
Playwright. Con la aplicación local iniciada y detenida mediante un proceso
acotado, Playwright cargó la consola, escribió la pregunta, seleccionó
`globex`, pulsó el botón **Preguntar**, esperó el motivo renderizado y capturó
la página completa.

```text
.venv/bin/python -m pip install playwright
.venv/bin/python -m playwright install firefox
.venv/bin/python -c "... page.locator('#q').fill('¿Qué incluye el plan Enterprise?'); page.locator('#ws').select_option('globex'); page.locator('button[type=submit]').click(); page.locator('text=Similitud 0.54, por debajo del mínimo de 0.55.').wait_for(state='visible'); page.screenshot(path='evidence/enterprise-sin-evidencia.png', full_page=True)"
```

Resultado observado: salida `0`; `evidence/enterprise-sin-evidencia.png` fue
creado con `54,598` bytes. `file` lo identificó como PNG RGBA de `1280 x 900`.
La validación de DOM confirmó la pregunta y el motivo
`Similitud 0.54, por debajo del mínimo de 0.55.` con el estado
`SIN_EVIDENCIA` visible. No se usó JSON crudo, un mock ni una imagen generada
manualmente.

### Verificación desde clon local nuevo

Se recreó `/tmp/complete-technical-assessment-clone` exclusivamente desde el
repositorio local actual con `git clone --no-local`. Se creó un `.venv` propio
del clon y se instaló `requirements.txt` desde PyPI. La marca de inicio exacta
no fue capturada por la sesión anterior; la finalización de esta remediación
queda registrada como `2026-09-18T08:41:44-05:00` y los tiempos observados se
indican donde estuvieron disponibles.

```text
rm -rf /tmp/complete-technical-assessment-clone
git clone --no-local /home/sergiog/Desktop/Prueba_tecnica /tmp/complete-technical-assessment-clone
/home/sergiog/Desktop/Prueba_tecnica/starter_kit/starter_kit/.venv/bin/python -m venv /tmp/complete-technical-assessment-clone/starter_kit/starter_kit/.venv
/tmp/complete-technical-assessment-clone/starter_kit/starter_kit/.venv/bin/python -m pip install -r /tmp/complete-technical-assessment-clone/starter_kit/starter_kit/requirements.txt
/tmp/complete-technical-assessment-clone/starter_kit/starter_kit/.venv/bin/python -m pytest /tmp/complete-technical-assessment-clone/starter_kit/starter_kit/tests
```

Resultado observado: instalación correcta y `45 passed in 0.27s`. Después se
inició de forma acotada
`/tmp/complete-technical-assessment-clone/starter_kit/starter_kit/.venv/bin/python /tmp/complete-technical-assessment-clone/starter_kit/starter_kit/app.py`
en `127.0.0.1:8000`, se ejecutaron las tres consultas prescritas por
`/api/consulta` y se detuvo el proceso. Los resultados fueron `APROBADO`
(`1.00`) para Pro/acme, `DUDOSO` (`0.58`) para invitación/globex y
`SIN_EVIDENCIA` (`0.54`, `respuesta: null`) para Enterprise/globex. Tras cada
escenario, y al cierre final, el puerto 8000 quedó sin servicio.

### Integridad final

El commit de línea base `5d2feb41996e6e568e70129cb00d6e4e1caf4fcd` sigue siendo
ancestro de `HEAD`. Se recalcularon los ocho hashes protegidos y todos
coincidieron con el registro inicial de `apply-progress.md`; no se modificaron
clientes, recuperador, fixtures, prueba clasificadora base, configuración de
pytest, dependencias ni el verificador v1.

## Trabajo pendiente

No queda trabajo pendiente para la evidencia de entrega.

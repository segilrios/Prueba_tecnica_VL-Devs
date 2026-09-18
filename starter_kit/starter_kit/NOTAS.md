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

### Captura Enterprise `SIN_EVIDENCIA`

Referencia requerida: [`evidence/enterprise-sin-evidencia.png`](evidence/enterprise-sin-evidencia.png).

**No disponible.** Se intentó crearla con el Firefox local ya instalado:

```text
firefox --headless --screenshot evidence/enterprise-sin-evidencia.png --window-size 1280,900 'http://127.0.0.1:8000/api/consulta?q=%C2%BFQu%C3%A9%20incluye%20el%20plan%20Enterprise%3F&ws=globex'
```

El proceso terminó con salida `0`, pero no creó el archivo. No había una
herramienta local de automatización de navegador disponible para cargar la
consola y enviar la pregunta antes de capturarla. No se generó una imagen
sustitutiva ni se marcó esta evidencia como completada.

### Verificación desde clon local nuevo

Se creó `/tmp/complete-technical-assessment-clone` mediante `git clone --no-local`
apuntando exclusivamente al repositorio local actual. Se recreó el entorno
virtual sin acceder a índices remotos. La instalación no pudo completarse:
el nuevo entorno no contenía `pytest` ni `pytest_asyncio`, por lo que
`.venv/bin/python -m pytest` terminó con `No module named pytest`.

Aun así, el arranque acotado y las mismas tres consultas de API en ese clon
produjeron exactamente los resultados `APROBADO` (`1.00`), `DUDOSO` (`0.58`) y
`SIN_EVIDENCIA` (`0.54`) detallados arriba. Esta limitación es de preparación

## Trabajo pendiente

1. Obtener una captura real de la consola ya enviada para la pregunta
   Enterprise y guardarla en `evidence/enterprise-sin-evidencia.png`.
2. En un entorno autorizado con dependencias disponibles, instalar
   `requirements.txt` en el clon nuevo y repetir la suite completa de pytest.

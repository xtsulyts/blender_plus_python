# CLAUDE.md — Blender + Python Scripting

## Qué es este proyecto

Repo de aprendizaje personal de Blender Python scripting, con objetivo final de construir un MCP server que conecte Blender con un LLM via el protocolo MCP, y exportar escenas como glTF para visualizar en Three.js.

Plan completo: `plan_de_estudios.txt` (7 fases, ~11 semanas).

## Estructura

```
tutoriales/     código de referencia del tutorial series original (solo lectura)
aprendizaje/    trabajo propio, organizado por fase y sesión
plan_de_estudios.txt
```

### tutoriales/
Scripts del autor original del repo. Sirven como referencia para las fases 2–4 del plan.
Carpetas clave:
- `holder/`          → setup básico de escena (punto de partida fase 2)
- `cube_loop/`       → objeto + animación básica
- `color_slices/`    → serie completa (8 partes), materiales y animación
- `add-ons/`         → ejemplos de add-ons para fase 4
- `geo_nodes/`       → Geometry Nodes via script (fase 3)

### aprendizaje/
Sesiones propias. Convención de nombres: `faseX_sesionY/`.
- `fase1_sesion2/escena_base.py` — materiales Principled BSDF y keyframes

## Fase actual

**Fase 1 completada** (interfaz y flujo de trabajo, primeros scripts bpy).
**Próximo**: Fase 2 — Python API de Blender (bpy) fundamentos.

## Workflow

- Un tema por sesión, un commit al terminar cada sesión.
- No avanzar a la siguiente fase sin completar la actual.
- Cada sesión va en su propia carpeta dentro de `aprendizaje/`.

## Referencias clave

- Blender API: https://docs.blender.org/api/current/index.html
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP build server: https://modelcontextprotocol.io/docs/develop/build-server

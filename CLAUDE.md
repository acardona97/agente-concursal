# CLAUDE.md — Agente Concursal

## Proyecto
Curso de IA "Clases de Vuelo" para profesionales del derecho concursal.

## Estructura del Repositorio

```
agente-concursal/
  clases-vuelo/          ← Clases del curso (HTML estático)
    INDEX.html           ← Índice del curso
    001-*.html → 031-*.html
  clase-sucesiones/      ← Material de derecho sucesoral
  .claude/
    agents/              ← Agentes del pipeline /ship
    commands/            ← Comandos personalizados
```

## Convenciones del Curso

### Estilo HTML de clases
Todas las clases usan el mismo sistema de diseño:
```css
:root {
  --bg:#0d0f0e; --surface:#131615; --border:#1e2420;
  --gold:#c9a84c; --gold-dim:#7a6230;
  --text:#e8e4d9; --text-dim:#7a7568;
  --green:#2d4a3e; --blue:#1e3a5f;
  --font-body:'Georgia',serif;
  --font-mono:'Courier New',monospace;
}
```

### Nomenclatura de archivos
`NNN-slug-descriptivo.html` — NNN es número de 3 dígitos, sin espacios, todo minúsculas con guiones.

### Quizzes
Cada clase termina con 5 preguntas de opción múltiple con feedback inmediato vía JavaScript.

### Marca de completado
`localStorage.setItem('completed_NNN', fecha)` — key incluye el número de clase.

## Pipeline de 4 Agentes (/ship)

Para implementar features con revisión automática, usa `/ship <descripción>`.

Ver `.claude/commands/ship.md` para detalles completos.

Agentes disponibles:
- `.claude/agents/planner.md` — especificación técnica
- `.claude/agents/coder.md` — implementación
- `.claude/agents/tester.md` — verificación
- `.claude/agents/reviewer.md` — revisión final

## Branch de Desarrollo

Trabajo activo en: `claude/anthropic-study-flight-course-uaMnL`

## Comandos Útiles

```bash
# Ver clases existentes
ls clases-vuelo/*.html | sort

# Contar clases
ls clases-vuelo/[0-9]*.html | wc -l

# Abrir índice local
open clases-vuelo/INDEX.html
```

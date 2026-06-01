# INDEX MAESTRO — Anthropic Study
**Estudiante:** Andrés Cardona · Quarta · Abogado Concursal · Colombia  
**Fecha de creación:** 2026-06-01  
**Objetivo:** 13 horas de estudio personalizado · Vuelo  
**Prioridad:** Prompting avanzado → Agentes/Legal Hub → Claude Code → Finanzas/BTC

---

## REPOSITORIOS CLONADOS

| Repo | Descripción | Notebooks | HTMLs |
|------|-------------|-----------|-------|
| `courses/` | Cursos oficiales Anthropic: API fundamentals, prompt engineering, evaluations, tool use, real world prompting | 67 | 67 |
| `prompt-eng-interactive-tutorial/` | Tutorial interactivo de 9 capítulos — prompting desde básico hasta avanzado con ejercicios | 41 | 41 |
| `anthropic-cookbook/` | Recetas de código: RAG, sub-agents, MCP, tool use, PDF processing, managed agents, extended thinking | 85 | 85 |
| `claude-code/` | Código fuente y documentación oficial de Claude Code CLI | 0 | 0 |
| `claude-quickstarts/` | Proyectos de inicio rápido con Claude API | 1 | 1 |
| `claude-code-ultimate-guide/` | Guía completa de Claude Code: beginner→power user. Incluye cheatsheet, workflows, MCP, hooks, seguridad | 0 | 0 |
| `cwc-workshops/` | 7 workshops oficiales Code with Claude 2026: rightmodel, agent-decomposition, how-we-claude-code, ship-your-first-managed-agent, agent-battle, agents-that-remember, eval-driven-agent-development | 0 | 0 |
| `cwc-long-running-agents/` | Patrones para agentes de larga duración, hooks, evaluador con contexto fresco | 0 | 0 |
| `claude-for-legal/` | **PRIORIDAD ALTA** — Suite completa de plugins legales: corporate, litigation, IP, regulatory, employment, privacy, AI governance. MCP connectors para sistemas legales. Practice profiles configurables. | 0 | 0 |
| `knowledge-work-plugins/` | Plugins para trabajo de conocimiento: legal/, finance/, HR, sales, engineering, design, marketing. Playbooks configurables por jurisdicción. | 0 | 0 |
| `financial-services/` | Agentes financieros: DCF, LBO, reconciliación GL, pitch agent, valuation reviewer, earnings reviewer, market researcher. Patrón managed agents. | 0 | 0 |
| `skills/` | Skills reutilizables para Claude Code | 0 | 0 |

**Total repos:** 12  
**Total notebooks:** 194  
**Total HTMLs generados:** 213  

---

## ESTRUCTURA DEL CURSO PERSONALIZADO

### RESUMEN DE RESPUESTAS DE ENTREVISTA
- **Tiempo:** 13 horas, pausas a criterio personal
- **Prioridad:** c) Prompting avanzado → b) Agentes → a) Claude Code
- **Conocidos (no micro-clase):** API keys, Railway, tokens, context window
- **Principios (calibración rápida):** async/await, embeddings, RAG, fine-tuning vs prompting, MCP, skills
- **Estilo de aprendizaje:** código primero, práctica directa
- **Proyectos de aplicación:** todos los de Quarta + finanzas/BTC desde cero
- **Claude Code CLI:** muy poco uso — arranca desde lo concreto
- **Finanzas:** desde cero total

---

## ARCHIVOS HTML DEL CURSO — POR BLOQUE

### BLOQUE 0 — Micro-clases de Calibración (~40 min)
*Nota: el estudiante ya tiene principios en todos estos temas. Son calibraciones de 7-8 min, no clases desde cero.*

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/001-micro-async-await.html` | Async/await — calibración y expansión | 8 min | General |
| `clases/002-micro-embeddings.html` | Embeddings — cómo funciona ChromaDB | 8 min | General |
| `clases/003-micro-rag-por-dentro.html` | RAG internals — con el agente concursal real | 8 min | General |
| `clases/004-micro-fine-tuning-vs-prompting.html` | Fine-tuning vs prompting para Quarta | 8 min | General |
| `clases/005-micro-mcp-agentes-conexion.html` | MCP y agentes — desde lo que ya sabes | 8 min | claude-for-legal |

### BLOQUE 1 — Prompt Engineering Avanzado (~3.5 horas)
*Prioridad máxima según entrevista. Estrategias intermedias-avanzadas.*

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/006-prompt-engineering-estrategias-avanzadas.html` | Las 6 estrategias que más impactan | 45 min | courses + prompt-eng-interactive-tutorial |
| `clases/007-chain-of-thought-y-thinking-mode.html` | CoT + Extended Thinking | 30 min | anthropic-cookbook |
| `clases/008-prompt-caching-y-optimizacion.html` | Prompt caching — hasta 90% ahorro en costos | 30 min | courses/anthropic_api_fundamentals |
| `clases/009-system-prompts-que-funcionan.html` | Anatomía de system prompts poderosos | 30 min | claude-for-legal |
| `clases/010-evaluacion-de-prompts.html` | Evals y métricas para prompts legales | 45 min | courses/prompt_evaluations |
| `clases/011-prompting-para-documentos-legales.html` | Prompts para memoriales y recursos | 30 min | claude-for-legal/litigation-legal |

### BLOQUE 2 — MCP en Profundidad (~2 horas)
*Quieres dominar MCP — aquí va la profundidad real.*

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/012-mcp-arquitectura-fundamentos.html` | Protocolo MCP completo — desde tus principios | 45 min | claude-for-legal + cwc-workshops |
| `clases/013-mcp-tu-primer-servidor-avanzado.html` | MCP server completo en Python | 45 min | General + cwc-workshops |
| `clases/014-mcp-conectores-quarta-colombia.html` | Conectores colombianos: CSJ, SIC, DIAN, Supersociedades | 30 min | claude-for-legal/CONNECTORS.md |

### BLOQUE 3 — Agentes y Quarta Legal Hub (~2.5 horas)

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/015-micro-que-es-un-agente-ia.html` | Qué es un agente — calibración desde tu agente actual | 8 min | General |
| `clases/016-arquitectura-de-agentes-con-claude.html` | Managed Agents API + patrones avanzados | 45 min | cwc-workshops + anthropic-cookbook |
| `clases/017-skills-en-claude-code-como-funcionan.html` | Skills: cuándo usarlos, cómo crearlos, Cowork vs CLI | 30 min | claude-for-legal/skills + claude-code-ultimate-guide |
| `clases/018-agente-concursal-v2-decomposicion.html` | Refactorizar el agente concursal actual | 45 min | cwc-workshops/agent-decomposition |
| `clases/019-quarta-legal-hub-diseno-completo.html` | Diseño completo del Quarta Legal Hub | 45 min | claude-for-legal (TODO el repo) |

### BLOQUE 4 — Claude Code (~1.5 horas)
*Claude Code CLI — arranca desde casi cero, enfoque práctico.*

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/020-claude-code-cli-desde-cero.html` | Claude Code CLI — lo esencial para empezar | 30 min | claude-code-ultimate-guide |
| `clases/021-hooks-automatizacion-claude-code.html` | Hooks: auto-commit, notificaciones, seguridad | 30 min | claude-code-ultimate-guide + cwc-long-running-agents |
| `clases/022-claude-code-quarta-workflow-real.html` | Workflow real: feature → diff → deploy en Railway | 30 min | cwc-workshops/how-we-claude-code |

### BLOQUE 5 — Finanzas e Inversión con IA (~2.5 horas)
*Desde cero total. BTC, mercados, Polymarket.*

| Archivo | Tema | Duración | Repo origen |
|---------|------|----------|-------------|
| `clases/023-micro-agentes-financieros-intro.html` | Qué puede y NO puede hacer un agente financiero | 8 min | financial-services |
| `clases/024-agente-trading-btc-arquitectura.html` | Agente de análisis BTC desde cero | 45 min | financial-services/managed-agent-cookbooks |
| `clases/025-analisis-mercado-con-claude.html` | Morning brief automático: BTC + SPY + macro | 45 min | financial-services |
| `clases/026-polymarket-prediccion-eventos.html` | Polymarket: tu ventaja legal como edge competitivo | 30 min | General |

---

## ORDEN DE ESTUDIO — RUTA RECOMENDADA 13 HORAS

### Segmento 1 (0:00 — 1:10) · Calibración y base
```
001 → 002 → 003 → 004 → 005 → 006
[40 min micro-clases] + [45 min prompting avanzado]
```

### Segmento 2 (1:10 — 3:25) · Prompting avanzado completo
```
007 → 008 → 009 → 010 → 011
[30+30+30+45+30 = 165 min]
```

### Segmento 3 (3:25 — 5:25) · MCP en profundidad
```
012 → 013 → 014
[45+45+30 = 120 min]
```

### Segmento 4 (5:25 — 8:00) · Agentes y Legal Hub
```
015 → 016 → 017 → 018 → 019
[8+45+30+45+45 = 173 min]
```

### Segmento 5 (8:00 — 9:30) · Claude Code
```
020 → 021 → 022
[30+30+30 = 90 min]
```

### Segmento 6 (9:30 — 11:58) · Finanzas e inversión
```
023 → 024 → 025 → 026
[8+45+45+30 = 128 min]
```

**Total estimado: ~780 min = 13 horas**

---

## NOTEBOOKS HTML GENERADOS — POR REPO

### anthropic-cookbook/ (85 notebooks → 85 HTMLs)
Rutas completas en el directorio `/home/user/anthropic-study/anthropic-cookbook/`

**Managed Agents (12 archivos):**
- CMA_verify_with_outcome_grader.html
- CMA_gate_human_in_the_loop.html
- CMA_remember_user_preferences.html
- sre_incident_responder.html
- CMA_coordinate_specialist_team.html
- slack_data_bot.html
- CMA_explore_unfamiliar_codebase.html
- CMA_prompt_versioning_and_rollback.html
- CMA_orchestrate_issue_to_pr.html
- CMA_operate_in_production.html
- CMA_iterate_fix_failing_tests.html
- data_analyst_agent.html

**Extended Thinking (2):** extended_thinking.html, extended_thinking_with_tool_use.html

**Multimodal (6):** best_practices_for_vision.html, crop_tool.html, reading_charts_graphs_powerpoints.html, using_sub_agents.html, how_to_transcribe_text.html, getting_started_with_vision.html

### courses/ (67 notebooks → 67 HTMLs)
**anthropic_api_fundamentals/ (6):** 01_getting_started.html → 06_vision.html  
**real_world_prompting/ (5):** call_summarizer, customer_support_ai, medical_prompt, prompt_engineering, prompting_recap  
**tool_use/ (6):** tool_use_overview, structured_outputs, complete_workflow, tool_choice, chatbot_with_multiple_tools, + más  
**prompt_evaluations/ (varios):** eval frameworks, LLM-as-judge patterns  

### prompt-eng-interactive-tutorial/ (41 notebooks → 41 HTMLs)
Capítulos 01-10 + Appendix: Basic Prompt Structure, Messages Format, Assigning Roles, Avoiding Hallucinations, Formatting Output, Precognition/Thinking Step by Step, Few-Shot Prompting, Complex Prompts from Scratch, Chaining Prompts, Tool Use

### claude-quickstarts/ (1 notebook → 1 HTML)

---

## LOS 5 NOTEBOOKS MÁS RELEVANTES DEL COOKBOOK

1. `anthropic-cookbook/managed_agents/CMA_coordinate_specialist_team.html` — patrón de agente coordinador con especialistas (base del Quarta Legal Hub)
2. `anthropic-cookbook/managed_agents/CMA_remember_user_preferences.html` — memoria persistente entre sesiones
3. `anthropic-cookbook/extended_thinking/extended_thinking.html` — thinking mode completo
4. `anthropic-cookbook/managed_agents/CMA_gate_human_in_the_loop.html` — guardrails con human-in-the-loop (crítico para legal)
5. `anthropic-cookbook/managed_agents/data_analyst_agent.html` — agente de análisis de datos (base del sistema de trading)

---

## RUTAS EXACTAS DE ARCHIVOS CLAVE

```
~/anthropic-study/
├── INDEX.md                              ← Este archivo
├── tarea-vuelo.md                        ← Tarea especial colombia/claude-for-legal
├── clases/
│   ├── INDEX.html                        ← Navegador visual del curso
│   ├── 001-micro-async-await.html
│   ├── 002-micro-embeddings.html
│   ├── ... (26 clases en total)
│   └── 026-polymarket-prediccion-eventos.html
├── courses/
├── prompt-eng-interactive-tutorial/
├── anthropic-cookbook/
├── claude-code/
├── claude-quickstarts/
├── claude-code-ultimate-guide/
├── cwc-workshops/
├── cwc-long-running-agents/
├── claude-for-legal/
├── knowledge-work-plugins/
├── financial-services/
└── skills/
```

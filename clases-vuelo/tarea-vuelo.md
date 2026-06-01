# Tarea Especial del Vuelo — Adaptar claude-for-legal a Colombia
**Para ejecutar DURANTE el vuelo — no requiere internet**  
**Estimado:** 2-3 horas de trabajo concreto  
**Resultado esperado:** Borrador funcional del Quarta Legal Hub listo para implementar al aterrizar

---

## PARTE 1 — Entender la arquitectura de claude-for-legal

El repo `claude-for-legal` está en `~/anthropic-study/claude-for-legal/`

### Qué leer primero (en orden):
```
1. claude-for-legal/QUICKSTART.md
2. claude-for-legal/README.md (sección Agents — ver tabla completa)
3. claude-for-legal/litigation-legal/CLAUDE.md
4. claude-for-legal/litigation-legal/skills/ (ver los archivos .md)
5. claude-for-legal/corporate-legal/CLAUDE.md
6. claude-for-legal/ip-legal/CLAUDE.md
7. claude-for-legal/CONNECTORS.md
```

### Lo que encontrarás:
- **Practice profile (CLAUDE.md):** Archivo que le dice a Claude todo sobre la firma — jurisdicción, práctica, playbook, restricciones
- **Skills:** Archivos `.md` que definen comandos `/practice-area:accion` — por ejemplo `/litigation-legal:complaint-draft`
- **Agents:** Flujos completos que combinan múltiples skills con herramientas
- **Connectors:** Cómo conectar con sistemas externos (CourtListener, iManage, Everlaw, etc.)

---

## PARTE 2 — Adaptar el Practice Profile a Quarta

### Archivo a crear: `~/anthropic-study/quarta-legal-hub/CLAUDE.md`

Copia la estructura del archivo `claude-for-legal/litigation-legal/CLAUDE.md` y adapta:

```markdown
# Quarta — Practice Profile

## Firma
- Nombre: Quarta
- Jurisdicción principal: Colombia
- Derecho aplicable: Ley 1116 de 2006 (insolvencia), CGP (Código General del Proceso), 
  Decisión 486 CAN (propiedad industrial), Ley 256 de 1996 (competencia desleal)
- Tipo de práctica: Firma boutique — concursal, PI, litigios comerciales

## Áreas de práctica activas
1. **Derecho Concursal** (principal)
   - Procesos de reorganización (Ley 1116 Capítulo I)
   - Liquidación judicial (Ley 1116 Capítulo II)  
   - Validación de acuerdos extrajudiciales
   - Calificación y graduación de créditos
   - Autoridad competente: Superintendencia de Sociedades (delegada), Juzgados Civiles del Circuito
   
2. **Propiedad Industrial** (secundaria)
   - Marcas, patentes, diseños industriales
   - Decisión 486 CAN + Decisión 344 CAN
   - Autoridad competente: SIC (Superintendencia de Industria y Comercio)
   - Recursos: ante el Tribunal Administrativo, acción de nulidad y restablecimiento
   
3. **Litigios Comerciales** (terciaria)
   - Responsabilidad contractual, incumplimientos
   - Procesos verbales y verbales sumarios (CGP)
   - Autoridad competente: Juzgados Civiles del Circuito, Tribunal Superior

## Procesos activos de referencia
- MEMORY FOAM: Rad. 2025-0500 (concursal — reorganización)
- CAC vs CES: Rad. 24-422115 (litigio comercial)
- Magno Chocolates (concursal)

## Restricciones de guardrail
- TODO output es borrador para revisión del abogado — nunca consejo legal final
- Citar fuente exacta de toda afirmación normativa (artículo + ley)
- Indicar siempre la jurisdicción asumida
- Alertar cuando la ley sea ambigua o haya jurisprudencia contradictoria
- No generar plazos procesales sin verificar la norma exacta

## Formato de output preferido
- Memoriales: formato Word (DOCX)
- Análisis: markdown con citas en pie de página
- Tablas de créditos: Excel (XLSX)
- Cronogramas: tabla markdown
```

---

## PARTE 3 — Equivalentes colombianos de los conectores de claude-for-legal

### Tabla de mapeo: Sistema EE.UU. → Equivalente Colombia

| Sistema claude-for-legal | Función | Equivalente Colombia | URL / API | Estado |
|--------------------------|---------|---------------------|-----------|--------|
| CourtListener | Jurisprudencia federal | CSJ Relatoría | https://cortesuprema.gov.co/relatoría | Web scraping |
| CourtListener PACER | Dockets federales | Rama Judicial TYBA | https://consultaprocesos.ramajudicial.gov.co | API pública |
| Westlaw / LexisNexis | Base jurídica | Legis / Lalegis | (suscripción) | API privada |
| Ironclad | Gestión contratos | Ninguno equivalente | — | Por construir |
| iManage | Gestión documentos | Google Drive / OneDrive | API disponible | Integración directa |
| Everlaw | Revisión documental | Ninguno equivalente | — | Por construir |
| EDGAR (SEC) | Documentos societarios | RUES + SIIS | https://rues.org.co / Supersociedades | Web scraping |
| CourtListener (IPs) | Marcas / patentes | SIC SIPI | https://sipi.sic.gov.co | Web scraping |
| IRS / Tax docs | Tributario | DIAN | https://www.dian.gov.co | Portal web |
| OpenCorporates | Info empresas | Cámara de Comercio RUES | https://rues.org.co | API pública parcial |

### Prioridad de construcción para Quarta:

**Prioridad 1 — Construir primero (alto impacto, técnicamente viable):**
```python
# Conector 1: Rama Judicial — consulta de procesos
# URL: https://consultaprocesos.ramajudicial.gov.co/api/v2
# Tipo: REST API pública
# Uso: obtener estado de procesos, actuaciones, providencias

# Conector 2: Supersociedades SIIS — información de insolvencia
# URL: https://siis.ia.supersociedades.gov.co  
# Tipo: Web scraping / API parcial
# Uso: estado de procesos concursales, resoluciones, oficios

# Conector 3: CSJ Relatoría — jurisprudencia
# URL: https://cortesuprema.gov.co/relatoria/
# Tipo: Búsqueda web + scraping HTML
# Uso: sentencias de la Sala Civil sobre Ley 1116
```

**Prioridad 2 — Segundo sprint:**
```python
# Conector 4: SIC SIPI — propiedad industrial  
# URL: https://sipi.sic.gov.co
# Tipo: Web scraping
# Uso: estado de marcas, resoluciones de registro

# Conector 5: RUES — información societaria
# URL: https://www.rues.org.co
# Tipo: Web scraping / consulta por NIT
# Uso: razón social, representante legal, estado comercial
```

**Prioridad 3 — Tercer sprint:**
```python
# Conector 6: DIAN — estado tributario
# Conector 7: BanRep — tasas de interés y certificaciones
# Conector 8: Google Drive — gestión documental interna Quarta
```

---

## PARTE 4 — Skills a adaptar de claude-for-legal a Colombia

### Skills de litigios → adaptados a Ley 1116 y CGP

```markdown
# skill: quarta:calificacion-creditos
Toma la información de los créditos reconocidos en un proceso de reorganización 
y genera el proyecto de calificación y graduación según el artículo 2495 CC 
y los artículos 26-36 de la Ley 1116 de 2006.

Output: tabla Excel con columnas [Acreedor, Valor, Clase, Prelación, Observaciones]
Citar: artículo específico de la Ley 1116 para cada clase asignada
Alerta: identificar créditos con clasificación ambigua para revisión del abogado
```

```markdown
# skill: quarta:proyecto-votos
Genera el proyecto de votos para la deliberación del acuerdo de reorganización.
Calcula: quórum decisorio por clase (mayorías simples y calificadas, Art. 29 Ley 1116)
Output: tabla Excel con [Acreedor, Clase, Valor, % del total de clase, % del total]
```

```markdown
# skill: quarta:analisis-credito
Analiza si un crédito presentado en un proceso concursal cumple los requisitos 
del artículo 51 Ley 1116. Identifica documentos faltantes. Sugiere clase y prelación.
Output: memo de análisis con semáforo (verde/amarillo/rojo) y lista de objeciones posibles
```

```markdown
# skill: quarta:buscar-jurisprudencia  
Busca jurisprudencia de la Corte Suprema de Justicia (Sala Civil) sobre un tema 
específico del derecho concursal colombiano.
Fuentes: CSJ Relatoría, Supersociedades, Tribunal Superior de Bogotá
Output: lista de sentencias con radicado, fecha, ponente, tesis y cita exacta
```

```markdown
# skill: quarta:memorial-objecion
Redacta memorial de objeción a crédito en un proceso concursal.
Inputs: acreedor, valor objetado, clase actual, clase solicitada, argumentos
Output: memorial DOCX en formato Quarta, listo para revisar y presentar
Guardrail: siempre incluir "Borrador — Sujeto a revisión del abogado tratante"
```

```markdown
# skill: quarta:analisis-pi
Analiza la viabilidad de un registro de marca o patente ante la SIC.
Jurisdicción: Colombia (Decisión 486 CAN)
Output: análisis de distintividad, búsqueda de antecedentes (simulada), 
        recomendación y próximos pasos
```

---

## PARTE 5 — Borrador de arquitectura del Quarta Legal Hub

### Estructura de directorios a crear al aterrizar:

```
quarta-legal-hub/
├── CLAUDE.md                    ← Practice profile de Quarta (redactado en Parte 2)
├── concursal/
│   ├── CLAUDE.md               ← Perfil específico derecho concursal
│   ├── skills/
│   │   ├── calificacion-creditos.md
│   │   ├── proyecto-votos.md
│   │   ├── analisis-credito.md
│   │   ├── memorial-objecion.md
│   │   └── buscar-jurisprudencia.md
│   └── agents/
│       ├── proceso-watcher.py  ← Monitorea Rama Judicial por actuaciones
│       └── creditos-reviewer.py← Revisa proyecto de calificación automáticamente
├── pi/
│   ├── CLAUDE.md
│   └── skills/
│       ├── analisis-pi.md
│       └── respuesta-oficio-sic.md
├── litigios/
│   ├── CLAUDE.md
│   └── skills/
│       ├── analisis-demanda.md
│       └── recurso-reposicion.md
├── connectors/
│   ├── rama_judicial.py        ← API pública
│   ├── supersociedades.py      ← Web scraping
│   ├── csj_relatoria.py        ← Web scraping
│   └── sic_sipi.py             ← Web scraping
└── shared/
    ├── templates/              ← Templates DOCX y XLSX de Quarta
    ├── guardrails.py           ← Validaciones legales comunes
    └── citations.py            ← Formato de citas jurídicas
```

### Prioridad de implementación post-vuelo:

**Semana 1:** Crear CLAUDE.md de Quarta + 5 skills de concursal + integrar con agente concursal actual  
**Semana 2:** Conector Rama Judicial + proceso-watcher.py  
**Semana 3:** Conector Supersociedades + creditos-reviewer.py  
**Mes 2:** Skills de PI + conector SIC  
**Mes 3:** Skills de litigios + conector CSJ Relatoría  
**Mes 4-6:** Agentes de larga duración, integración Cowork, dashboard

---

## PARTE 6 — Lo que puedes implementar HOY (durante el vuelo, sin internet)

> Estos archivos no requieren conexión. Solo Claude Code o tu editor.

### Tarea 1: Crear el CLAUDE.md de Quarta (30 min)
Usa la plantilla de la Parte 2. Personaliza con tu playbook real.
Ubícalo en: `~/agente-concursal/CLAUDE.md` para que Claude Code lo use inmediatamente.

### Tarea 2: Escribir el skill quarta:calificacion-creditos (45 min)
Es el skill más usado en tu práctica diaria.
Estructura del archivo `.md` del skill (cópiala de `claude-for-legal/litigation-legal/skills/`):
```
---
name: calificacion-creditos
description: Genera proyecto de calificación y graduación de créditos según Ley 1116
trigger: /quarta:calificacion-creditos
---

[INSTRUCCIÓN DEL SKILL]
```

### Tarea 3: Diseñar el conector Rama Judicial (45 min)
URL pública: https://consultaprocesos.ramajudicial.gov.co/api/v2
Diseña las funciones que necesitas:
- `buscar_proceso(numero_radicado)` → retorna estado y últimas actuaciones
- `listar_actuaciones(radicado, desde_fecha)` → retorna lista de providencias nuevas
- `descargar_providencia(id_actuacion)` → descarga el PDF (si disponible)

### Tarea 4: Planear el proceso-watcher (30 min)
Un agente que corre diariamente y:
1. Lee una lista de radicados de procesos activos de Quarta
2. Consulta el conector Rama Judicial por novedades
3. Si hay actuaciones nuevas → genera resumen con Claude
4. Envía alerta con el resumen al abogado tratante
5. Marca el proceso como revisado

---

## CHECKLIST DE ENTREGABLES DEL VUELO

- [ ] Leí los archivos clave de claude-for-legal (Parte 1)
- [ ] Redacté el CLAUDE.md de Quarta (Parte 2)
- [ ] Ubiqué el CLAUDE.md en ~/agente-concursal/
- [ ] Escribí al menos 2 skills de concursal
- [ ] Diseñé el conector Rama Judicial en pseudocódigo/Python
- [ ] Definí el plan de arquitectura del Quarta Legal Hub
- [ ] Identifiqué los 3 agentes que quiero construir primero al aterrizar

---

## RECURSOS OFFLINE DISPONIBLES

Durante el vuelo puedes leer (sin internet):
```
~/anthropic-study/claude-for-legal/         → Arquitectura completa del sistema
~/anthropic-study/knowledge-work-plugins/legal/ → Playbooks configurables
~/anthropic-study/cwc-workshops/            → Todos los workshops
~/anthropic-study/claude-code-ultimate-guide/ → Guía completa Claude Code
~/anthropic-study/clases/INDEX.html         → Navegador del curso
```

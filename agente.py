"""
agente.py v2 — Motor del Agente Concursal
Incluye indexación de documentos en tiempo real
"""

import os
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import pypdf
from docx import Document

# ─── Configuración ────────────────────────────────────────────────────────────
DB_FOLDER    = "./vectordb"
EMBED_MODEL  = "paraphrase-multilingual-mpnet-base-v2"
N_RESULTADOS = 7
MAX_TOKENS   = 4096
CLAUDE_MODEL = "claude-opus-4-5"
CHUNK_SIZE   = 900
CHUNK_OVERLAP = 180
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Eres un agente jurídico especializado en derecho concursal colombiano, \
con dominio experto de la Ley 1116 de 2006 y sus decretos reglamentarios, el Decreto 772 de 2020, \
las Circulares y Resoluciones de la Superintendencia de Sociedades, y la jurisprudencia \
de la Sala de Casación Civil de la Corte Suprema de Justicia en materia concursal.

Tu función principal es asistir a un abogado en la redacción de:
- Memoriales y escritos procesales en procesos de reorganización y liquidación judicial
- Proyectos de calificación y graduación de créditos (Art. 49-52 Ley 1116)
- Proyectos de votos para deliberaciones de la junta de acreedores
- Objeciones a proyectos de calificación y graduación
- Recursos de reposición y apelación contra autos del juez del concurso
- Acuerdos de reorganización y sus modificaciones

REGLAS DE REDACCIÓN:
1. Usa el lenguaje forense colombiano formal y preciso
2. Cita artículos específicos de la Ley 1116 de 2006 o normas concordantes cuando corresponda
3. Estructura los escritos así:
   - Encabezado (despacho, radicado, nombre del proceso, nombre del promovente)
   - Hechos (numerados)
   - Fundamentos jurídicos
   - Peticiones (numeradas, claras y concretas)
   - Anexos (si aplica)
4. Basa tu respuesta SIEMPRE en el contexto normativo y los modelos proporcionados
5. Si el contexto no es suficiente para un dato puntual, usa: [DATO A COMPLETAR POR EL ABOGADO]
6. Cuando redactes proyectos de calificación, respeta el orden de preferencia del Art. 2495 C.C. \
y las normas especiales de la Ley 1116
7. Mantén coherencia terminológica: usa "promovente", "deudor", "acreedor", "acreencia", \
"crédito reconocido", "crédito admitido" según corresponda procesalmente

El abogado usuario es experto en la materia. Responde con rigor técnico, sin explicaciones \
pedagógicas innecesarias. Ve directo al escrito o análisis solicitado.

REGLAS DE CONFIDENCIALIDAD — OBLIGATORIAS E INNEGOCIABLES:
1. NUNCA uses nombres propios de personas naturales, empresas, sociedades o entidades que aparezcan \
en los documentos de contexto indexados. Esos documentos contienen información confidencial de clientes reales.
2. Cuando necesites referenciar un ejemplo, usa SIEMPRE placeholders genéricos: \
[DEUDOR], [ACREEDOR], [SOCIEDAD], [TRABAJADOR], [PROVEEDOR], [ENTIDAD FINANCIERA], [NOMBRE DEL PROCESO].
3. Si el abogado te proporciona nombres específicos en su solicitud, úsalos SOLO para ese escrito \
puntual — nunca los mezcles con información extraída de otros documentos indexados.
4. Los documentos indexados son fuente de estructura normativa y modelos de redacción ÚNICAMENTE. \
Jamás extraigas ni reproduzcas datos, nombres, cifras o hechos específicos de esos documentos.
5. Si detectas que estás a punto de escribir un nombre propio proveniente del contexto indexado, \
sustitúyelo inmediatamente por el placeholder correspondiente."""


# ─── Inicialización ───────────────────────────────────────────────────────────
print("🤖 Cargando agente concursal v2...")

_embed_model   = SentenceTransformer(EMBED_MODEL)
_chroma_client = chromadb.PersistentClient(path=DB_FOLDER)
__anthropic = anthropic.Anthropic(api_key=os.environ.get("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"))

try:
    _collection = _chroma_client.get_collection("concursal")
    count = _collection.count()
    print(f"✅ Base vectorial cargada: {count} fragmentos indexados")
except Exception:
    _collection = None
    print("⚠️  Base vectorial no encontrada. Ejecuta primero: python ingest.py")
# ──────────────────────────────────────────────────────────────────────────────


def _leer_archivo(path: str, nombre: str) -> str:
    """Lee el contenido de un archivo según su extensión."""
    ext = Path(nombre).suffix.lower()
    if ext == ".pdf":
        try:
            reader = pypdf.PdfReader(path)
            paginas = []
            for i, page in enumerate(reader.pages):
                texto = page.extract_text()
                if texto and texto.strip():
                    paginas.append(f"[Página {i+1}]\n{texto}")
            return "\n\n".join(paginas)
        except Exception as e:
            return ""
    elif ext == ".docx":
        try:
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return ""
    elif ext == ".txt":
        try:
            return Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
    return ""


def _chunker(texto: str, nombre: str) -> list[dict]:
    """Divide texto en fragmentos con overlap."""
    chunks = []
    texto = texto.strip()
    if not texto:
        return chunks
    inicio = 0
    idx = 0
    while inicio < len(texto):
        fin = min(inicio + CHUNK_SIZE, len(texto))
        fragmento = texto[inicio:fin].strip()
        if fragmento:
            chunks.append({"texto": fragmento, "fuente": nombre, "chunk_idx": idx})
            idx += 1
        inicio += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def indexar_documento_nuevo(tmp_path: str, nombre_original: str) -> dict:
    """
    Indexa un documento nuevo en tiempo real.
    Retorna dict con ok, fragmentos_nuevos, fragmentos_total.
    """
    global _collection

    if _collection is None:
        # Intentar crear la colección si no existe
        try:
            _collection = _chroma_client.create_collection(
                name="concursal",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            _collection = _chroma_client.get_collection("concursal")

    # Leer el archivo
    texto = _leer_archivo(tmp_path, nombre_original)
    if not texto.strip():
        return {
            "ok": False,
            "error": "No se pudo extraer texto. El PDF puede estar escaneado (imagen)."
        }

    # Generar chunks
    chunks = _chunker(texto, nombre_original)
    if not chunks:
        return {"ok": False, "error": "El documento no contiene texto procesable."}

    # Generar embeddings
    textos = [c["texto"] for c in chunks]
    embeddings = _embed_model.encode(textos).tolist()

    # Generar IDs únicos para no colisionar con los existentes
    count_actual = _collection.count()
    ids = [f"nuevo_{count_actual + i}" for i in range(len(chunks))]

    # Agregar a la colección
    _collection.add(
        documents=textos,
        embeddings=embeddings,
        metadatas=[{"fuente": nombre_original} for _ in chunks],
        ids=ids
    )

    fragmentos_total = _collection.count()

    return {
        "ok": True,
        "fragmentos_nuevos": len(chunks),
        "fragmentos_total": fragmentos_total
    }


def buscar_contexto(consulta: str) -> tuple[str, list[str]]:
    """Busca los fragmentos más relevantes en la base vectorial."""
    if _collection is None:
        return "⚠️ Base vectorial no disponible.", []

    embedding = _embed_model.encode([consulta]).tolist()
    resultados = _collection.query(
        query_embeddings=embedding,
        n_results=min(N_RESULTADOS, _collection.count())
    )

    fragmentos = []
    fuentes_usadas = set()
    for doc, meta in zip(resultados["documents"][0], resultados["metadatas"][0]):
        fuente = meta.get("fuente", "Documento")
        fuentes_usadas.add(fuente)
        fragmentos.append(f"[Fuente: {fuente}]\n{doc}")

    return "\n\n---\n\n".join(fragmentos), sorted(fuentes_usadas)


def consultar_agente(mensaje: str, historial: list = None) -> tuple[str, list, list]:
    """Consulta principal al agente con RAG."""
    if historial is None:
        historial = []

    contexto, fuentes = buscar_contexto(mensaje)

    mensaje_con_contexto = f"""CONTEXTO NORMATIVO Y DOCUMENTOS DEL PROCESO:
{contexto}

{'─' * 60}

SOLICITUD:
{mensaje}"""

    mensajes = historial + [{"role": "user", "content": mensaje_con_contexto}]

    response = _anthropic.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=mensajes
    )

    respuesta = response.content[0].text

    historial_nuevo = historial + [
        {"role": "user",      "content": mensaje_con_contexto},
        {"role": "assistant", "content": respuesta}
    ]

    if len(historial_nuevo) > 12:
        historial_nuevo = historial_nuevo[-12:]

    return respuesta, historial_nuevo, fuentes


def estado_base_vectorial() -> dict:
    """Retorna info sobre la base vectorial."""
    if _collection is None:
        return {"ok": False, "fragmentos": 0, "mensaje": "Base vectorial no inicializada"}
    try:
        count = _collection.count()
        return {"ok": True, "fragmentos": count, "mensaje": f"{count} fragmentos indexados"}
    except Exception as e:
        return {"ok": False, "fragmentos": 0, "mensaje": str(e)}

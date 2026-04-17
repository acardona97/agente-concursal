"""
ingest.py — Agente Concursal Ley 1116
Procesa e indexa todos los documentos en /documentos
Ejecutar UNA sola vez (y cada vez que agregues archivos nuevos)
"""

import os
import sys
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import pypdf
from docx import Document

# ─── Configuración ────────────────────────────────────────────────────────────
DOCS_FOLDER  = "./documentos"
DB_FOLDER    = "./vectordb"
CHUNK_SIZE   = 900    # caracteres por fragmento
CHUNK_OVERLAP = 180   # superposición para no perder contexto entre fragmentos
EMBED_MODEL  = "paraphrase-multilingual-mpnet-base-v2"  # soporta español nativo
# ──────────────────────────────────────────────────────────────────────────────


def leer_pdf(path: Path) -> str:
    """Extrae texto de un PDF, página por página."""
    try:
        reader = pypdf.PdfReader(str(path))
        paginas = []
        for i, page in enumerate(reader.pages):
            texto = page.extract_text()
            if texto and texto.strip():
                paginas.append(f"[Página {i+1}]\n{texto}")
        return "\n\n".join(paginas)
    except Exception as e:
        print(f"  ⚠️  Error leyendo PDF {path.name}: {e}")
        return ""


def leer_docx(path: Path) -> str:
    """Extrae texto de un archivo Word (.docx)."""
    try:
        doc = Document(str(path))
        parrafos = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(parrafos)
    except Exception as e:
        print(f"  ⚠️  Error leyendo DOCX {path.name}: {e}")
        return ""


def leer_txt(path: Path) -> str:
    """Extrae texto de un archivo .txt."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"  ⚠️  Error leyendo TXT {path.name}: {e}")
        return ""


def chunker(texto: str, nombre_archivo: str) -> list[dict]:
    """
    Divide el texto en fragmentos con overlap.
    Retorna lista de dicts con texto y metadatos.
    """
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
            chunks.append({
                "texto": fragmento,
                "fuente": nombre_archivo,
                "chunk_idx": idx
            })
            idx += 1
        inicio += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def indexar_todo():
    """Proceso principal: lee, trocea e indexa todos los documentos."""

    # Verificar que existe la carpeta de documentos
    docs_path = Path(DOCS_FOLDER)
    if not docs_path.exists():
        print(f"❌ No se encontró la carpeta '{DOCS_FOLDER}'.")
        print("   Crea la carpeta y agrega tus archivos PDF y DOCX.")
        sys.exit(1)

    # Inicializar base vectorial
    print("🔧 Inicializando base vectorial...")
    chroma_client = chromadb.PersistentClient(path=DB_FOLDER)

    # Borrar colección anterior si existe (para re-indexar limpio)
    try:
        chroma_client.delete_collection("concursal")
        print("   Colección anterior eliminada (re-indexación limpia)")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name="concursal",
        metadata={"hnsw:space": "cosine"}
    )

    # Cargar modelo de embeddings
    print(f"🤖 Cargando modelo de embeddings ({EMBED_MODEL})...")
    print("   (Primera vez puede tomar 1-2 minutos descargando el modelo)")
    embed_model = SentenceTransformer(EMBED_MODEL)
    print("   ✅ Modelo listo\n")

    # Procesar archivos
    extensiones_soportadas = {".pdf", ".docx", ".txt"}
    archivos = [
        f for f in docs_path.rglob("*")
        if f.suffix.lower() in extensiones_soportadas and f.is_file()
    ]

    if not archivos:
        print("❌ No se encontraron archivos PDF, DOCX o TXT en la carpeta documentos/")
        sys.exit(1)

    print(f"📁 Archivos encontrados: {len(archivos)}\n")

    todos_chunks = []
    for archivo in sorted(archivos):
        extension = archivo.suffix.lower()
        print(f"  📄 {archivo.name}", end=" ... ")

        if extension == ".pdf":
            texto = leer_pdf(archivo)
        elif extension == ".docx":
            texto = leer_docx(archivo)
        elif extension == ".txt":
            texto = leer_txt(archivo)
        else:
            print("omitido")
            continue

        if not texto.strip():
            print("⚠️  sin texto extraíble")
            continue

        chunks = chunker(texto, archivo.name)
        todos_chunks.extend(chunks)
        print(f"✅ {len(chunks)} fragmentos")

    if not todos_chunks:
        print("\n❌ No se pudo extraer texto de ningún archivo.")
        sys.exit(1)

    print(f"\n📊 Total fragmentos generados: {len(todos_chunks)}")
    print("🔢 Generando embeddings (puede tomar varios minutos)...")

    # Generar embeddings en lotes
    BATCH_SIZE = 64
    textos  = [c["texto"]  for c in todos_chunks]
    fuentes = [c["fuente"] for c in todos_chunks]
    ids     = [f"chunk_{i}" for i in range(len(todos_chunks))]

    todos_embeddings = []
    for i in range(0, len(textos), BATCH_SIZE):
        lote = textos[i : i + BATCH_SIZE]
        embeddings_lote = embed_model.encode(lote, show_progress_bar=False).tolist()
        todos_embeddings.extend(embeddings_lote)
        progreso = min(i + BATCH_SIZE, len(textos))
        print(f"   {progreso}/{len(textos)} fragmentos procesados", end="\r")

    print(f"   {len(textos)}/{len(textos)} fragmentos procesados ✅")

    # Guardar en ChromaDB en lotes
    print("💾 Guardando en base vectorial...")
    for i in range(0, len(todos_chunks), BATCH_SIZE):
        collection.add(
            documents=textos[i : i + BATCH_SIZE],
            embeddings=todos_embeddings[i : i + BATCH_SIZE],
            metadatas=[{"fuente": f} for f in fuentes[i : i + BATCH_SIZE]],
            ids=ids[i : i + BATCH_SIZE]
        )

    print(f"\n✅ Indexación completa.")
    print(f"   {len(archivos)} archivos → {len(todos_chunks)} fragmentos indexados")
    print(f"   Base vectorial guardada en: {DB_FOLDER}/")
    print(f"\n👉 Ahora puedes correr: python app.py")


if __name__ == "__main__":
    indexar_todo()

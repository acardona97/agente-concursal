"""
ingest.py v2 — Sin sentence-transformers, usa embeddings de ChromaDB
Ejecutar UNA sola vez (y cada vez que agregues archivos nuevos)
"""

import os
import sys
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import pypdf
from docx import Document

DOCS_FOLDER  = "./documentos"
DB_FOLDER    = "./vectordb"
CHUNK_SIZE   = 900
CHUNK_OVERLAP = 180


def leer_pdf(path):
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


def leer_docx(path):
    try:
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  ⚠️  Error leyendo DOCX {path.name}: {e}")
        return ""


def leer_txt(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"  ⚠️  Error leyendo TXT {path.name}: {e}")
        return ""


def chunker(texto, nombre_archivo):
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
            chunks.append({"texto": fragmento, "fuente": nombre_archivo, "chunk_idx": idx})
            idx += 1
        inicio += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def indexar_todo():
    docs_path = Path(DOCS_FOLDER)
    if not docs_path.exists():
        print(f"❌ No se encontró la carpeta '{DOCS_FOLDER}'.")
        sys.exit(1)

    print("🔧 Inicializando base vectorial...")
    chroma_client = chromadb.PersistentClient(path=DB_FOLDER)
    ef = embedding_functions.DefaultEmbeddingFunction()

    try:
        chroma_client.delete_collection("concursal")
        print("   Colección anterior eliminada")
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name="concursal",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    extensiones = {".pdf", ".docx", ".txt"}
    archivos = [f for f in docs_path.rglob("*")
                if f.suffix.lower() in extensiones and f.is_file()]

    if not archivos:
        print("❌ No se encontraron archivos en la carpeta documentos/")
        sys.exit(1)

    print(f"📁 Archivos encontrados: {len(archivos)}\n")

    todos_chunks = []
    for archivo in sorted(archivos):
        ext = archivo.suffix.lower()
        print(f"  📄 {archivo.name}", end=" ... ")
        if ext == ".pdf":
            texto = leer_pdf(archivo)
        elif ext == ".docx":
            texto = leer_docx(archivo)
        elif ext == ".txt":
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

    print(f"\n📊 Total fragmentos: {len(todos_chunks)}")
    print("💾 Guardando en base vectorial...")

    BATCH = 64
    textos  = [c["texto"]  for c in todos_chunks]
    fuentes = [c["fuente"] for c in todos_chunks]
    ids     = [f"chunk_{i}" for i in range(len(todos_chunks))]

    for i in range(0, len(todos_chunks), BATCH):
        collection.add(
            documents=textos[i:i+BATCH],
            metadatas=[{"fuente": f} for f in fuentes[i:i+BATCH]],
            ids=ids[i:i+BATCH]
        )
        print(f"   {min(i+BATCH, len(textos))}/{len(textos)} guardados", end="\r")

    print(f"\n✅ Indexación completa: {len(archivos)} archivos → {len(todos_chunks)} fragmentos")
    print(f"👉 Ahora puedes correr: python app.py")


if __name__ == "__main__":
    indexar_todo()

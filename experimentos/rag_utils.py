import os, re
import numpy as np

_UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(os.path.dirname(_UTILS_DIR), "documentos_estandar")

# Embedding model used for dense retrieval.
# all-MiniLM-L6-v2: 22 M params, 384-dim, runs on CPU in <1 s per batch.
_EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
_embedder = None  # lazy-loaded on first call


def _get_embedder():
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Force CPU so the embedding model does not compete for the GPU
            # VRAM budget reserved for the LLM (8 GB RTX 4060).
            _embedder = SentenceTransformer(_EMBEDDING_MODEL_ID, device="cpu")
            print(f"  [+] RAG embedder loaded (CPU): {_EMBEDDING_MODEL_ID}")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    return _embedder


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosine similarity between query vector a (1-D) and matrix b (N x D)."""
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return b_norm @ a_norm


def cargar_documentos() -> list[dict]:
    """
    Reads all PDFs and Word files from documentos_estandar.
    Returns a list of dicts: {nombre, texto, chunks, embeddings}.
    Chunks and embeddings are computed here for reuse.
    """
    if not os.path.isdir(DOCS_DIR):
        print(f"  [!] Folder not found: {DOCS_DIR}")
        return []

    embedder = _get_embedder()
    docs = []
    for fname in sorted(os.listdir(DOCS_DIR)):
        path = os.path.join(DOCS_DIR, fname)
        ext = fname.lower()
        if ext.endswith(".pdf"):
            texto = _leer_pdf(path)
        elif ext.endswith((".docx", ".doc")):
            texto = _leer_word(path)
        else:
            continue
        if not texto.strip():
            continue

        chunks = _chunkear(texto)
        if not chunks:
            continue

        embeddings = embedder.encode(chunks, convert_to_numpy=True,
                                     show_progress_bar=False, device="cpu")
        docs.append({
            "nombre":     fname,
            "texto":      texto,
            "chunks":     chunks,
            "embeddings": embeddings,
        })
        print(
            f"  [+] RAG document loaded: {fname} "
            f"({len(texto):,} chars, {len(chunks)} chunks)"
        )
    return docs


def _chunkear(texto: str, max_chars: int = 400) -> list[str]:
    """
    Splits text into semantic chunks:
    1. Splits on double newlines (\\n\\n).
    2. Paragraphs longer than max_chars are subdivided by sentence.
    Returns a list of non-empty strings.
    """
    parrafos = [p.strip() for p in re.split(r"\n{2,}", texto) if p.strip()]
    chunks: list[str] = []
    for p in parrafos:
        if len(p) <= max_chars:
            chunks.append(p)
        else:
            # subdivide by sentence
            oraciones = re.split(r"(?<=[.!?])\s+", p)
            buf = ""
            for o in oraciones:
                if len(buf) + len(o) + 1 <= max_chars:
                    buf = (buf + " " + o).strip() if buf else o
                else:
                    if buf:
                        chunks.append(buf)
                    buf = o
            if buf:
                chunks.append(buf)
    return [c for c in chunks if len(c) > 20]


def _leer_pdf(path: str) -> str:
    for mod_name in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(mod_name)
            Reader = getattr(mod, "PdfReader")
            with open(path, "rb") as f:
                reader = Reader(f)
                return "\n".join(
                    (page.extract_text() or "") for page in reader.pages
                )
        except ImportError:
            continue
    print(f"  [!] pypdf/PyPDF2 not installed — skipping {os.path.basename(path)}")
    return ""


def _leer_word(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        print(f"  [!] python-docx not installed — skipping {os.path.basename(path)}")
        return ""


def recuperar_contexto(documentos: list[dict], meta_rule: str,
                       artifact_content: str = "",
                       top_k: int = 4,
                       max_chars: int = 1500) -> str:
    """
    Dense semantic retrieval: embeds a query composed of meta_rule + artifact
    content snippet, computes cosine similarity against all document chunks,
    and returns the top_k most relevant chunks (up to max_chars total).

    Falls back gracefully if documentos is empty.
    """
    if not documentos:
        return "No documentary context available."

    # Build query: meta-rule name + first 200 chars of artifact for context
    snippet = artifact_content[:200].strip() if artifact_content else ""
    query = f"{meta_rule} {snippet}".strip()

    embedder = _get_embedder()
    q_emb = embedder.encode(query, convert_to_numpy=True,
                            show_progress_bar=False, device="cpu")

    # Collect (score, chunk) pairs across all documents
    scored: list[tuple[float, str]] = []
    for doc in documentos:
        sims = _cosine_similarity(q_emb, doc["embeddings"])
        for sim, chunk in zip(sims, doc["chunks"]):
            scored.append((float(sim), chunk))

    if not scored:
        return "No specific documentary context for this meta-rule."

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [chunk for _, chunk in scored[:top_k]]
    contexto = "\n---\n".join(selected)
    return contexto[:max_chars]

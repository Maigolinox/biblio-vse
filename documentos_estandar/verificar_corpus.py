# CHECK THE RETRIEVAL CORPORA
#
# The ISO/IEC 29110 standard documents are not redistributed with this
# repository (see documentos_estandar/README.md). This script reports which
# corpus files are present, their SHA-256, and the number of characters and
# chunks that the retrieval pipeline extracts from each, so that a downloaded
# copy can be compared with the one used for the published results.
#
# Usage (from repo root):  python documentos_estandar/verificar_corpus.py

import hashlib
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_DIR)
sys.path.insert(0, os.path.join(_ROOT, "experimentos"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Reference values of the copies used for the results reported in the article.
REFERENCE = {
    "NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf": {
        "sha256": "614be6e60f4925a9a76fc4f9682255bb53f4e2c24c21f4353225afc07e34ea46",
        "chars": 96552, "chunks": 271,
        "what": "ISO/IEC TR 29110-5-1-2:2011 (English) — main RAG corpus",
        "required_for": "--rag-corpus official (Exp 3, 5, 7, 8 of the mixed, en and noisy conditions)",
    },
    "Parte 5-1-2 GuiadeGestioneIngenieria_PDS 2022.pdf": {
        "sha256": "8701f5594555623938a6de120e6a0119995596a19524f9164c732ee6364e81de",
        "chars": 104318, "chunks": 289,
        "what": "NTP-RT ISO/IEC 29110-5-1-2 (Spanish, Peru) — Spanish pipeline",
        "required_for": "--rag-corpus official_es (Exp 3, 5, 7, 8 of the es condition)",
    },
    "Metareglas extraidas.docx": {
        "sha256": "4eb96b1c6775b55807e086d1ca0faace2664f5458ac8774c85256e0c181f8809",
        "chars": 3864, "chunks": 14,
        "what": "author-derived meta-rule digest (included in this repository)",
        "required_for": "--rag-corpus metarules (pilot sensitivity condition)",
    },
}


def main():
    from rag_utils import _chunkear, _leer_pdf, _leer_word

    missing = []
    for name, ref in REFERENCE.items():
        path = os.path.join(_DIR, name)
        print(f"\n{name}\n  {ref['what']}\n  needed for: {ref['required_for']}")
        if not os.path.exists(path):
            print("  [ ] MISSING — see documentos_estandar/README.md for where to download it")
            missing.append(name)
            continue
        with open(path, "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        text = _leer_pdf(path) if name.lower().endswith(".pdf") else _leer_word(path)
        chunks = _chunkear(text)
        same = digest == ref["sha256"]
        print(f"  [x] present, SHA-256 {'matches' if same else 'DIFFERS FROM'} the reference copy")
        if not same:
            print(f"      yours: {digest}\n      ours:  {ref['sha256']}")
        print(f"      characters extracted: {len(text):,} (reference {ref['chars']:,})")
        print(f"      chunks: {len(chunks)} (reference {ref['chunks']})")
        if not same and (len(text) != ref["chars"] or len(chunks) != ref["chunks"]):
            print("      note: a different edition or PDF text layer will shift retrieval slightly;"
                  "\n      report these counts alongside any results you publish")

    if missing:
        print(f"\n{len(missing)} file(s) missing. Experiments 1, 2, 4 and 6 and all analyses run "
              f"without them; the retrieval conditions do not.")
        return 1
    print("\nAll retrieval corpora are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Retrieval corpora (RAG)

The RAG experiments retrieve from two corpora. One of them is included here; the
other two files are the ISO/IEC 29110 standard documents, which **are not
redistributed with this repository** because their copyright belongs to ISO/IEC
and to the national standards body that published the Spanish translation. This
page explains how to obtain them and how to verify that you have the same
editions that produced the published results.

| File | Used by | Included here |
|---|---|---|
| `Metareglas extraidas.docx` | author-derived digest (pilot sensitivity condition, `--rag-corpus metarules`) | yes, it is our own material |
| `NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf` | main RAG condition (`--rag-corpus official`) | no, see below |
| `Parte 5-1-2 GuiadeGestioneIngenieria_PDS 2022.pdf` | Spanish pipeline (`--rag-corpus official_es`) | no, see below |

## 1. English edition — ISO/IEC TR 29110-5-1-2:2011

*Software engineering — Lifecycle profiles for Very Small Entities (VSEs) —
Part 5-1-2: Management and engineering guide: Generic profile group: Basic
profile*, first edition 2011-05-15.

The ISO/IEC 29110 Technical Reports are distributed at no charge. ISO retired
the old "Publicly Available Standards" download page; the documents are now
obtained, still free of charge, from the ISO and IEC webstores:

- ISO catalogue entry: <https://www.iso.org/standard/51153.html>
- ISO freely available standards index: <https://standards.iso.org/ittf/PubliclyAvailableStandards/index.html>
- List maintained by ISO/IEC JTC 1/SC 7: <https://sites.google.com/site/isoiecjtc1sc7/freely-available-standards>

Download the English PDF and save it in this directory as:

```
NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf
```

## 2. Spanish edition — NTP-RT ISO/IEC 29110-5-1-2 (Peru)

*Ingeniería de Software. Perfiles del ciclo de vida para las pequeñas
organizaciones (PO). Parte 5-1-2: Guía de gestión e ingeniería: Grupo de perfil
genérico. Perfil básico*, INDECOPI/INACAL, first edition 2012.

- INACAL virtual store: <https://tiendavirtual.inacal.gob.pe/0/modulos/TIE/TIE_DetallarProducto.aspx?PRO=2015>
- Reference page of the Peruvian mirror committee (CTN-ISSI, PUCP): <https://ctn-issi.pucp.pe/normas-tecnicas-peruanas>

Save it in this directory as:

```
Parte 5-1-2 GuiadeGestioneIngenieria_PDS 2022.pdf
```

Any faithful Spanish edition of Part 5-1-2 reproduces the experiment; the
verification below only tells you whether your copy is byte-identical to ours.

## 3. Verify your copies

```bash
python documentos_estandar/verificar_corpus.py
```

The script reports, for each file, whether it is present, its SHA-256, and the
number of characters and chunks that the retrieval pipeline extracts from it.
The copies used for the published results are:

| File | SHA-256 | Pages | Characters extracted | Chunks |
|---|---|---|---|---|
| `NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf` | `614be6e60f4925a9a76fc4f9682255bb53f4e2c24c21f4353225afc07e34ea46` | 54 | 96,552 | 271 |
| `Parte 5-1-2 GuiadeGestioneIngenieria_PDS 2022.pdf` | `8701f5594555623938a6de120e6a0119995596a19524f9164c732ee6364e81de` | 83 | 104,318 | 289 |
| `Metareglas extraidas.docx` | `4eb96b1c6775b55807e086d1ca0faace2664f5458ac8774c85256e0c181f8809` | -- | 3,864 | 14 |

If the character and chunk counts of your copy match, the retrieval condition is
reproduced exactly. If they differ (different edition, or a different PDF text
layer), retrieval results may shift slightly; report the counts produced by
`verificar_corpus.py` alongside any results you publish.

The experiments that do not use retrieval (Exp 1, 2, 4, 6) and all analyses run
without these files.

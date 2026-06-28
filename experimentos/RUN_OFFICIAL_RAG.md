# Official ISO/IEC 29110 RAG rerun

Run commands from the repository root (`D:\biblio_vse` in Windows or
`/mnt/d/biblio_vse` in WSL).

## 1. Install the PDF and retrieval dependencies

```bash
python -m pip install -r requirements.txt
```

## 2. Verify the two explicitly separated corpora

```text
documentos_estandar/Metareglas extraidas.docx
documentos_estandar/NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf
```

`--rag-corpus metarules` reproduces the author-derived RAG condition.
`--rag-corpus official` uses only the official guide. Do not use `all` for the
main circularity test because it mixes the two sources.

## 3. Run the four official-corpus RAG configurations

PowerShell:

```powershell
python experimentos/experimento_rag_3.py --rag-corpus official 2>&1 | Tee-Object resultados_rag_official_exp3.txt
python experimentos/experimento_zeroshot_rag_5.py --rag-corpus official 2>&1 | Tee-Object resultados_rag_official_exp5.txt
python experimentos/experimento_rag_steering_7.py --rag-corpus official --lang es 2>&1 | Tee-Object resultados_rag_official_exp7.txt
python experimentos/experimento_zeroshot_rag_steering_8.py --rag-corpus official --lang es 2>&1 | Tee-Object resultados_rag_official_exp8.txt
```

Bash/WSL:

```bash
python experimentos/experimento_rag_3.py --rag-corpus official 2>&1 | tee resultados_rag_official_exp3.txt
python experimentos/experimento_zeroshot_rag_5.py --rag-corpus official 2>&1 | tee resultados_rag_official_exp5.txt
python experimentos/experimento_rag_steering_7.py --rag-corpus official --lang es 2>&1 | tee resultados_rag_official_exp7.txt
python experimentos/experimento_zeroshot_rag_steering_8.py --rag-corpus official --lang es 2>&1 | tee resultados_rag_official_exp8.txt
```

Run all commands in the same software environment and with deterministic model
generation settings. Keep the existing `metarules` results as the comparison
condition; do not overwrite them.

## 4. Recompute the existing steering interaction analysis

```bash
python experimentos/build_predictions_matrix.py
python experimentos/statistical_resampling.py
python experimentos/steering_interaction_analysis.py
```

Build and analyze the official-corpus matrix with:

```bash
python experimentos/build_official_rag_matrix.py
PREDICTIONS_MATRIX=experimentos/predictions_n32_official_rag.json \
  STATISTICAL_ANALYSIS_OUT=experimentos/statistical_analysis_official_rag.json \
  python experimentos/statistical_resampling.py
PREDICTIONS_MATRIX=experimentos/predictions_n32_official_rag.json \
  STEERING_INTERACTION_OUT=experimentos/steering_interaction_official_rag.json \
  python experimentos/steering_interaction_analysis.py
```

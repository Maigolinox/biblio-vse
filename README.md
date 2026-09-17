# Biblio-VSE — Benchmark and Experiments

Research artifacts for the article **"Corpus, Prompt, and Steering Effects in LLM-Based ISO/IEC 29110 Compliance Classification: A Privacy-Preserving Benchmark Study"** (IEEE Access, under revision).

Biblio-VSE is a synthetic benchmark for **artifact-level ISO/IEC 29110 compliance classification**: given one software artifact (source code, project document, or CI/CD configuration) and one operational meta-rule, decide whether the artifact complies (1) or violates the rule (0). This repository contains everything you need to rebuild the benchmark, rerun every experiment, and regenerate every table and statistic in the paper.

> The benchmark's measurable characteristics are calibrated to a private, previously assessed ISO/IEC 29110 project. That project is **not** included; only its aggregate statistics are used (see [Private reference data](#private-reference-data)).

---

## Contents

1. [Repository layout](#repository-layout)
2. [Benchmark versions](#benchmark-versions)
3. [Setup](#setup)
4. [Reproducing the results](#reproducing-the-results)
5. [Validation checks](#validation-checks)
6. [Artifact inventory](#artifact-inventory)
7. [Paper-to-file map](#paper-to-file-map)
8. [Private reference data](#private-reference-data)
9. [Notes and limitations](#notes-and-limitations)

---

## Repository layout

```
.
├── catalogo/  prestamos/  config/  manage.py   Synthetic Django project ("Biblio-VSE") whose git
│                                                branches feat/r*-positiva|negativa hold the original
│                                                compliant/violating mutations (see extractor.py)
├── dataset_isomorfico.json                      Benchmark v1, N=32 (first submission; unchanged)
├── dataset_isomorfico_n96.json                  Benchmark v2, N=96, Spanish
├── dataset_isomorfico_n96_en.json               Benchmark v2, N=96, English edition (paired)
├── dataset_isomorfico_n96_noisy.json            Benchmark v2, N=96, noise-injected stress test
├── dataset_v2/                                  Sources and builders of benchmark v2
├── documentos_estandar/                         RAG corpora (official guide EN/ES, author digest)
├── experimentos/                                Experiment, analysis, and result files
├── resultados/n32/                              Raw experiment logs of the N=32 study
├── resultados/n96/<condition>/                  Raw experiment logs of the N=96 study
├── extractor.py                                 Extracts artifacts from the mutation branches
├── model_loader.py                              Model catalog (IDs, steering layers)
├── requirements.txt                             Dependencies of the synthetic Django project
└── requirements-experiments.txt                 Pinned dependencies of the experiments
```

## Benchmark versions

| Version | File | N | Content |
|---|---|---|---|
| v1 | `dataset_isomorfico.json` | 32 | 20 core mutations + 12 adversarial (6 Type-B, 6 Type-C). Results of the first submission. Kept byte-for-byte. |
| v2 | `dataset_isomorfico_n96.json` | 96 | The 32 v1 artifacts + 64 new ones; 48 compliant / 48 violating; 21 Type-B, 16 Type-C; 43 source code, 37 documents, 16 CI/CD; 53 mutation scenarios. |
| v2-en | `dataset_isomorfico_n96_en.json` | 96 | English translation of v2, paired artifact by artifact (same IDs, labels, scenarios). |
| v2-noisy | `dataset_isomorfico_n96_noisy.json` | 96 | v2 embedded in label-preserving enterprise noise (license headers, unrelated helpers, wiki-export residue, unrelated CI jobs). |

The v1 → v2 changes to the 32 original artifacts are listed in `dataset_v2/build_dataset_n96.py`:

- Four duplicated IDs were made unique (`SMP-GOBERNANZA-SRC/DOC-POS`, `SMP-TRAZABILIDAD-POS-A/B`).
- Comments that stated the label inside six artifacts were removed (for example `# MAL: Credenciales en texto plano`).

Each record has these fields:

| Field | Meaning |
|---|---|
| `id_muestra` | Artifact ID. `SMP-*`: core v1. `ADV-B/C-*`: adversarial v1. `EXT-*`: v2 extension. `EXT-ADVB/ADVC-*`: adversarial v2. |
| `meta_regla` | Meta-rule: DOCUMENTAL, CALIDAD, GOBERNANZA, SEGURIDAD, TRAZABILIDAD, PRUEBAS, RESPALDO, ACUERDOS, INFRA (English names in v2-en). |
| `tipo_artefacto` | `codigo_fuente`, `documento_texto`, or `pipeline_ci` |
| `contenido_texto` | Artifact content |
| `etiqueta_clase` | Ground truth (1 = compliant, 0 = violation) |
| `escenario` | Mutation scenario (dependence cluster used by the statistics) |
| `adversarial`, `adversarial_nota` | `tipo_b` (keywords in a non-compliant context) or `tipo_c` (compliant without the keywords), with a rationale |
| `origen` | `original_v1` or `extension_v2` |

## Setup

Hardware used: NVIDIA RTX 4060 (8 GB VRAM), 64 GB RAM, Windows 11. All models run with 4-bit NF4 quantization.

```bash
conda create -n aud_llm python=3.10.19
conda activate aud_llm
pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements-experiments.txt
```

Model weights are downloaded from Hugging Face on first use. Gemma-2 and Mistral require accepting their licenses on Hugging Face (`huggingface-cli login`). The models are:

- `google/gemma-2-9b-it`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `Qwen/Qwen2.5-7B-Instruct`
- `microsoft/Phi-3.5-mini-instruct`
- `sentence-transformers/all-MiniLM-L6-v2` (RAG embedder, runs on the CPU)

For the frontier-model reference (Gemini), put your own key in a git-ignored `.env` file:

```
GEMINI_API_KEY=your-key
```

Run every command from the repository root.

## Reproducing the results

### 1. Rebuild the benchmark (seconds, no GPU)

```bash
python dataset_v2/build_dataset_n96.py         # -> dataset_isomorfico_n96.json
python dataset_v2/build_dataset_n96_en.py      # -> dataset_isomorfico_n96_en.json
python dataset_v2/build_dataset_n96_noisy.py   # -> dataset_isomorfico_n96_noisy.json
```

### 2. Run the eight configurations × four local models (GPU)

| Exp | Configuration | Script |
|---|---|---|
| 1 | Baseline (no structuring) | `experimentos/experimento_baseline_1.py` |
| 2 | Structured zero-shot (ZS) | `experimentos/experimento_zeroshot_2.py` |
| 3 | RAG | `experimentos/experimento_rag_3.py` |
| 4 | Activation steering | `experimentos/experimento_steering_4.py` |
| 5 | ZS + RAG | `experimentos/experimento_zeroshot_rag_5.py` |
| 6 | ZS + steering | `experimentos/experimento_zeroshot_steering_6.py` |
| 7 | RAG + steering | `experimentos/experimento_rag_steering_7.py` |
| 8 | ZS + RAG + steering | `experimentos/experimento_zeroshot_rag_steering_8.py` |

All scripts accept these options:

- `--dataset PATH`
- `--prompt-lang mixed|es|en`
- `--models gemma2,mistral,qwen25,phi35`
- RAG scripts: `--rag-corpus metarules|official|official_es`
- Steering scripts: `--lang es|en` (anchor language)

`experimentos/run_condition.py` runs a complete condition. It writes one log per experiment to `resultados/n96/<condition>/`, and you can resume it after an interruption:

```bash
python experimentos/run_condition.py --condition mixed                 # main results (~1 h)
python experimentos/run_condition.py --condition es                    # monolingual Spanish
python experimentos/run_condition.py --condition en                    # monolingual English
python experimentos/run_condition.py --condition noisy --exps 1,2,5,6  # noise stress test
```

| Condition | Artifacts | Instructions | Steering anchors | RAG corpus |
|---|---|---|---|---|
| `mixed` | Spanish | English instructions, bilingual rule names (original design) | Spanish | Official guide (English) |
| `es` | Spanish | Spanish | Spanish | Official guide (Spanish edition) |
| `en` | English | English | English | Official guide (English) |
| `noisy` | Spanish + noise | as `mixed` | Spanish | Official guide (English) |

### 3. Frontier-model reference (Gemini API; Exp 1, 2, 3, 5)

Steering needs access to hidden states, so Exp 4, 6, 7 and 8 are not applicable to a hosted API. Responses are cached in `resultados/n96/gemini_cache.jsonl`, which makes reruns free and deterministic.

```bash
python experimentos/experimento_gemini.py --condition mixed   # newest stable Gemini Flash
python experimentos/experimento_gemini.py --condition es
python experimentos/experimento_gemini.py --condition en
python experimentos/experimento_gemini.py --condition noisy --exps 1,2,5
```

### 4. Analyses (minutes, no GPU)

```bash
for c in mixed es en noisy; do
  python experimentos/build_matrix_n96.py --condition $c           # predictions_n96_<c>.json/.csv
  python experimentos/statistical_analysis_n96.py --condition $c   # CIs, MCC, BAcc, tests, costs
  python experimentos/subset_analysis_n96.py --condition $c        # adversarial/origin/rule subsets
done
for c in mixed es en; do python experimentos/steering_interaction_n96.py --condition $c; done
python experimentos/compare_conditions.py --a es --b en        # language study
python experimentos/compare_conditions.py --a mixed --b es
python experimentos/compare_conditions.py --a mixed --b en
python experimentos/compare_conditions.py --a mixed --b noisy  # robustness study
python experimentos/lexical_baselines.py --dataset dataset_isomorfico_n96.json --out experimentos/lexical_baselines_n96.json
python experimentos/lexical_baselines.py --dataset dataset_isomorfico_n96_en.json --out experimentos/lexical_baselines_n96_en.json
python experimentos/calibration_n96.py --dataset dataset_isomorfico_n96.json --private-dir <D_private>   # needs the private repository
```

### 5. First-submission results (N=32)

```bash
python experimentos/build_predictions_matrix.py      # validates all 32 cells against the manuscript F1 values
python experimentos/build_official_rag_matrix.py
python experimentos/statistical_resampling.py
PREDICTIONS_MATRIX=experimentos/predictions_n32_official_rag.json \
  STATISTICAL_ANALYSIS_OUT=experimentos/statistical_analysis_official_rag.json \
  python experimentos/statistical_resampling.py
python experimentos/steering_interaction_analysis.py
python experimentos/lexical_baselines.py
python experimentos/classic_baseline.py
python experimentos/isomorphism_metrics.py
```

The α-selection LOO analysis (`loo_steering.py`), the layer sweeps (`layer_sensitivity.py`), the anchor-language ablation (`ablacion_espanol.py`), and the quantization ablation (`ablacion_cuantizacion.py`) were run on N=32. Their outputs are the `loo_results_*.json` and `layer_sensitivity_*.json` files.

## Validation checks

The pipeline fails loudly when the data are inconsistent:

- `build_dataset_n96.py` asserts N=96, a 48/48 label balance and unique IDs. It also checks the adversarial design: every Type-B artifact must trigger the regex baseline and every Type-C artifact must evade it.
- `build_dataset_n96_en.py` checks that all 96 translations exist, re-validates the adversarial design with English regex patterns, and reports untranslated Spanish fragments.
- `build_dataset_n96_noisy.py` checks every noise block against the regex patterns of all nine rules, so noise cannot add compliance cues. The noisy code still parses.
- `build_matrix_n96.py` checks artifact order and ground truth for every model block in every log, and skips incomplete runs.
- `build_predictions_matrix.py` (N=32) checks every parsed cell against the F1 values printed in the manuscript.

Quick smoke test (about 30 s on the GPU):

```bash
python -c "import json; d=json.load(open('dataset_isomorfico_n96.json', encoding='utf-8')); json.dump(d[:3], open('mini.json', 'w', encoding='utf-8'), ensure_ascii=False)"
python experimentos/experimento_zeroshot_rag_steering_8.py --dataset mini.json --prompt-lang es --rag-corpus official_es --lang es --models phi35
```

## Artifact inventory

### Benchmark construction

| File | Purpose |
|---|---|
| `extractor.py` | Builds artifacts by diffing each `feat/r*` mutation branch against `master` |
| `dataset_v2/extension_es_{a,b,c}.py` | The 64 v2 artifacts (Spanish), grouped by meta-rule |
| `dataset_v2/en_originals.py`, `dataset_v2/en_extension_{a,b,c}.py` | English translations of all 96 artifacts |
| `dataset_v2/build_dataset_n96*.py` | Builders of v2, v2-en and v2-noisy |
| `documentos_estandar/NORMA_Part 5_1_2_Management_Engineering_guide_ISO29110.pdf` | Official ISO/IEC 29110 Part 5-1-2 guide (English); main RAG corpus |
| `documentos_estandar/Parte 5-1-2 GuiadeGestioneIngenieria_PDS 2022.pdf` | Spanish edition of the guide; RAG corpus of the `es` condition |
| `documentos_estandar/Metareglas extraidas.docx` | Author-derived meta-rule digest (circularity sensitivity condition of the N=32 study) |

### Experiments

| File | Purpose |
|---|---|
| `experimentos/utils.py` | Model loading, prompt templates (mixed/es/en), inference, steering vector extraction and injection |
| `experimentos/rag_utils.py` | Chunking, embedding, dense top-k retrieval |
| `experimentos/experimento_*_{1..8}.py` | The eight configurations |
| `experimentos/run_condition.py` | Runner for a full condition |
| `experimentos/experimento_gemini.py` | Frontier-model reference via the Gemini API |
| `experimentos/loo_steering.py`, `layer_sensitivity.py`, `ablacion_espanol.py`, `ablacion_cuantizacion.py` | α-selection LOO, layer sweeps, anchor-language and quantization ablations (N=32) |

### Analyses

| File | Purpose |
|---|---|
| `experimentos/build_matrix_n96.py` | Log parser → canonical prediction matrix |
| `experimentos/statistical_analysis_n96.py` | F1, MCC, BAcc, macro-F1, costs, grouped bootstrap CIs, scenario and meta-rule permutation tests, McNemar, Holm |
| `experimentos/steering_interaction_n96.py` | Factorial steering × prompting / steering × RAG interactions |
| `experimentos/compare_conditions.py` | Paired comparison of two conditions (language and noise studies) |
| `experimentos/subset_analysis_n96.py` | Adversarial / origin / per-rule subsets, hardest artifacts |
| `experimentos/lexical_baselines.py`, `classic_baseline.py` | TF-IDF baselines (leave-one-rule-out) and regex baseline |
| `experimentos/calibration_n96.py`, `isomorphism_metrics.py`, `dependency_graph.py`, `measure_private_repo.py` | Distributional calibration against the private repository (V(G), AST depth, Fog, lexical measures, import graph, TOST) |
| `experimentos/build_predictions_matrix.py`, `build_official_rag_matrix.py`, `statistical_resampling.py`, `steering_interaction_analysis.py` | N=32 analyses of the first submission |
| `experimentos/error_analysis.py`, `measure_fog.py`, `tune_fog.py`, `verify_metrics.py`, `fix_import_density.py` | Legacy helpers of the N=20 pilot and the v1 calibration, kept for provenance |

### Results

| File | Content |
|---|---|
| `resultados/n96/<condition>/exp<N>.txt`, `gemini_exp<N>.txt` | Raw per-artifact predictions of the N=96 study |
| `resultados/n96/gemini_cache.jsonl` | Raw Gemini responses |
| `experimentos/predictions_n96_<condition>.json/.csv` | Prediction matrices (N=96) |
| `experimentos/statistical_analysis_n96_<condition>.json` | Statistics (N=96) |
| `experimentos/steering_interaction_n96_<condition>.json` | Steering interactions (N=96) |
| `experimentos/compare_n96_<a>_vs_<b>.json` | Language and noise comparisons |
| `experimentos/subset_analysis_n96_<condition>.json` | Subset and error analysis |
| `experimentos/lexical_baselines_n96*.json` | TF-IDF baselines (N=96, ES/EN) |
| `experimentos/calibration_n32.json`, `calibration_n96.json` | Calibration aggregates (synthetic vs private) |
| `resultados/n32/*.txt` | Raw logs of the N=32 study |
| `experimentos/predictions_n32*.json/.csv`, `statistical_analysis_*.json`, `steering_interaction_*.json`, `lexical_baselines_n32.json`, `loo_results_*.json`, `layer_sensitivity_*.json` | N=32 results |

## Paper-to-file map

| Manuscript element | Files |
|---|---|
| Meta-rules and detection predicates | `experimentos/utils.py` (`_CRITERIOS_ZEROSHOT*`), `experimentos/classic_baseline.py` (`PATTERNS`) |
| Distributional calibration (§III-B) | `experimentos/calibration_n96.py`, `calibration_n*.json`, `dependency_graph.py` |
| Benchmark construction (§III-C) | `extractor.py`, `dataset_v2/`, `dataset_isomorfico*.json` |
| Pipeline: prompting, RAG, steering (§III-D) | `experimentos/utils.py`, `rag_utils.py`, `experimento_*.py` |
| Main results, forest plot, confusion matrices | `statistical_analysis_n96_mixed.json`, `predictions_n96_mixed.json` |
| Frontier-model reference | `experimento_gemini.py`, `resultados/n96/*/gemini_exp*.txt` |
| Language study | `compare_n96_es_vs_en.json`, `compare_n96_mixed_vs_*.json` |
| Noise robustness study | `dataset_isomorfico_n96_noisy.json`, `compare_n96_mixed_vs_noisy.json` |
| Steering interactions | `steering_interaction_n96_*.json` |
| Error analysis | `subset_analysis_n96_*.json` |
| LOO, layer sweeps, quantization, anchor language (N=32) | `loo_results_*.json`, `layer_sensitivity_*.json`, `ablacion_*.py` |

## Private reference data

The calibration reference `D_private` is a confidential repository of a company assessed under ISO/IEC 29110. The disclosure agreement allows publishing aggregate statistics only. Those aggregates are:

- hard-coded in `experimentos/isomorphism_metrics.py`;
- re-measured, as aggregates only, in `experimentos/calibration_n*.json`.

Scripts that read the private repository (`measure_private_repo.py`, `dependency_graph.py`, `calibration_n96.py --private-dir`) print aggregates only. They cannot be run without access to that repository.

## Notes and limitations

- **Scope.** Biblio-VSE measures artifact-level rule classification. It says nothing about organizational conformance or certification readiness.
- **Labels.** Labels follow the mutation protocol and the meta-rule criteria. They are not the result of independent auditor adjudication (see the threats to validity in the paper).
- **RAG corpora.** The ISO/IEC 29110 Part 5-1-2 guides are included only so that the RAG conditions can be reproduced. Their copyright belongs to their publishers.
- **Steering vectors** are not distributed as tensors. They are a deterministic function of the anchor prompts in `experimentos/utils.py` and the public checkpoints.

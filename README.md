# Multimodal Financial Document Auditor (Enterprise-Grade)

Serious, hybrid AI system for invoice/receipt auditing with multimodal reasoning and rule-based validation.

## Quickstart

1. Create and activate a Python venv
2. Install deps
3. (Optional) Install ML deps for Qwen-VL + PaddleOCR
4. Run a sample pipeline

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-ml.txt
python -m src.main --input samples/invoice_01.png --vendor_db data/vendors.csv --contract_text data/contract.txt --json_out reports/output.json
```

## Architecture

Image -> OCR -> Structured Parser -> VLM Reasoning -> Logical Validator -> Risk Engine -> Report Generator

## Modules

- OCR Layer: PaddleOCR or Donut
- Structured Field Extraction: Qwen-VL prompt for JSON
- Logical Validation Engine: arithmetic + policy checks
- Risk Reasoning: VLM risk score + justification
- Report Generator: explainable risk report

## Datasets

- Real: extracted into `data/real/`
- `archive_1`: images only (unlabeled, useful for OCR/VLM pretraining)
- `archive_2`: invoice images + CSV with JSON fields (supervised extraction)
- Combined manifest: `data/real/manifest.jsonl` (built from both)

## Splits

Create train/val/test splits from the manifest:

```bash
python scripts/split_manifest.py --manifest data/real/manifest.jsonl --out_dir data/real/splits --labeled_only
```

Outputs:
- `data/real/splits/train.jsonl`
- `data/real/splits/val.jsonl`
- `data/real/splits/test.jsonl`

## Evaluation

Prepare a predictions file with:
- `image_path`
- `extracted_json` (your model output in the target schema)

Then run:

```bash
python scripts/evaluate_extraction.py --ground_truth data/real/splits/test.jsonl --predictions data/real/preds.jsonl
```

## Training / Heavy Compute

If training or large model inference is heavy locally, use Google Colab (T4 GPU). See `notebooks/colab_qwen_vl.ipynb`.

## Folder Structure

- src/: pipeline code
- scripts/: dataset generation and evaluation
- configs/: runtime configs
- schemas/: JSON schemas
- data/: datasets
- reports/: generated reports

## Notes

- This repo is designed for enterprise-style rigor: metrics, error analysis, and explainability.
- No training required by default; models can be swapped in when GPU is available.

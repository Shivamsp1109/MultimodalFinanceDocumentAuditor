from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def normalize_path(p: Path) -> str:
    return str(p.as_posix())


def build_from_archive_2(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    batch_root = root / "batch_1" / "batch_1"
    csvs = list(batch_root.glob("batch1_*.csv"))
    for csv_path in csvs:
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            fname = row["File Name"]
            json_data = row.get("Json Data", "")
            ocr_text = row.get("OCRed Text", "")
            image_path = None
            for sub in ["batch1_1", "batch1_2", "batch1_3"]:
                candidate = batch_root / sub / fname
                if candidate.exists():
                    image_path = candidate
                    break
            if image_path is None:
                continue
            rows.append(
                {
                    "image_path": normalize_path(image_path),
                    "json_data": json.loads(json_data) if isinstance(json_data, str) else {},
                    "ocr_text": ocr_text if isinstance(ocr_text, str) else "",
                    "source": "archive_2",
                    "labeled": True,
                }
            )
    return rows


def build_from_archive_1(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for img in root.glob("*.jpg"):
        rows.append(
            {
                "image_path": normalize_path(img),
                "json_data": {},
                "ocr_text": "",
                "source": "archive_1",
                "labeled": False,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--archive1", required=True)
    parser.add_argument("--archive2", required=True)
    args = parser.parse_args()

    archive1 = Path(args.archive1)
    archive2 = Path(args.archive2)

    rows = []
    rows.extend(build_from_archive_1(archive1))
    rows.extend(build_from_archive_2(archive2))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()

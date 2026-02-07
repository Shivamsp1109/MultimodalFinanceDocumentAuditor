from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=float, default=0.8)
    parser.add_argument("--val", type=float, default=0.1)
    parser.add_argument("--test", type=float, default=0.1)
    parser.add_argument("--labeled_only", action="store_true")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    out_dir = Path(args.out_dir)

    rows = load_jsonl(manifest)
    if args.labeled_only:
        rows = [r for r in rows if r.get("labeled")]

    total = len(rows)
    if total == 0:
        raise SystemExit("No rows found to split.")

    if abs((args.train + args.val + args.test) - 1.0) > 1e-6:
        raise SystemExit("train + val + test must sum to 1.0")

    random.seed(args.seed)
    random.shuffle(rows)

    n_train = int(total * args.train)
    n_val = int(total * args.val)
    n_test = total - n_train - n_val

    train_rows = rows[:n_train]
    val_rows = rows[n_train : n_train + n_val]
    test_rows = rows[n_train + n_val :]

    write_jsonl(out_dir / "train.jsonl", train_rows)
    write_jsonl(out_dir / "val.jsonl", val_rows)
    write_jsonl(out_dir / "test.jsonl", test_rows)

    print(f"Total: {total}")
    print(f"Train: {len(train_rows)}")
    print(f"Val: {len(val_rows)}")
    print(f"Test: {len(test_rows)}")


if __name__ == "__main__":
    main()

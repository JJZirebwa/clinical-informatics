from __future__ import annotations

import argparse

from .generate_synthetic_data import generate_all_tables, write_tables
from .metrics import build_metric_tables
from .reporting import write_all_reports
from .validation import run_validation_checks


def build(seed: int = 42) -> dict[str, object]:
    tables = generate_all_tables(seed=seed)
    write_tables(tables)
    validation = run_validation_checks(tables)
    metrics = build_metric_tables(tables, validation)
    write_all_reports(tables, validation, metrics, seed)
    return {"tables": tables, "validation": validation, "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the synthetic clinical informatics project outputs.")
    parser.add_argument("--seed", type=int, default=42, help="Synthetic data seed.")
    args = parser.parse_args()
    build(seed=args.seed)
    print(f"Synthetic project outputs regenerated with seed {args.seed}.")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from .config import PROJECT_ROOT
from .generate_synthetic_data import generate_all_tables, write_tables
from .metrics import build_metric_tables
from .reporting import write_all_reports
from .validation import run_validation_checks


def build(
    seed: int = 42, output_root: Path | str = PROJECT_ROOT
) -> dict[str, object]:
    project_root = Path(output_root)
    tables = generate_all_tables(seed=seed)
    write_tables(tables, project_root / "data" / "synthetic")
    validation = run_validation_checks(tables)
    metrics = build_metric_tables(tables, validation)
    write_all_reports(tables, validation, metrics, seed, project_root)
    return {"tables": tables, "validation": validation, "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate the synthetic clinical informatics project outputs.")
    parser.add_argument("--seed", type=int, default=42, help="Synthetic data seed.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project-shaped output directory. Defaults to the repository root.",
    )
    args = parser.parse_args()
    build(seed=args.seed, output_root=args.output_root)
    print(
        f"Synthetic project outputs regenerated with seed {args.seed} "
        f"under {args.output_root}."
    )


if __name__ == "__main__":
    main()

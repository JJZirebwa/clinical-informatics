from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import DATA_DICTIONARY, FIGURE_DIR, OUTPUT_DIR, TABLE_NAMES, ensure_project_directories


def write_data_dictionary(path: Path, tables: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Data Dictionary",
        "",
        "All datasets in this repository are synthetic and created for demonstration. They do not contain real patient, site, sponsor, or EDC data.",
        "",
    ]
    for table_name in TABLE_NAMES:
        frame = tables[table_name]
        lines.extend([f"## {table_name}.csv", "", "| Field | Type | Meaning / notes |", "|---|---|---|"])
        for column in frame.columns:
            dtype = str(frame[column].dtype)
            meaning = DATA_DICTIONARY.get(table_name, {}).get(column, "Synthetic demonstration field.")
            lines.append(f"| `{column}` | `{dtype}` | {meaning} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation_report(path: Path, validation: dict[str, pd.DataFrame]) -> None:
    summary = validation["summary"]
    issues = validation["issues"]
    lines = [
        "# Validation Report",
        "",
        "This report demonstrates awareness-level clinical data validation checks on synthetic data. It is not a validated clinical data-management system and is not suitable for regulated operational use.",
        "",
        "## Summary",
        "",
        "| Check | Status | Severity | Issue count |",
        "|---|---:|---|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(f"| `{row.check_id}` | {row.status} | {row.severity} | {row.issue_count} |")

    lines.extend(["", "## Highest Priority Issues", ""])
    priority = issues[issues["severity"].isin(["Critical", "High"])].head(20)
    if priority.empty:
        lines.append("No critical or high-severity synthetic validation issues were generated.")
    else:
        lines.extend(["| Severity | Table | Record | Message |", "|---|---|---|---|"])
        for row in priority.itertuples(index=False):
            lines.append(f"| {row.severity} | {row.table_name} | `{row.record_id}` | {row.message} |")

    lines.extend(
        [
            "",
            "## Assumption Log",
            "",
            "- Query ageing threshold: open or answered queries older than 14 days require review.",
            "- Visit-window flags are operational prompts, not automatic protocol-deviation adjudications.",
            "- Lab plausibility thresholds are broad synthetic checks and do not represent protocol safety criteria.",
            "- Serious or ongoing adverse events are highlighted when follow-up status remains open.",
            "- Validation output is issue-oriented so a dashboard user can move from metric to record-level review.",
            "",
            "## ALCOA+ Awareness Note",
            "",
            "The checks are designed to make records attributable to a table and record identifier, readable in tabular form, time-aware through date fields, original to the generated synthetic record, and accurate enough for demonstration. The reports also emphasize completeness, consistency, durable CSV/Markdown outputs, and availability for review.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_metrics_summary(path: Path, metrics: dict[str, pd.DataFrame]) -> None:
    overview = metrics["overview"].iloc[0].to_dict()
    lines = [
        "# Operational Metrics Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in overview.items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The synthetic dashboard emphasizes site-level progress, data-cleaning workload, visit-window adherence, adverse-event visibility, and validation flags. These are operational prompts for analyst review rather than clinical judgments.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_method_manifest(path: Path, seed: int, tables: dict[str, pd.DataFrame], metrics: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Build Manifest",
        "",
        f"- Synthetic generation seed: `{seed}`",
        "- Data cut date: `2026-06-30`",
        "- Scenario: multicenter Phase II metabolic outcomes trial operations demo",
        "",
        "## Generated Tables",
        "",
        "| Table | Rows |",
        "|---|---:|",
    ]
    for table_name in TABLE_NAMES:
        lines.append(f"| `{table_name}.csv` | {len(tables[table_name])} |")
    lines.extend(["", "## Metric Tables", "", "| Table | Rows |", "|---|---:|"])
    for table_name, frame in metrics.items():
        lines.append(f"| `{table_name}.csv` | {len(frame)} |")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(metrics: dict[str, pd.DataFrame]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    site_metrics = metrics["site_metrics"].sort_values("site_id")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(site_metrics["site_id"], site_metrics["enrolled_n"], label="Enrolled", color="#2f6f73")
    ax.plot(site_metrics["site_id"], site_metrics["target_enrollment"], marker="o", color="#b45f06", label="Target")
    ax.set_title("Synthetic Enrollment Progress by Site")
    ax.set_xlabel("Site")
    ax.set_ylabel("Participants")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "site_enrollment_progress.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(site_metrics["site_id"], site_metrics["open_query_n"], color="#7f4f24")
    ax.set_title("Open or Answered Query Burden by Site")
    ax.set_xlabel("Site")
    ax.set_ylabel("Open/answered queries")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "site_query_burden.png", dpi=180)
    plt.close(fig)

    visit_summary = (
        metrics["visit_adherence"].groupby("visit_name", as_index=False)[["scheduled_n", "outside_window_n"]].sum()
    )
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(visit_summary["visit_name"], visit_summary["outside_window_n"], color="#8a3ffc")
    ax.set_title("Visit Window Misses by Scheduled Visit")
    ax.set_xlabel("Synthetic visits outside window")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "visit_window_misses.png", dpi=180)
    plt.close(fig)


def write_output_tables(validation: dict[str, pd.DataFrame], metrics: dict[str, pd.DataFrame]) -> None:
    ensure_project_directories()
    validation["issues"].to_csv(OUTPUT_DIR / "validation_issues.csv", index=False)
    validation["summary"].to_csv(OUTPUT_DIR / "validation_summary.csv", index=False)
    for name, frame in metrics.items():
        frame.to_csv(OUTPUT_DIR / f"{name}.csv", index=False)


def write_all_reports(
    tables: dict[str, pd.DataFrame],
    validation: dict[str, pd.DataFrame],
    metrics: dict[str, pd.DataFrame],
    seed: int,
) -> None:
    ensure_project_directories()
    write_output_tables(validation, metrics)
    write_data_dictionary(Path(__file__).resolve().parents[2] / "data" / "data_dictionary.md", tables)
    write_validation_report(OUTPUT_DIR / "validation_report.md", validation)
    write_metrics_summary(OUTPUT_DIR / "metrics_summary.md", metrics)
    write_method_manifest(OUTPUT_DIR / "build_manifest.md", seed, tables, metrics)
    write_figures(metrics)


from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .config import (
    DATA_CUT_DATE,
    DATA_DICTIONARY,
    FIGURE_DIR,
    MILESTONE_DELAY_TOLERANCE_DAYS,
    OUTPUT_DIR,
    PROJECT_ROOT,
    QUERY_AGE_THRESHOLD_DAYS,
    TABLE_NAMES,
)


def write_data_dictionary(path: Path, tables: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Data dictionary",
        "",
        "All datasets in this repository are synthetic, generated with a fixed seed. They contain no real patient, site, sponsor or EDC data.",
        "",
    ]
    for table_name in TABLE_NAMES:
        frame = tables[table_name]
        lines.extend([f"## {table_name}.csv", "", "| Field | Type | Meaning / notes |", "|---|---|---|"])
        for column in frame.columns:
            dtype = str(frame[column].dtype)
            meaning = DATA_DICTIONARY.get(table_name, {}).get(column, "Synthetic field.")
            lines.append(f"| `{column}` | `{dtype}` | {meaning} |")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_validation_report(path: Path, validation: dict[str, pd.DataFrame]) -> None:
    summary = validation["summary"]
    issues = validation["issues"]
    lines = [
        "# Validation report",
        "",
        "This report lists the record-level validation checks run on the synthetic snapshot and the issues each one found.",
        "",
        "## Summary",
        "",
        "| Check | Status | Severity | Issue count |",
        "|---|---:|---|---:|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(f"| `{row.check_id}` | {row.status} | {row.severity} | {row.issue_count} |")

    lines.extend(["", "## Highest priority issues", ""])
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
            "## Assumptions and thresholds",
            "",
            f"- Unresolved query threshold: Open or Answered queries older than {QUERY_AGE_THRESHOLD_DAYS} days require review.",
            f"- Milestone delay tolerance: {MILESTONE_DELAY_TOLERANCE_DAYS} calendar days after the planned date.",
            "- Visit-window flags apply only to performed visits. Missed and pending visits are reported separately.",
            "- Lab plausibility thresholds are broad synthetic checks and do not represent protocol safety criteria.",
            "- Missing lab results are flagged only for performed visits; planned records for missed or pending visits are not treated as completed-data omissions.",
            "- Serious adverse events require complete follow-up; ongoing events remain visible until resolved.",
            "- Validation output is issue-oriented so a dashboard user can move from metric to record-level review.",
            "",
            "## ALCOA+ note",
            "",
            "The checks make each issue attributable to a table and record identifier, readable in tabular form and time-aware through explicit dates. CSV and Markdown outputs support completeness, consistency and availability for review.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_metrics_summary(path: Path, metrics: dict[str, pd.DataFrame]) -> None:
    overview = metrics["overview"].iloc[0].to_dict()
    lines = [
        "# Operational metrics summary",
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
            "The synthetic dashboard links site progress, data-cleaning workload, performed-visit adherence, adverse-event follow-up and validation flags. These are operational review signals, not clinical judgements.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_method_manifest(path: Path, seed: int, tables: dict[str, pd.DataFrame], metrics: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Build manifest",
        "",
        f"- Synthetic generation seed: `{seed}`",
        f"- Data cut date: `{DATA_CUT_DATE.date().isoformat()}`",
        "- Scenario: multicentre Phase II metabolic outcomes trial-operations scenario",
        "",
        "## Generated tables",
        "",
        "| Table | Rows |",
        "|---|---:|",
    ]
    for table_name in TABLE_NAMES:
        lines.append(f"| `{table_name}.csv` | {len(tables[table_name])} |")
    lines.extend(["", "## Metric tables", "", "| Table | Rows |", "|---|---:|"])
    for table_name, frame in metrics.items():
        lines.append(f"| `{table_name}.csv` | {len(frame)} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figures(
    metrics: dict[str, pd.DataFrame], figure_dir: Path = FIGURE_DIR
) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    site_metrics = metrics["site_metrics"].sort_values("site_id")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(site_metrics["site_id"], site_metrics["enrolled_n"], label="Enrolled", color="#2f6f73")
    ax.plot(site_metrics["site_id"], site_metrics["target_enrollment"], marker="o", color="#b45f06", label="Target")
    ax.set_title("Synthetic Enrolment Progress by Site")
    ax.set_xlabel("Site")
    ax.set_ylabel("Participants")
    ax.legend()
    fig.tight_layout()
    fig.savefig(figure_dir / "site_enrollment_progress.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(site_metrics["site_id"], site_metrics["open_query_n"], color="#7f4f24")
    ax.set_title("Open or Answered Query Burden by Site")
    ax.set_xlabel("Site")
    ax.set_ylabel("Open/answered queries")
    fig.tight_layout()
    fig.savefig(figure_dir / "site_query_burden.png", dpi=180)
    plt.close(fig)

    visit_summary = (
        metrics["visit_adherence"].groupby("visit_name", as_index=False)[["scheduled_n", "outside_window_n"]].sum()
    )
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(visit_summary["visit_name"], visit_summary["outside_window_n"], color="#8a3ffc")
    ax.set_title("Visit Window Misses by Scheduled Visit")
    ax.set_xlabel("Synthetic visits outside window")
    fig.tight_layout()
    fig.savefig(figure_dir / "visit_window_misses.png", dpi=180)
    plt.close(fig)


def write_output_tables(
    validation: dict[str, pd.DataFrame],
    metrics: dict[str, pd.DataFrame],
    output_dir: Path = OUTPUT_DIR,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    validation["issues"].to_csv(output_dir / "validation_issues.csv", index=False)
    validation["summary"].to_csv(output_dir / "validation_summary.csv", index=False)
    for name, frame in metrics.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)


def write_all_reports(
    tables: dict[str, pd.DataFrame],
    validation: dict[str, pd.DataFrame],
    metrics: dict[str, pd.DataFrame],
    seed: int,
    project_root: Path = PROJECT_ROOT,
) -> None:
    data_dir = project_root / "data"
    output_dir = project_root / "outputs"
    figure_dir = output_dir / "figures"
    data_dir.mkdir(parents=True, exist_ok=True)
    write_output_tables(validation, metrics, output_dir)
    write_data_dictionary(data_dir / "data_dictionary.md", tables)
    write_validation_report(output_dir / "validation_report.md", validation)
    write_metrics_summary(output_dir / "metrics_summary.md", metrics)
    write_method_manifest(output_dir / "build_manifest.md", seed, tables, metrics)
    write_figures(metrics, figure_dir)

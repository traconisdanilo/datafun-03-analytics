"""danilotraconis_csv_pipeline.py - CSV ETVL pipeline.

Goal:
  Average number of texts sent per day by age group (with basic stats).

ETVL:
  E = Extract (read)
  T = Transform (process)
  V = Verify (check)
  L = Load (write results to data/processed)

Reads:
  data/raw/texts_by_age.csv

Writes:
  data/processed/danilotraconis_texts_by_age_stats.txt
"""

from __future__ import annotations

import csv
from pathlib import Path
import statistics
from typing import Any, Final

from datafun_toolkit.logger import get_logger

LOG = get_logger("P03", level="INFO")

PROJECT_ROOT: Final[Path] = Path.cwd()
RAW_PATH: Final[Path] = PROJECT_ROOT / "data" / "raw" / "texts_by_age.csv"
PROCESSED_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "danilotraconis_texts_by_age_stats.txt"
)


def extract_rows(*, file_path: Path) -> list[dict[str, str]]:
    """E: Read CSV rows into memory."""
    LOG.info("EXTRACT: reading %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    with file_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row.")

        required = {"age_group", "texts_per_day"}
        missing = required - set(reader.fieldnames)
        if missing:
            raise KeyError(f"CSV missing required columns: {sorted(missing)}")

        return list(reader)


def transform_to_grouped_stats(
    *, rows: list[dict[str, str]]
) -> dict[str, dict[str, float]]:
    """T: Group numeric values by age_group and compute stats for each group."""
    LOG.info("TRANSFORM: rows=%s", len(rows))

    grouped: dict[str, list[float]] = {}

    for row in rows:
        age_group = (row.get("age_group") or "").strip()
        raw_val = (row.get("texts_per_day") or "").strip()

        if not age_group or not raw_val:
            continue

        try:
            val = float(raw_val)
        except ValueError:
            continue

        grouped.setdefault(age_group, []).append(val)

    stats_by_group: dict[str, dict[str, float]] = {}

    for group, values in grouped.items():
        if not values:
            continue

        stats_by_group[group] = {
            "count": float(len(values)),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        }

    return stats_by_group


def verify_grouped_stats(*, stats_by_group: dict[str, dict[str, float]]) -> None:
    """V: Sanity-check grouped stats."""
    if not stats_by_group:
        raise ValueError("No valid numeric data found to analyze.")

    required_keys = {"count", "min", "max", "mean", "stdev"}

    for group, stats in stats_by_group.items():
        missing = required_keys - set(stats.keys())
        if missing:
            raise KeyError(f"{group}: missing stats keys: {sorted(missing)}")

        if stats["count"] <= 0:
            raise ValueError(f"{group}: count must be positive.")

        if stats["min"] > stats["max"]:
            raise ValueError(f"{group}: min cannot be greater than max.")


def load_report(*, out_path: Path, stats_by_group: dict[str, dict[str, float]]) -> None:
    """L: Write grouped stats report to a text file."""
    LOG.info("LOAD: writing %s", out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("Texts Sent Per Day Statistics (by Age Group)\n")
    lines.append("------------------------------------------------\n\n")

    for group in sorted(stats_by_group.keys()):
        s = stats_by_group[group]
        lines.append(f"Age Group: {group}\n")
        lines.append(f"Count: {int(s['count'])}\n")
        lines.append(f"Minimum: {s['min']:.2f}\n")
        lines.append(f"Maximum: {s['max']:.2f}\n")
        lines.append(f"Mean: {s['mean']:.2f}\n")
        lines.append(f"Standard Deviation: {s['stdev']:.2f}\n")
        lines.append("\n")

    out_path.write_text("".join(lines), encoding="utf-8")


def run_pipeline(
    *,
    raw_path: Path = RAW_PATH,
    processed_path: Path = PROCESSED_PATH,
    logger: Any = LOG,
) -> None:
    """Run the full ETVL pipeline."""
    logger.info("CSV (texts_by_age): START")

    # E
    rows = extract_rows(file_path=raw_path)

    # T
    stats_by_group = transform_to_grouped_stats(rows=rows)

    # V
    verify_grouped_stats(stats_by_group=stats_by_group)

    # L
    load_report(out_path=processed_path, stats_by_group=stats_by_group)

    logger.info("CSV (texts_by_age): wrote %s", processed_path)
    logger.info("CSV (texts_by_age): END")

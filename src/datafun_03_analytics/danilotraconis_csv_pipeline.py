"""danilotraconis_csv_pipeline.py - CSV ETL pipeline.

Reads a raw CSV file from data/raw, transforms it, and writes results to data/processed.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Final

from datafun_toolkit.logger import get_logger

LOG = get_logger("P03", level="INFO")

PROJECT_ROOT: Final[Path] = Path.cwd()
RAW_PATH: Final[Path] = PROJECT_ROOT / "data" / "raw" / "danilo_holidays.csv"
PROCESSED_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "danilotraconis_holiday_summary.txt"
)


def extract(*, path: Path) -> list[dict[str, str]]:
    """Extract: read CSV rows into memory."""
    LOG.info(f"EXTRACT: reading {path}")
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def transform(*, rows: list[dict[str, str]]) -> dict[str, int]:
    """Transform: count holidays by type."""
    LOG.info(f"TRANSFORM: rows={len(rows)}")
    counts: dict[str, int] = {}
    for row in rows:
        holiday_type = row.get("type", "unknown").strip().lower()
        counts[holiday_type] = counts.get(holiday_type, 0) + 1
    return counts


def load(*, path: Path, summary: dict[str, int]) -> None:
    """Load: write a simple text report to data/processed."""
    LOG.info(f"LOAD: writing {path}")
    lines = ["Holiday counts by type:\n"]
    for k in sorted(summary):
        lines.append(f"- {k}: {summary[k]}\n")
    path.write_text("".join(lines), encoding="utf-8")


def run_pipeline() -> None:
    """Run the full pipeline: Extract -> Transform -> Load."""
    rows = extract(path=RAW_PATH)
    summary = transform(rows=rows)
    load(path=PROCESSED_PATH, summary=summary)
    LOG.info("PIPELINE DONE")

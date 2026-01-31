"""danilotraconis_happiness_csv_pipeline.py - CSV ETVL pipeline.

ETVL:
  E = Extract (read)
  T = Transform (process)
  V = Verify (check)
  L = Load (write results to data/processed)

Dataset:
  2020 World Happiness Report

Metric:
  Ladder score
"""

import csv
from pathlib import Path
import statistics
from typing import Any


# =========================
# E — EXTRACT
# =========================
def extract_ladder_scores(*, file_path: Path) -> list[float]:
    """Read CSV and extract Ladder score values as floats."""
    if not file_path.exists():
        raise FileNotFoundError(f"Missing input file: {file_path}")

    scores: list[float] = []

    with file_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None or "Ladder score" not in reader.fieldnames:
            raise KeyError("CSV missing required column: Ladder score")

        for row in reader:
            raw_value = (row.get("Ladder score") or "").strip()
            if not raw_value:
                continue
            try:
                scores.append(float(raw_value))
            except ValueError:
                continue

    return scores


# =========================
# T — TRANSFORM
# =========================
def transform_scores_to_stats(*, scores: list[float]) -> dict[str, float]:
    """Calculate descriptive statistics."""
    if not scores:
        raise ValueError("No numeric values found.")

    return {
        "count": float(len(scores)),
        "min": min(scores),
        "max": max(scores),
        "mean": statistics.mean(scores),
        "stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
    }


# =========================
# V — VERIFY
# =========================
def verify_stats(*, stats: dict[str, float]) -> None:
    """Sanity-check stats dictionary."""
    required = {"count", "min", "max", "mean", "stdev"}
    missing = required - set(stats.keys())

    if missing:
        raise KeyError(f"Missing stats keys: {missing}")

    if stats["count"] <= 0:
        raise ValueError("Count must be positive.")

    if stats["min"] > stats["max"]:
        raise ValueError("Min cannot exceed max.")


# =========================
# L — LOAD
# =========================
def load_stats_report(*, stats: dict[str, float], out_path: Path) -> None:
    """Write statistics report to text file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        f.write("CSV Ladder Score Statistics (2020 World Happiness Report)\n")
        f.write("---------------------------------------------------------\n")
        f.write(f"Count: {int(stats['count'])}\n")
        f.write(f"Minimum: {stats['min']:.2f}\n")
        f.write(f"Maximum: {stats['max']:.2f}\n")
        f.write(f"Mean: {stats['mean']:.2f}\n")
        f.write(f"Standard Deviation: {stats['stdev']:.2f}\n")


# =========================
# PIPELINE RUNNER
# =========================
def run_happiness_pipeline(*, raw_dir: Path, processed_dir: Path, logger: Any) -> None:
    """Run the full happiness CSV ETVL pipeline."""
    logger.info("CSV (happiness): START")

    input_file = raw_dir / "2020_happiness.csv"
    output_file = processed_dir / "danilotraconis_happiness_ladder_stats.txt"

    scores = extract_ladder_scores(file_path=input_file)
    stats = transform_scores_to_stats(scores=scores)
    verify_stats(stats=stats)
    load_stats_report(stats=stats, out_path=output_file)

    logger.info("CSV (happiness): wrote %s", output_file)
    logger.info("CSV (happiness): END")

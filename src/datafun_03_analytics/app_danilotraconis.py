"""app_danilotraconis.py - Project script.

# Data source chosen: CSV

Author: Danilo Traconis
Date: 2026-01

Practice key Python skills:
- pathlib for cross-platform paths
- logging (preferred over print)
- calling functions from modules
- clear ETL pipeline stages:
  E = Extract (read, get data from source into memory)
  T = Transform (process, change data in memory)
  L = Load (write results, to data/processed or other destination)

OBS:
  This is your file to practice and customize.
"""

# === DECLARE IMPORTS (BRING IN FREE CODE) ===

import logging
from pathlib import Path
from typing import Final

from datafun_toolkit.logger import get_logger, log_header

# === IMPORT LOCAL MODULE FUNCTIONS ===
# REQ: imports from other modules in this project must use full package path
from datafun_03_analytics.danilotraconis_csv_pipeline import run_pipeline
from datafun_03_analytics.danilotraconis_happiness_csv_pipeline import (
    run_happiness_pipeline,
)

# === CONFIGURE LOGGER ONCE PER MODULE ===

LOG: logging.Logger = get_logger("P03", level="DEBUG")

# === DECLARE GLOBAL VARIABLES ===

ROOT_DIR: Final[Path] = Path.cwd()
DATA_DIR: Final[Path] = ROOT_DIR / "data"
RAW_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"


def main() -> None:
    """Entry point: run CSV ETVL pipelines."""
    log_header(LOG, "Pipelines: Read, Process, Verify, Write (ETVL)")
    LOG.info("START main()")

    # CSV pipeline: texts by age
    run_pipeline()

    # CSV pipeline: 2020 happiness ladder scores
    run_happiness_pipeline(
        raw_dir=RAW_DIR,
        processed_dir=PROCESSED_DIR,
        logger=LOG,
    )

    LOG.info("END main()")


if __name__ == "__main__":
    main()

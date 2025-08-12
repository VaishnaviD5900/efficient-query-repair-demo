# app/core/config.py
import os
from pathlib import Path

# ABSOLUTE path to the external "query repair" project folder that contains main.py
# Example from your logs:
# C:/Query-Repair-System/Query-Repair-for-Aggregate-Constraints/pp
REPAIR_PROJECT_DIR = Path(
    os.getenv(
        "REPAIR_PROJECT_DIR",
        r"C:/Query-Repair-System/Query-Repair-for-Aggregate-Constraints/pp",
    )
)

# Where that project writes its outputs (you already set this in main.py)
OUTPUT_DIR = Path(
    os.getenv("REPAIR_OUTPUT_DIR", r"C:/Query-Repair-System/Exp")
)

# If you ever need to change defaults, just override via env vars above.

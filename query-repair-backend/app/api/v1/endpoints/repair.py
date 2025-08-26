# app/api/v1/endpoints/repair.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pathlib import Path
import sys
import traceback
import pandas as pd

from app.models.schemas import RepairRequest, RepairResult

router = APIRouter()

# ---- configure where the external query-repair project lives ----
# folder that contains that project's main.py
QR_PROJECT_DIR = Path(__file__).resolve().parents[5] / "query-repair-module" / "pp"

# add to import path once
if str(QR_PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(QR_PROJECT_DIR))

try:
    # import the external main.py (it should expose a function `main(...)`)
    import main as qr_main  # type: ignore
except Exception as e:
    # if this import fails at startup, the endpoint will 500 with a clearer message
    print("Failed to import external query-repair main.py:", e)
    qr_main = None  # sentinel so we can error nicely later


def _read_results_from_output_dir(output_dir: Path, max_csv_preview_rows: int = 5) -> Dict[str, Any]:
    """
    Very simple reader that lists files in the output directory and returns a tiny
    preview for CSVs.
    """
    if not output_dir.exists():
        return {"files": [], "previews": {}, "note": f"Output dir does not exist: {output_dir}"}

    # collect files (non-recursive for now; make it rglob if you nest)
    files = sorted(output_dir.glob("*"))
    file_list = [str(p) for p in files if p.is_file()]

    previews: Dict[str, List[Dict[str, Any]]] = {}
    for p in files:
        if p.is_file() and p.suffix.lower() == ".csv":
            try:
                df = pd.read_csv(p)
                previews[str(p)] = df.head(max_csv_preview_rows).to_dict(orient="records")
            except Exception as e:
                previews[str(p)] = [{"error": f"Failed to read CSV preview: {e}"}]

    return {"files": file_list, "previews": previews}


@router.post("/run", response_model=RepairResult)
def run_repair(req: RepairRequest) -> RepairResult:
    """
    Synchronously run the external query-repair `main()` with the given payload,
    then read the output directory and return a lightweight summary.
    """
    if qr_main is None:
        raise HTTPException(status_code=500, detail="Query-repair module not importable. Check QR_PROJECT_DIR.")

    # where to look for results;
    # use payload if provided, else default to the constant used in your main.py
    output_dir = Path(req.output_dir or (Path(__file__).resolve().parents[5] / "query-repair-backend" / "output"))

    try:
        # Call external main(). Your patched main signature:
        #   main(dataName: str, Top_k: int, predicates: list[dict], constraint_def: dict)
        qr_main.main(
            dataName=req.dataName,
            Top_k=req.Top_k,
            predicates=[p.model_dump() for p in req.predicates],
            constraint_def=req.constraint_def.model_dump(),
        )
    except Exception as e:
        print("Query-repair run failed:\n", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"query-repair execution error: {e}")

    # After it finishes, read results
    results = _read_results_from_output_dir(output_dir)

    # Build a simple response (for now we just echo files and tiny CSV previews)
    return RepairResult(
        ok=True,
        message="Repair run completed.",
        files=results["files"],
        previews=results["previews"],
        output_dir=str(output_dir),
    )

# app/api/v1/endpoints/repair.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from typing import Dict, Any, List
from pathlib import Path
import os
import traceback
import threading
import uuid
import pandas as pd

from query_repair_module.pp import main as qr_main
from app.models.schemas import (
    RepairRequest,
    RepairResult,
    JobAccepted,
    JobStatus,
)

router = APIRouter()

# ---- config ----
DEFAULT_OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output")).resolve()

# ---- simple in-memory job store (OK for single instance) ----
JOBS: Dict[str, Dict[str, Any]] = {}
LOCK = threading.Lock()


def _read_results_from_output_dir(output_dir: Path, max_csv_preview_rows: int = 5) -> Dict[str, Any]:
    """
    Very simple reader that lists files in the output directory and returns a tiny
    preview for CSVs.
    """
    if not output_dir.exists():
        return {"files": [], "previews": {}, "note": f"Output dir does not exist: {output_dir}"}

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


def _run_job(job_id: str, req: RepairRequest, output_dir: Path) -> None:
    """Background worker that runs the heavy query-repair and stores results."""
    try:
        qr_main(
            dataName=req.dataName,
            Top_k=req.Top_k,
            predicates=[p.model_dump() for p in req.predicates],
            constraint_def=req.constraint_def.model_dump(),
        )
        results = _read_results_from_output_dir(output_dir)
        result_obj = RepairResult(
            ok=True,
            message="Repair run completed.",
            files=results["files"],
            previews=results["previews"],
            output_dir=str(output_dir),
        )
        with LOCK:
            JOBS[job_id]["status"] = "done"
            JOBS[job_id]["result"] = result_obj
    except Exception as e:
        print("Query-repair run failed:\n", traceback.format_exc())
        with LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = f"{e}"


@router.post("/run", status_code=status.HTTP_202_ACCEPTED, response_model=JobAccepted)
def run_repair(req: RepairRequest, background_tasks: BackgroundTasks) -> JobAccepted:
    """
    Kick off the repair job and return immediately (avoid Azure 504 on long runs).
    Poll /api/v1/repair/status/{job_id} for completion.
    """
    if qr_main is None:
        raise HTTPException(status_code=500, detail="Query-repair module not importable.")

    output_dir = Path(getattr(req, "output_dir", "") or DEFAULT_OUTPUT_DIR).resolve()
    os.makedirs(output_dir, exist_ok=True)

    job_id = str(uuid.uuid4())
    with LOCK:
        JOBS[job_id] = {"status": "running", "output_dir": str(output_dir)}

    background_tasks.add_task(_run_job, job_id, req, output_dir)

    return JobAccepted(
        job_id=job_id,
        status_url=f"/api/v1/repair/status/{job_id}",
        message="Accepted",
    )


@router.get("/status/{job_id}", response_model=JobStatus)
def get_status(job_id: str) -> JobStatus:
    """Return the state of a previously accepted job."""
    with LOCK:
        info = JOBS.get(job_id)
        if not info:
            return JobStatus(job_id=job_id, status="unknown")
        if info["status"] == "done":
            return JobStatus(job_id=job_id, status="done", result=info["result"])
        if info["status"] == "error":
            return JobStatus(job_id=job_id, status="error", error=info.get("error"))
        return JobStatus(job_id=job_id, status="running")

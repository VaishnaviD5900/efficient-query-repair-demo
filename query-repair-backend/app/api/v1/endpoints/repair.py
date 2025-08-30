# app/api/v1/endpoints/repair.py
from __future__ import annotations

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import traceback
import threading
import uuid
import json
import pandas as pd
from datetime import datetime

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

# A small, shared, persistent job store on Azure App Service.
# /home is a persistent volume and available to all workers on the app.
JOB_STORE_DIR = Path(os.getenv("JOB_STORE_DIR", "/home/query-repair-jobs")).resolve()
os.makedirs(JOB_STORE_DIR, exist_ok=True)

# ---- helpers for JSON job store ----
def _job_path(job_id: str) -> Path:
    return JOB_STORE_DIR / f"{job_id}.json"

def _write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), default=str)
    os.replace(tmp, path)  # atomic on same volume

def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _save_job(job_id: str, status: str, *, result: Dict[str, Any] | None = None, error: str | None = None, output_dir: str | None = None) -> None:
    payload: Dict[str, Any] = {
        "job_id": job_id,
        "status": status,  # "running" | "done" | "error"
        "output_dir": output_dir,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    if result is not None:
        payload["result"] = result
    if error is not None:
        payload["error"] = error
    _write_json_atomic(_job_path(job_id), payload)

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
            files=results.get("files"),
            previews=results.get("previews"),
            output_dir=str(output_dir),
        )
        # Persist final status to shared store
        _save_job(
            job_id,
            "done",
            result=result_obj.model_dump(mode="json"),
            output_dir=str(output_dir),
        )
    except Exception:
        err_text = traceback.format_exc()
        print("Query-repair run failed:\n", err_text)
        _save_job(job_id, "error", error=err_text, output_dir=str(output_dir))

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

    # Persist "running" to shared store so any worker can serve /status
    _save_job(job_id, "running", output_dir=str(output_dir))

    # Offload the heavy work to a background thread
    background_tasks.add_task(_run_job, job_id, req, output_dir)

    return JobAccepted(
        job_id=job_id,
        status_url=f"/api/v1/repair/status/{job_id}",
        message="Accepted",
    )

@router.get("/status/{job_id}", response_model=JobStatus)
def get_status(job_id: str) -> JobStatus:
    """Return the state of a previously accepted job. Uses shared JSON store."""
    info = _load_json(_job_path(job_id))
    if not info:
        return JobStatus(job_id=job_id, status="unknown")

    status_val = info.get("status", "unknown")

    if status_val == "done":
        # Rehydrate RepairResult from stored JSON
        result_dict = info.get("result") or {}
        try:
            result_obj = RepairResult(**result_dict)
        except Exception:
            # If schema changed, surface raw error but still mark as error
            return JobStatus(job_id=job_id, status="error", error="Failed to parse stored result")
        return JobStatus(job_id=job_id, status="done", result=result_obj)

    if status_val == "error":
        return JobStatus(job_id=job_id, status="error", error=info.get("error"))

    # default: running
    return JobStatus(job_id=job_id, status="running")

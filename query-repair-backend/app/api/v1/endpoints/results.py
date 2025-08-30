# app/api/v1/endpoints/results.py
from __future__ import annotations
import os
import re

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from typing import List, Optional
import pandas as pd

from app.models.schemas import ParsedResults, RunInfo, SatisfiedRow

router = APIRouter()

# ---------- helpers ----------
def _first(paths: List[Path]) -> Optional[Path]:
    return sorted(paths)[0] if paths else None

def _read_csv(p: Optional[Path]) -> pd.DataFrame:
    if p and p.exists():
        try:
            return pd.read_csv(p, engine="python", keep_default_na=False)
        except Exception:
            pass
    return pd.DataFrame()

def _to_int(v):
    try:
        if v in ("", None, "None"): return None
        return int(float(v))
    except Exception:
        return None

def _to_float(v):
    try:
        if v in ("", None, "None"): return None
        return float(v)
    except Exception:
        return None

def _parse_run_info(df: pd.DataFrame) -> RunInfo:
    """
    Parse your single-row wide CSV with headers:

    Data Name, Data Size, Query Num, Constraint Num, Type, Top-K,
    Combinations Num, Distance, Access Num, Checked Num, Refinement Num, Time,
    Constraint Width, Solutions Count, Constraint, Query,
    Range Evaluation Time, Division Time, Single Time, Processing Time
    """
    if df.empty:
        return RunInfo()

    # trim header whitespace just in case
    df = df.rename(columns=lambda c: str(c).strip())
    row = df.iloc[0]

    return RunInfo(
        dataset            = row.get("Data Name"),
        size               = _to_int(row.get("Data Size")),
        query_num          = _to_int(row.get("Query Num")),
        constraint_num     = _to_int(row.get("Constraint Num")),
        run_type           = row.get("Type"),
        top_k              = _to_int(row.get("Top-K")),
        combinations       = _to_int(row.get("Combinations Num")),
        distance           = _to_float(row.get("Distance")),
        access_num         = _to_int(row.get("Access Num")),
        checked_num        = _to_int(row.get("Checked Num")),
        refinement_num     = _to_int(row.get("Refinement Num")),
        time_sec           = _to_float(row.get("Time")),
        constraint_width   = _to_float(row.get("Constraint Width")),
        solutions_count    = _to_int(row.get("Solutions Count")),
        constraint_text    = row.get("Constraint"),
        query_text         = row.get("Query"),
        range_eval_time    = _to_float(row.get("Range Evaluation Time")),
        division_time      = _to_float(row.get("Division Time")),
        single_time        = _to_float(row.get("Single Time")),
        processing_time    = _to_float(row.get("Processing Time")),
    )

def _escape_dataset(ds: str) -> str:
    return re.escape(ds.strip())

def _match(files: List[Path], pattern: str) -> Optional[Path]:
    regex = re.compile(pattern, flags=re.IGNORECASE)
    for p in sorted(files):
        if p.suffix.lower() == ".csv" and regex.search(p.stem):
            return p
    return None

# ---------- endpoint ----------
@router.get("", response_model=ParsedResults)
def get_results(
    dataset: str = Query(..., description="Dataset name to fetch results for")
) -> ParsedResults:
    """
    Read artifacts from an output dir and return structured JSON for the Results page.
    """
    DEFAULT_OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output")).resolve() 
    odir = DEFAULT_OUTPUT_DIR
    if not odir.exists():
        raise HTTPException(status_code=404, detail=f"Output dir not found: {output_dir}")

    # search recursively (in case future runs write subfolders)
    files = [p for p in odir.rglob("*") if p.is_file()]
    if not files:
        raise HTTPException(status_code=404, detail=f"No files found in: {output_dir}")

    ds = _escape_dataset(dataset)

    run_info_pattern = rf"run[_-]?info.*{ds}|{ds}.*run[_-]?info"
    ff_pattern       = rf"satisfied[_-]?conditions[_-]?fully.*{ds}|{ds}.*satisfied[_-]?conditions[_-]?fully"
    rp_pattern       = rf"satisfied[_-]?conditions[_-]?ranges.*{ds}|{ds}.*satisfied[_-]?conditions[_-]?ranges"

    run_info_path = _match(files, run_info_pattern)
    ff_path       = _match(files, ff_pattern)
    rp_path       = _match(files, rp_pattern)

    run_info_df = _read_csv(run_info_path)
    ff_df       = _read_csv(ff_path)
    rp_df       = _read_csv(rp_path)

    run_info_rows = run_info_df.rename(columns=lambda c: str(c).strip()).to_dict(orient="records") if not run_info_df.empty else []


    return ParsedResults(
        output_dir=str(odir),
        run_info = run_info_rows,
        satisfied_conditions_ff=[SatisfiedRow(row=r) for r in ff_df.to_dict(orient="records")] if not ff_df.empty else [],
        satisfied_conditions_rp=[SatisfiedRow(row=r) for r in rp_df.to_dict(orient="records")] if not rp_df.empty else [],
        raw_files=[str(p) for p in files],
    )

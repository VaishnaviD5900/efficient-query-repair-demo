# app/api/v1/endpoints/results.py
from __future__ import annotations
import os
import re

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from typing import List, Optional, Tuple
import pandas as pd

from app.models.schemas import ParsedResults, RunInfo, SatisfiedRow

router = APIRouter()

# ---------- helpers ----------
def _read_original_check(files: List[Path], dataset: str) -> Tuple[Optional[str], Optional[bool]]:
    # tolerate underscores / hyphens and both orders
    pattern = rf"original[_-]?query.*{_escape_dataset(dataset)}|{_escape_dataset(dataset)}.*original[_-]?query"
    p = _match(files, pattern)
    if not p:
        return (None, None)

    df = _read_csv(p)
    if df.empty:
        return (None, None)

    df = _clean_df(df)

    # case-insensitive column lookup
    cols = {str(c).strip().lower(): c for c in df.columns}
    metric_col = cols.get("original metric")
    pass_col   = cols.get("original pass")
    if not metric_col or not pass_col:
        return (None, None)

    last = df.tail(1).iloc[0]
    metric_val = last.get(metric_col)
    pass_val = last.get(pass_col)

    # stringify metric exactly as stored
    metric_str = None if metric_val is None else str(metric_val)
    return (metric_str, (pass_val))

def _first(paths: List[Path]) -> Optional[Path]:
    return sorted(paths)[0] if paths else None

def _read_csv(p: Optional[Path]) -> pd.DataFrame:
    if p and p.exists():
        try:
            # let pandas parse NA normally; we'll normalize blanks below
            return pd.read_csv(p, engine="python")
        except Exception:
            pass
    return pd.DataFrame()

def _normalize_cell(v):
    """Convert whitespacey/placeholder strings to None; otherwise return trimmed strings or original value."""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s in ("", "None", "nan", "NaN", "N/A", "-"):
            return None
        return s  # keep as string; Pydantic will coerce where needed
    return v

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.rename(columns=lambda c: str(c).strip())
    # normalize every cell
    return df.applymap(_normalize_cell)

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
        raise HTTPException(status_code=404, detail=f"Output dir not found: {odir}")

    # search recursively (in case future runs write subfolders)
    files = [p for p in odir.rglob("*") if p.is_file()]
    if not files:
        raise HTTPException(status_code=404, detail=f"No files found in: {odir}")

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

    # --- Clean and coerce run_info into typed models ---
    if not run_info_df.empty:
        run_info_df = _clean_df(run_info_df)
        run_info_records = run_info_df.to_dict(orient="records")
        run_info_rows: List[RunInfo] = [RunInfo(**rec) for rec in run_info_records]
    else:
        run_info_rows = []

    # satisfied_* tables are passed through as-is (free-form rows)
    ff_rows = ff_df.to_dict(orient="records") if not ff_df.empty else []
    rp_rows = rp_df.to_dict(orient="records") if not rp_df.empty else []

    orig_metric, orig_pass = _read_original_check(files, dataset)

    return ParsedResults(
    output_dir=str(odir),
    run_info=run_info_rows,
    satisfied_conditions_ff=[SatisfiedRow(row=r) for r in ff_rows],
    satisfied_conditions_rp=[SatisfiedRow(row=r) for r in rp_rows],
    raw_files=[str(p) for p in files],
    original_metric=orig_metric,
    original_pass=orig_pass,
    )


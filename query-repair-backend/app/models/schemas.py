# app/models/schemas.py
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class Predicate(BaseModel):
    field: str
    op: str
    value: Any


class ConstraintDef(BaseModel):
    columns: List[str] = Field(..., description="Columns used by constraints/aggregations")
    aggregations: Dict[str, str] = Field(..., description='e.g. {"agg1": "sum(\\"Revenue\\")"}')
    expression: List[str] | str = Field(..., description='e.g. ["0.1 <= (agg1 / agg2) <= 0.2"]')
    const_num: Optional[int] = 0


class RepairRequest(BaseModel):
    dataName: str = Field(..., pattern="^(TPCH|ACSIncome|Healthcare)$")
    Top_k: int = 7
    predicates: List[Predicate]
    constraint_def: ConstraintDef
    output_dir: Optional[str] = None   # <- change


class RepairResult(BaseModel):
    ok: bool = True
    message: str = "Repair run completed."
    output_dir: Optional[str] = None
    files: Optional[List[str]] = None
    previews: Optional[Dict[str, List[Dict[str, Any]]]] = None


# ---------- parsed artifacts for Results page ----------

class RunInfo(BaseModel):
    # allow using either the field name (dataset) or the alias ("Data Name")

    dataset: Optional[str] = Field(None, alias="Data Name")
    size: Optional[int] = Field(None, alias="Data Size")
    query_num: Optional[int] = Field(None, alias="Query Num")
    constraint_num: Optional[int] = Field(None, alias="Constraint Num")
    run_type: Optional[str] = Field(None, alias="Type")
    top_k: Optional[int] = Field(None, alias="Top-K")
    combinations: Optional[int] = Field(None, alias="Combinations Num")
    distance: Optional[float] = Field(None, alias="Distance")
    access_num: Optional[int] = Field(None, alias="Access Num")
    checked_num: Optional[int] = Field(None, alias="Checked Num")
    refinement_num: Optional[int] = Field(None, alias="Refinement Num")
    time_sec: Optional[float] = Field(None, alias="Time")
    constraint_width: Optional[float] = Field(None, alias="Constraint Width")
    solutions_count: Optional[int] = Field(None, alias="Solutions Count")
    constraint_text: Optional[str] = Field(None, alias="Constraint")
    query_text: Optional[str] = Field(None, alias="Query")
    range_eval_time: Optional[float] = Field(None, alias="Range Evaluation Time")
    division_time: Optional[float] = Field(None, alias="Division Time")
    single_time: Optional[float] = Field(None, alias="Single Time")
    processing_time: Optional[float] = Field(None, alias="Processing Time")


class SatisfiedRow(BaseModel):
    row: Dict[str, Any]


class ParsedResults(BaseModel):
    output_dir: str
    run_info: List[RunInfo] = Field(default_factory=list)
    satisfied_conditions_ff: List[SatisfiedRow] = Field(default_factory=list)
    satisfied_conditions_rp: List[SatisfiedRow] = Field(default_factory=list)
    raw_files: List[str] = Field(default_factory=list)

class JobAccepted(BaseModel):
    job_id: str
    status_url: str
    message: str = "Accepted"

# Polled by GET /repair/status/{job_id}
class JobStatus(BaseModel):
    job_id: str
    status: Literal["running", "done", "error", "unknown"]
    result: Optional["RepairResult"] = None  # forward-ref to your existing model
    error: Optional[str] = None
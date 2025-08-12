# app/models/schemas.py
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Predicate(BaseModel):
    field: str
    op: str
    value: Any


class ConstraintDef(BaseModel):
    columns: List[str] = Field(..., description="Columns used by constraints/aggregations")
    aggregations: Dict[str, str] = Field(..., description='e.g. {"agg1": "sum(\\"Revenue\\")"}')
    expression: List[str] = Field(..., description='e.g. ["0.1 <= (agg1 / agg2) <= 0.2"]')
    const_num: Optional[int] = 0


class RepairRequest(BaseModel):
    dataName: str = Field(..., pattern="^(TPCH|ACSIncome|Healthcare)$")
    Top_k: int = 7
    predicates: List[Predicate]
    constraint_def: ConstraintDef
    output_dir: str


class RepairResult(BaseModel):
    status: str = "ok"
    output_dir: Optional[str] = None
    files: Optional[List[str]] = None
    note: Optional[str] = None

"""
Pydantic Schemas for Dashboard API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class AnalysisRunBase(BaseModel):
    config: Optional[dict[str, Any]] = None
    metrics_summary: Optional[dict[str, Any]] = None


class AnalysisRunCreate(AnalysisRunBase):
    pass


class AnalysisRun(AnalysisRunBase):
    id: str
    timestamp: datetime
    status: Optional[str] = "pending"
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class ResultItemBase(BaseModel):
    query: str
    response: str
    retrieved_contexts: list[str]
    ground_truth_contexts: Optional[list[str]] = None
    metrics: dict[str, float]


class ResultItemCreate(ResultItemBase):
    pass


class ResultItem(ResultItemBase):
    id: int
    run_id: str

    model_config = {"from_attributes": True}


class AnalyzeRequest(BaseModel):
    data: list[dict[str, Any]]
    config: Optional[dict[str, Any]] = None

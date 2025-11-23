"""
Pydantic Schemas for Dashboard API.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class AnalysisRunBase(BaseModel):
    config: Optional[Dict[str, Any]] = None
    metrics_summary: Optional[Dict[str, Any]] = None

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
    retrieved_contexts: List[str]
    ground_truth_contexts: Optional[List[str]] = None
    metrics: Dict[str, float]

class ResultItemCreate(ResultItemBase):
    pass

class ResultItem(ResultItemBase):
    id: int
    run_id: str

    model_config = {"from_attributes": True}

class AnalyzeRequest(BaseModel):
    data: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None

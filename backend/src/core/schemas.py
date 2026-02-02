from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl
from src.core.models import JobStatus

class JobBase(BaseModel):
    url: HttpUrl
    collection_index: int = 0
    max_items: int = 1000

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result_count: int
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class JobResult(JobResponse):
    result_json: Optional[Dict[str, Any]] = None

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, Text
from src.core.database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration used
    collection_index = Column(Integer, default=0)
    max_items = Column(Integer, default=1000)
    
    # Results
    result_count = Column(Integer, default=0)
    result_json = Column(JSON, nullable=True)  # For smaller results
    storage_path = Column(String, nullable=True)  # Path to file if too large
    error_message = Column(Text, nullable=True)


"""
SQLAlchemy Models for RAGLint Dashboard.
"""

import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    runs = relationship("AnalysisRun", back_populates="user")
    versions = relationship("PipelineVersion", back_populates="user")
    datasets = relationship("Dataset", back_populates="user")


class PipelineVersion(Base):
    __tablename__ = "pipeline_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hash = Column(String, index=True, unique=True)  # SHA256 of config
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String, nullable=True)

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="versions")

    runs = relationship("AnalysisRun", back_populates="version")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    config = Column(JSON, nullable=True)  # Snapshot of config at run time (redundant but safe)
    metrics_summary = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    version_id = Column(String, ForeignKey("pipeline_versions.id"), nullable=True)
    version = relationship("PipelineVersion", back_populates="runs")

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="runs")

    items = relationship("ResultItem", back_populates="run", cascade="all, delete-orphan")


class ResultItem(Base):
    __tablename__ = "result_items"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("analysis_runs.id"))

    query = Column(Text)
    response = Column(Text)
    retrieved_contexts = Column(JSON)
    ground_truth_contexts = Column(JSON, nullable=True)

    # Individual metrics for this item
    metrics = Column(JSON)

    run = relationship("AnalysisRun", back_populates="items")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="datasets")

    items = relationship("DatasetItem", back_populates="dataset", cascade="all, delete-orphan")


class DatasetItem(Base):
    __tablename__ = "dataset_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, ForeignKey("datasets.id"))

    data = Column(JSON)  # Stores the row data (query, ground_truth, etc.)

    dataset = relationship("Dataset", back_populates="items")

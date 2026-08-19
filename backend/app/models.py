from sqlalchemy import Column, Integer, String, Numeric, JSON, DateTime, func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector

from .config import settings

Base = declarative_base()


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True)
    environment = Column(String, unique=True, nullable=False)
    area_min = Column(Numeric)
    height_min = Column(Numeric)
    doors = Column(Integer)
    extra = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    properties = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class RevitLevel(Base):
    __tablename__ = "revit_levels"

    id = Column(Integer, primary_key=True)
    project_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    elevation = Column(Numeric, nullable=False)
    synced_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(settings.embedding_dim))
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    stages = relationship("PipelineStage", back_populates="pipeline", cascade="all, delete-orphan", order_by="PipelineStage.order")


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, default=0)

    pipeline = relationship("Pipeline", back_populates="stages")
    leads = relationship("Lead", back_populates="pipeline_stage")

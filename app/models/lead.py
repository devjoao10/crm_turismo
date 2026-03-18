from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base


lead_destinations = Table(
    "lead_destinations",
    Base.metadata,
    Column("lead_id", Integer, ForeignKey("leads.id"), primary_key=True),
    Column("destination_id", Integer, ForeignKey("destinations.id"), primary_key=True),
)


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    whatsapp = Column(String, nullable=False)
    status = Column(String, nullable=False, default="novo")
    travel_start_date = Column(Date, nullable=False)
    travel_end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    pipeline_stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=True)

    destinations = relationship(
        "Destination",
        secondary=lead_destinations,
        back_populates="leads"
    )

    pipeline_stage = relationship("PipelineStage", back_populates="leads")
# app/models/destination.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    leads = relationship(
        "Lead",
        secondary="lead_destinations",
        back_populates="destinations"
    )
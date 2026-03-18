# app/db/init_db.py
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.lead import Lead
from app.models.destination import Destination
from app.models.pipeline import Pipeline, PipelineStage
from app.utils.security import hash_password


def create_default_user():
    db: Session = SessionLocal()

    existing_user = db.query(User).filter(User.email == "admin@crm.com").first()

    if not existing_user:
        default_user = User(
            name="Administrador",
            email="admin@crm.com",
            password=hash_password("123456"),
            is_active=True
        )
        db.add(default_user)
        db.commit()

    db.close()


def create_default_destinations():
    db: Session = SessionLocal()

    default_destinations = ["ATACAMA", "SANTIAGO", "UYUNI"]

    for destination_name in default_destinations:
        existing_destination = (
            db.query(Destination)
            .filter(Destination.name == destination_name)
            .first()
        )

        if not existing_destination:
            db.add(Destination(name=destination_name))

    db.commit()
    db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    create_default_user()
    create_default_destinations()
from app.db.database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from app.models.user import User

def create_default_user():
        db: Session = SessionLocal()

        existing_user = db.query(User).filter(User.email == "admin@crm.com").first()

        if not existing_user:
                default_user = User(
                    name="Administrador",
                    email="admin@crm.com",
                    password="123456",
                    is_active=True
                )
                db.add(default_user)
                db.commit()

        db.close()


def init_db():
        Base.metadata.create_all(bind=engine)
        create_default_user()



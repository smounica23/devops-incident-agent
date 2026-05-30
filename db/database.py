from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base
import os

def get_engine():
    return create_engine(
        os.getenv("DATABASE_URL", "postgresql://admin:admin123@localhost:5432/incidents"),
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def create_tables():
    """Create all tables in PostgreSQL"""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")

def get_db():
    """FastAPI dependency — gives a DB session per request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# ============================================================
# Database Engine
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "development",
)


# ============================================================
# Database Session
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ============================================================
# Base Model
# ============================================================

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.

    Every model in the application will inherit from Base.
    """
    pass


# ============================================================
# Database Dependency
# ============================================================

def get_db():
    """
    Provides a database session to FastAPI endpoints.

    The session is automatically closed after the request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
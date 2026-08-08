import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("marine_twin.db")

database_url = settings.DATABASE_URL
engine_kwargs = {}

if database_url.startswith("sqlite"):
    logger.info("SQLite database detected")
    # Extract file path from URL (e.g. sqlite:///./marine_twin.db -> ./marine_twin.db)
    db_file = database_url.split("///")[-1]
    logger.info(f"Database file: {db_file}")
    
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }
else:
    logger.info("PostgreSQL database detected")
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }

try:
    engine = create_engine(database_url, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    # Final safety fallback to in-memory SQLite if everything else fails
    fallback_url = "sqlite:///:memory:"
    logger.warning(f"Using critical fallback: {fallback_url}")
    engine = create_engine(
        fallback_url,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency injection wrapper for DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

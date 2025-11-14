from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# Load environment variables from .env if present
load_dotenv()

# Database URL: defaults to local SQLite if not provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create SQLModel / SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    """Create all tables defined on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session

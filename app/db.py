from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./hero_api.db"

engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def create_db_and_tables() -> None:
    """Create all tables. Called once on application startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a DB session per-request."""
    with Session(engine) as session:
        yield session

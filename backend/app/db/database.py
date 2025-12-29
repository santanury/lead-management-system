from sqlmodel import SQLModel, create_engine, Session
from app.config import settings
from typing import Generator

engine = create_engine(settings.database_url)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

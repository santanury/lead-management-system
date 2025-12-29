from sqlmodel import SQLModel
from app.db.database import engine
from app.models import lead # Import models so they are registered
from app.models import settings # Import Settings model

def init_db():
    SQLModel.metadata.create_all(engine)

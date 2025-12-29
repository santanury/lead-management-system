from sqlmodel import SQLModel
from app.db.database import engine
from app.models import lead # Import models so they are registered

def init_db():
    SQLModel.metadata.create_all(engine)

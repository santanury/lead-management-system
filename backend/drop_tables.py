from app.db.database import engine
from sqlmodel import SQLModel
from app.models.lead import Lead
from sqlalchemy import text

def drop_lead_table():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS lead CASCADE;"))
        conn.commit()
    print("Dropped lead table.")

if __name__ == "__main__":
    drop_lead_table()

from sqlmodel import Session, select
from app.db.database import engine
from app.models.lead import Lead

def test_connection():
    try:
        print("Connecting to DB...")
        with Session(engine) as session:
            print("Connected.")
            results = session.exec(select(Lead)).all()
            print(f"Leads found: {len(results)}")
        print("DB Check Pass.")
    except Exception as e:
        print(f"DB Check Fail: {e}")

if __name__ == "__main__":
    test_connection()

# init_db.py
from app.db.database import engine
from app.models import models
from dotenv import load_dotenv

def init_db():
    """Initialize the database by creating all tables"""
    models.Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

if __name__ == "__main__":
    load_dotenv()
    init_db()
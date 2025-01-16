from sqlalchemy import create_engine
from app.models import models
import os
from google.cloud.sql.connector import Connector

def get_db_url():
    connector = Connector()
    conn = connector.connect(
        os.environ["DATABASE_URL"],
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"]
    )
    return conn

engine = create_engine(get_db_url())

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
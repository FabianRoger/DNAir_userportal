# app/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google.cloud.sql.connector import Connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_url():
    """Get database URL based on environment"""
    if os.getenv('ENVIRONMENT') == 'cloud':
        # Cloud SQL connection
        connector = Connector()
        
        def getconn():
            conn = connector.connect(
                "dnair-database:us-central1:edna-db",  # Cloud SQL instance connection name
                "pg8000",
                user="admin_edna",
                password="eDNA_Admin_2025!",
                db="edna-db"
            )
            return conn

        return getconn
    else:
        # Local development - Use PostgreSQL
        return "postgresql://admin_edna:admin@localhost/edna-db"

def get_engine():
    """Get SQLAlchemy engine based on environment"""
    if os.getenv('ENVIRONMENT') == 'cloud':
        return create_engine(
            "postgresql+pg8000://",
            creator=get_db_url(),
        )
    else:
        return create_engine(get_db_url())

# Create engine
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
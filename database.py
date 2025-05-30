import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class for ORM models
Base = declarative_base()

#use singleton pattern for session
def init_db():
    """Init Database and create tablesn."""
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Dependency for db !!!!! Refactor to database.py soon
def get_db():
    """Get database session."""
    db = SessionLocal()  
    try:
        return db 
    finally:
        db.close()  
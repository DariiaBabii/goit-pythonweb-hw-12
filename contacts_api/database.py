from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./contacts.db"

# Create the SQLAlchemy engine to connect to the SQLite database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

def get_db():
    """
    Creates and manages a database session.

    This function returns a session that can be used for database operations.
    The session will be closed automatically when the work with it is finished.

    Returns:
        Session: A new database session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SessionLocal is used to create a new session for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models to be defined using SQLAlchemy's declarative system
Base = declarative_base()


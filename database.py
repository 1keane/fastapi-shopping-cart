from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL for PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db/shopping_cart"

# Create a SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for the declarative models
Base = declarative_base()

# Function to initialize the database
def init_db():
    # Create all tables in the database based on the Base metadata
    Base.metadata.create_all(bind=engine)

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        # Provide the database session to the caller
        yield db
    finally:
        # Ensure the database session is closed after use
        db.close()


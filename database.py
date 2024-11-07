from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL_ENV = os.getenv("DATABASE_URL_ENV")

if not DATABASE_URL_ENV:
    raise ValueError("DATABASE_URL_ENV is not set in the environment variables.")
engine = create_engine(DATABASE_URL_ENV)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
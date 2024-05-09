from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (
                           self.name, self.fullname, self.nickname)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection(engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Database connection successful. Result: {result.scalar()}")
    except OperationalError:
        print("Failed to connect to the database.")

if __name__ == "__main__":
  # Test the connection
  test_connection(engine)
import json
import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, ForeignKey, PickleType
from sqlalchemy.orm import relationship
from pydantic import BaseModel, validator
from decimal import Decimal, ROUND_DOWN
from typing import Literal

from backend.utils.db import Base, get_db

load_dotenv()

SYMBOLS = os.getenv('SYMBOLS').split(',')
initial_symbols = {symbol: 0 for symbol in SYMBOLS}

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return "<User(username='%s')>" % (
                           self.username)
class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String)
    score = Column(Integer, default=0)
    symbols = Column(PickleType, default=initial_symbols)

    user = relationship("User", back_populates="leaderboard")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

User.leaderboard = relationship("Leaderboard", order_by=Leaderboard.id, back_populates="user")

class MarketRequestMessage(BaseModel):
    symbol: str
    dir: Literal['BUY', 'SELL']
    price: Decimal
    shares: int

    @validator('price', pre=True)
    def round_price(cls, v):
        return Decimal(v).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

if __name__ == "__main__":
    def clear_leaderboard(session):
        try:
            session.query(Leaderboard).delete()
            session.commit()
            print("Leaderboard table cleared successfully.")
        except Exception as e:
            session.rollback()
            print(f"Failed to clear Leaderboard table. Error: {e}")

    clear_leaderboard(next(get_db()))
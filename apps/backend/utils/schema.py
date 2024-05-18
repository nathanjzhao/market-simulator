import json
from sqlalchemy import Column, Integer, String, ForeignKey 
from sqlalchemy.orm import relationship
from pydantic import BaseModel, validator
from decimal import Decimal, ROUND_DOWN
from typing import Literal
from sqlalchemy.ext.declarative import declarative_base

from backend.utils.db import Base

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
    username = Column(String, ForeignKey('users.username'))
    score = Column(Integer)

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

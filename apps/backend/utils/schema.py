from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, validator
from decimal import Decimal, ROUND_DOWN
from typing import Literal
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return "<User(username='%s')>" % (
                           self.username)

class MarketRequestMessage(BaseModel):
    symbol: str
    dir: Literal['BUY', 'SELL']
    price: str

    # @validator('price', pre=True)
    # def round_price(cls, v):
    #     return Decimal(v).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

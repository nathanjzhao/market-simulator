import json
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, validator
from decimal import Decimal, ROUND_DOWN
from typing import Literal
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

class MarketRequestMessage(BaseModel):
    symbol: str
    dir: Literal['BUY', 'SELL']
    price: Decimal
    count: int

    @validator('price', pre=True)
    def round_price(cls, v):
        return Decimal(v).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

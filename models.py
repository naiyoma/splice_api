from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base  = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class TestUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column(String, name="uuid", primary_key=True, default=generate_uuid)
    phone_number = Column(String)
    fiatBalance = Column(String, default="0 KES")
    btcBalance = Column(Integer, default=0)
    lightingAddress = Column(String, default="")
    withdrawalFee = Column(Integer, default=0)

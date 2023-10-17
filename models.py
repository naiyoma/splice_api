from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base  = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())


class TestUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)


class CurrencyEnum(str, enum.Enum):
    NGN = "NGN"
    KES = "KES"
    BTC = "BTC"

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(String, name="uuid", primary_key=True, default=generate_uuid)
    phone_number = Column(String, nullable=False)
    lightning_address = Column(String, nullable=False)
    withdrawal_fee = Column(Integer, default=0)

    balances = relationship("Balance", back_populates="wallet")

class Balance(Base): 
    __tablename__ = 'balances'
    id = Column(Integer, primary_key=True, default=generate_uuid)
    wallet_id = Column(String, ForeignKey('wallets.uuid'), nullable=False)
    amount = Column(Float, default=0.0)
    currency = Column(Enum(CurrencyEnum), nullable=False)

    wallet = relationship("Wallet", back_populates="balances")

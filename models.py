from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base  = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(String, primary_key=True, default=generate_uuid)
    phone_number = Column(String, nullable=False, unique=True)
    lightning_address = Column(String, nullable=False, unique=True)
    withdrawal_fee = Column(Integer, default=0)
    preferred_fiat_currency = Column(String, nullable=False)

    # Define one-to-many relationship with Balance
    balances = relationship("Balance", back_populates="wallet")


class Balance(Base):
    __tablename__ = 'balances'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(String, ForeignKey('wallets.id'), nullable=False)
    amount = Column(Float, default=0.0)
    currency = Column(String, nullable=False)

    # Define many-to-one relationship with Wallet
    wallet = relationship("Wallet", back_populates="balances")


class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, default=0.0)
    asset_id = Column(String, nullable=False, unique=True)
    currency = Column(String, nullable=False, unique=True)

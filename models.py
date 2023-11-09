from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Boolean
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

    # Define relationship with a Payment for the receiver and the sender
    sent_payments = relationship("Payment", back_populates="sender_wallet", foreign_keys='Payment.source_wallet_id')
    received_payments = relationship("Payment", back_populates="receiver_wallet", foreign_keys='Payment.receiver_wallet_id')
    

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


class Payment(Base):
    # a wallet can have many payments
    # a payment is associated with one sender wallet and one receiver wallet 
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    payment_status = Column(String, default="Pending")
    source_wallet_id = Column(String, ForeignKey('wallets.id', name='fk_payments_source_wallet_id'), nullable=False)
    receiver_wallet_id = Column(String, ForeignKey('wallets.id', name='fk_payments_receiver_wallet_id'), nullable=False)
    sent_payment = Column(Boolean, default=False)
    receive_payment = Column(Boolean, default=False)
    fees = Column(Integer, default=0)
    # Define many-to-one relationship with Wallet for receiver wallet and for sender wallet
    receiver_wallet = relationship("Wallet", back_populates="received_payments", foreign_keys=[receiver_wallet_id])
    sender_wallet = relationship("Wallet", back_populates="sent_payments", foreign_keys=[source_wallet_id])
    

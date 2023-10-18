import os
import uuid
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Depends
from fastapi_sqlalchemy import DBSessionMiddleware, db

from typing import List, Tuple

from schema import WalletCreateSchema
from schema import WalletResponseSchema
from schema import BalanceResponse
from schema import InvoiceRequestSchema
from schema import WalletDetailResponseSchema
from schema import InvoiceResponseSchema

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Wallet, Balance, CurrencyEnum

from sqlalchemy.orm import Session


from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()


app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DEFAULT_FIAT_BALANCE = 100000.0
DEFAULT_BTC_BALANCE = 5.0

@app.post('/api/invoices', response_model=InvoiceResponseSchema)  # Use the response schema
async def create_invoice(invoice_request: InvoiceRequestSchema,  db: Session = Depends(get_db)):
    # use the lightning address to figure out the withdrawal fee for the merchant/agent 
    # add the withdrawal to the amount to send. 
    # create ask tapd to create an invoice for the amount to send
    # Do an FX for the KES To NGN, using our set rates.
    # return invoice/address and amount Precious has to pay in NGN
    receiver_wallet = db.query(Wallet).filter(Wallet.lightning_address == invoice_request.destionationAddress).first()
    sender_wallet = db.query(Wallet).filter(Wallet.id == invoice_request.walletId).first()
    if receiver_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    amount_to_send = invoice_request.amount + receiver_wallet.withdrawal_fee
    amount_to_pay = forex(amount_to_send, sender_wallet.preferred_fiat_currency, receiver_wallet.preferred_fiat_currency)
    response_data = {
        "invoice": "",
        "amount": amount_to_pay,
        "currency": sender_wallet.preferred_fiat_currency,
    }
    return response_data
    

@app.post('/api/wallets', response_model=WalletResponseSchema)  # Use the response schema
async def create_wallet(wallet: WalletCreateSchema):

    new_wallet = Wallet(
        phone_number=wallet.phoneNumber,
        withdrawal_fee=wallet.withdrawalFee,
        preferred_fiat_currency=wallet.preferredFiatCurrency,
        lightning_address=wallet.phoneNumber + "@splice.africa",
    )

    db.session.add(new_wallet)
    db.session.commit()

    fiat_balance = Balance(
        amount=DEFAULT_FIAT_BALANCE,
        currency=new_wallet.preferred_fiat_currency,
        wallet_id=new_wallet.id
    )

    btc_balance = Balance(
        amount=DEFAULT_BTC_BALANCE,
        currency="BTC",
        wallet_id=new_wallet.id
    )

    db.session.add(fiat_balance)
    db.session.add(btc_balance)
    db.session.commit()

    response_data = {
        "id": new_wallet.id,
        "lighting_address": new_wallet.lightning_address,  # Corrected field name
        "withdrawal_fee": new_wallet.withdrawal_fee,  # Corrected field name
        "balances": [
            {"amount": fiat_balance.amount, "currency": fiat_balance.currency.value},
            {"amount": btc_balance.amount, "currency": btc_balance.currency.value}
        ]
    }
    return response_data

@app.get('/api/wallets/{wallet_id}', response_model=WalletDetailResponseSchema)
async def get_wallet_by_id(
    wallet_id: str = Path(..., title="The ID of the wallet to retrieve"),
    db: Session = Depends(get_db)
):
    db_wallet = get_wallet_from_db(wallet_id, db)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    response_data = {
        "walletID": db_wallet.id,
        "fiatBalance": fiat_balance,
        "btcBalance": btc_balance,
        "lightingAddress": f"{db_wallet.phone_number}@splice.africa",
        "withdrawalFee": db_wallet.withdrawal_fee,
    }
    return response_data


def get_wallet_from_db(wallet_id: str, db: Session = Depends(get_db)) -> Wallet:
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def forex(amount_to_send, sender_fiat_currency, receiver_fiat_currency):
    if sender_fiat_currency == receiver_fiat_currency:
        raise HTTPException(status_code=400, detail="Sender and receiver fiat currencies cannot be the same")
    rate_key = f"{receiver_fiat_currency}/{sender_fiat_currency}"
    rates = {
        "NGN/KES": 0.20,
        "KES/NGN": 5.11,
        "BTC/KES": 4235589.39,
        "KES/BTC": 0.000000236,
        "BTC/NGN": 21644172.60,
        "NGN/BTC": 0.000000046,
    }

    return amount_to_send * rates[rate_key]


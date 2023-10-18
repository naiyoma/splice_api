import os
import uuid
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Depends
from fastapi_sqlalchemy import DBSessionMiddleware, db

from typing import List, Tuple

from schema import TestUserSchema
from schema import WalletCreateSchema
from schema import WalletResponseSchema
from schema import BalanceResponse
from schema import WalletDetailResponseSchema

from sqlalchemy.orm import Session
from database import SessionLocal
from models import TestUser, Wallet, Balance, CurrencyEnum

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
    
    fiat_balance, btc_balance = calculate_balances(db_wallet.balances)
    
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

def calculate_balances(balances: List[Balance]) -> Tuple[float, float]:
        fiat_balance = 0.0
        btc_balance = 0.0
        for balance in balances:
            if balance.currency == CurrencyEnum.NGN or balance.currency == CurrencyEnum.KES:
                fiat_balance += balance.amount
            elif balance.currency == CurrencyEnum.BTC:
                btc_balance += balance.amount
        return fiat_balance, btc_balance


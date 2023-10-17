import os
import uuid
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware, db

from typing import List

from schema import TestUserSchema
from schema import WalletCreateSchema
from schema import WalletResponseSchema

from models import TestUser, Wallet

from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()


app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])

@app.get("/")
async def root():
    return {"message": "hello world"}


@app.post('/test_user/', response_model=TestUserSchema)
async def user(user:TestUserSchema):
    db_user= TestUser(name=user.name, age=user.age)
    db.session.add(db_user)
    db.session.commit()
    return db_user

@app.get('/users/')
async def test_users():
    test_user = db.session.query(TestUser).all()
    return test_user


# @app.post('/wallets/create', response_model=WalletCreateSchema)
# async def wallet(wallet:WalletCreateSchema):
#     db_wallet= Wallet(phone_number=wallet.phone_number, withdrawalFee=wallet.withdrawalFee)
#     db.session.add(db_wallet)
#     db.session.commit()
#     return db_wallet

@app.post('/wallets/create', response_model=WalletResponseSchema)  # Use the response schema
async def create_wallet(wallet: WalletCreateSchema):

    db_wallet = Wallet(
        phone_number=wallet.phone_number,
    withdrawalFee=wallet.withdrawalFee
    )
    db.session.add(db_wallet)
    db.session.commit()

    # Calculate the response fields
    fiat_balance = "10"
    btc_balance = 10
    response_data = {
        "id": db_wallet.id,  # Use db_wallet.id to get the generated UUID
        "fiatBalance": fiat_balance,
        "btcBalance": btc_balance,
        "lightingAddress": f"{wallet.phone_number}@splice.africa",
        "withdrawalFee": wallet.withdrawalFee
    }
    return response_data 

@app.get('/wallets/{wallet_id}/', response_model=WalletResponseSchema)
async def get_wallet_by_id(wallet_id: str):
    # import pdb; pdb.set_trace()
    db_wallet = db.session.query(Wallet).filter(Wallet.id == wallet_id).first()
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    response_data = {
        "id": db_wallet.id,
        "fiatBalance": db_wallet.fiatBalance,
        "btcBalance": db_wallet.btcBalance,
        "lightingAddress": f"{db_wallet.phone_number}@splice.africa",
        "withdrawalFee": db_wallet.withdrawalFee
    }
    return response_data

@app.get('/wallets/', response_model=List[WalletResponseSchema])
async def get_all_wallets():
    db_wallets = db.session.query(Wallet).all()

    # Assuming you have logic to calculate fiat_balance and btc_balance for each wallet
    wallets_data = []
    for db_wallet in db_wallets:
        fiat_balance = db_wallet.fiatBalance
        btc_balance = db_wallet.btcBalance

        wallet_data = {
            "id": db_wallet.id,
            "fiatBalance": fiat_balance,
            "btcBalance": btc_balance,
            "lightingAddress": f"{db_wallet.phone_number}@splice.africa",
            "withdrawalFee": db_wallet.withdrawalFee
        }
        wallets_data.append(wallet_data)

    return wallets_data

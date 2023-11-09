import os
import uuid
import uvicorn
import time
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Path
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware, db

from typing import List, Tuple

from schema import WalletCreateSchema
from schema import WalletResponseSchema
from schema import BalanceResponse
from schema import InvoiceRequestSchema
from schema import InvoiceResponseSchema
from schema import PaymentRequestSchema
from schema import PaymentResponseSchema
from schema import ClaimPaymentResponseSchema
from schema import RateResponseSchema
from schema import CalculateRequestSchema
from schema import CalculateResponseSchema
from schema import RampInvoiceRequestSchema
from schema import RampInvoiceResponseSchema
from schema import RampPaymentRequestSchema
from schema import RampPaymentResponseSchema
from schema import PaymentsResponse
from schema import PaymentResponse
from schema import PaymentFilterRequest

from sqlalchemy.orm import Session
from database import SessionLocal
from models import Wallet, Balance, Asset, Payment

from sqlalchemy.orm import Session

from assets import create_asset, finalize_asset_creation, burn_asset, generate_address, send_asset, list_assets, get_transfers


from dotenv import load_dotenv

load_dotenv('.env')


app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add DBSession middleware
# Ensure you've imported DBSessionMiddleware before this
app.add_middleware(
    DBSessionMiddleware, 
    db_url=os.environ['DATABASE_URL']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DEFAULT_FIAT_BALANCE = 100000.0
DEFAULT_BTC_BALANCE = 2.0
rates = {
    "NGN/KES": 0.20,
    "KES/NGN": 5.11,
    "BTC/KES": 4235589.39,
    "KES/BTC": 0.000000236,
    "BTC/NGN": 21644172.60,
    "NGN/BTC": 0.000000046,
}

@app.post('/api/invoices', response_model=InvoiceResponseSchema)  # Use the response schema
async def create_invoice(invoice_request: InvoiceRequestSchema,  db: Session = Depends(get_db)):
    # use the lightning address to figure out the withdrawal fee for the merchant/agent 
    # add the withdrawal to the amount to send. 
    # create ask tapd to create an invoice for the amount to send
    # Do an FX for the KES To NGN, using our set rates.
    # return invoice/address and amount Precious has to pay in NGN
    receiver_wallet = db.query(Wallet).filter(Wallet.lightning_address == invoice_request.destionationAddress).first()
    receiver_asset = db.query(Asset).filter(Asset.currency == receiver_wallet.preferred_fiat_currency).first()
    sender_wallet = db.query(Wallet).filter(Wallet.id == invoice_request.walletId).first()
    if receiver_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    amount_to_send = invoice_request.amount + receiver_wallet.withdrawal_fee
    amount_to_pay = forex(amount_to_send, sender_wallet.preferred_fiat_currency, receiver_wallet.preferred_fiat_currency)
    address = generate_address(receiver_asset.asset_id, amount_to_send)

    payment = Payment(
        amount=amount_to_pay,
        currency=sender_wallet.preferred_fiat_currency,
        source_wallet_id=sender_wallet.id,
        receiver_wallet_id=receiver_wallet.id
    )
    db.add(payment)
    db.commit()

    response_data = {
        "invoice": address['encoded'],
        "amount": amount_to_pay,
        "currency": sender_wallet.preferred_fiat_currency,
    }
    return response_data

@app.post('/api/invoices/send', response_model=PaymentResponseSchema)  # Use the response schema
async def pay_invoice(payment_request: PaymentRequestSchema,  db: Session = Depends(get_db)):
    # pay invoice
    payment_res = send_asset(payment_request.tapdAddress)
    # deduct amount from sender wallet balance
    sender_wallet = db.query(Wallet).filter(Wallet.lightning_address == payment_request.sourceAddress).first()
    receiver_wallet = db.query(Wallet).filter(Wallet.lightning_address == payment_request.destinationAddress).first()
    if sender_wallet is None or receiver_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    for balance in sender_wallet.balances:
        if balance.currency != 'BTC':
            balance.amount -= payment_request.amount

    for balance in receiver_wallet.balances:
        if balance.currency != 'BTC':
            balance.amount += forex(payment_request.amount, receiver_wallet.preferred_fiat_currency, sender_wallet.preferred_fiat_currency)

    db.add(sender_wallet)
    db.add(receiver_wallet)
    db.commit()
    # burn equivalent amount of NGN asset
    assets = list_assets()
    asset_id = ''
    for asset in assets['assets']:
        if asset['asset_genesis']['name'] == sender_wallet.preferred_fiat_currency:
            asset_id = asset['asset_genesis']['asset_id']
    asset = burn_asset(asset_id, payment_request.amount)
    # mint equivalent amount of KES asset
    create_asset(receiver_wallet.preferred_fiat_currency, forex(payment_request.amount, receiver_wallet.preferred_fiat_currency, sender_wallet.preferred_fiat_currency))
    finalize_asset_creation()

    response_data = {
        "proofOfPayment": payment_res['transfer']['anchor_tx_hash'],
        "amount": payment_request.amount,
        "currency": sender_wallet.preferred_fiat_currency,
        "destinationAddress": payment_request.destinationAddress,
    }
    return response_data

@app.get('/api/invoices/<txid>', response_model=ClaimPaymentResponseSchema)
async def claim_payment(txid: str):
    # check if there is any asset transfer with this ID
    # if there is return true if there is not return false
    transfers = get_transfers()
    for transfer in transfers['transfers']:
        if transfer['anchor_tx_hash'] == txid:
            return {
                "succeeded": True
            }
    return {
        "succeeded": False
    }

@app.get('/api/rate/<source>/<destination>', response_model=RateResponseSchema)
async def get_rate(source: str, destination: str):
    rate_key = f"{source}/{destination}"
    return {
        "rate": rates[rate_key]
    }

@app.post('/api/on/calculate', response_model=CalculateResponseSchema)
async def amount_to_receive(req: CalculateRequestSchema):
    to_receive = req.rate * req.amount
    return {
        "amount": to_receive,
        "currency": req.destination
    }

@app.post('/api/on/invoices', response_model=RampInvoiceResponseSchema)
async def get_ramp_invoice(req: RampInvoiceRequestSchema):
    assets = list_assets()
    asset_id = ''
    for asset in assets['assets']:
        if asset['asset_genesis']['name'] == req.currency:
            asset_id = asset['asset_genesis']['asset_id']
    if req.currency == 'BTC':
        req.amount = req.amount * 100000000
    address = generate_address(asset_id, req.amount)

    return {
        "destinationAddress": address['encoded'],
    }

@app.post('/api/on/invoices/send', response_model=RampPaymentResponseSchema)
async def pay_ramp_invoice(req: RampPaymentRequestSchema, db: Session = Depends(get_db)):
    payment_res = send_asset(req.destinationAddress)
    if payment_res["code"] == 2:
        return {
            "paymentId": "000000000000000",
            "status": "Payment Uncofirmed"
        }
    else:
        
        receiver_wallet = db.query(Wallet).filter(Wallet.lightning_address == req.lightningAddress).first()
        if receiver_wallet is None:
            raise HTTPException(status_code=404, detail="Wallet not found")

        for balance in receiver_wallet.balances:
            if balance.currency == req.currency:
                balance.amount += req.amount
        
        db.add(receiver_wallet)
        db.commit()

        return {
            "paymentId": payment_res['transfer']['anchor_tx_hash'],
            "status": "Payment successful"
        }


@app.post('/api/wallets', response_model=WalletResponseSchema)  # Use the response schema
async def create_wallet(wallet: WalletCreateSchema, db: Session = Depends(get_db)):
    #import pdb; pdb.set_trace()
    new_wallet = Wallet(
        phone_number=wallet.phoneNumber,
        withdrawal_fee=wallet.withdrawalFee,
        preferred_fiat_currency=wallet.preferredFiatCurrency,
        lightning_address=wallet.phoneNumber + "@splice.africa",
    )

    db.add(new_wallet)
    db.commit()

    fiat_asset = create_asset(wallet.preferredFiatCurrency, DEFAULT_FIAT_BALANCE)
    btc_asset = create_asset("BTC", DEFAULT_BTC_BALANCE)
    finalize_asset_creation()

    existing_fiat_asset = db.query(Asset).filter(Asset.currency == wallet.preferredFiatCurrency).first()

   

    if existing_fiat_asset:
        # If an asset with the same name exists, update it
        existing_fiat_asset.amount += DEFAULT_FIAT_BALANCE
        db.add(existing_fiat_asset)
    else:
        # If not, create a new asset
        # Sleep for 30 seconds, so that asset gets confirmed
        time.sleep(35)
        assets = list_assets()
        asset_id = ''
        for asset in assets['assets']:
            if asset['asset_genesis']['name'] == wallet.preferredFiatCurrency:
                asset_id = asset['asset_genesis']['asset_id']
        new_asset = Asset(
            amount=DEFAULT_FIAT_BALANCE,
            asset_id=asset_id,
            currency=wallet.preferredFiatCurrency
        )
        db.add(new_asset)

    existing_btc_asset = db.query(Asset).filter(Asset.currency == 'BTC').first()

    if existing_btc_asset:
        # If an asset with the same name exists, update it
        existing_btc_asset.amount += DEFAULT_BTC_BALANCE
        db.add(existing_btc_asset)
    else:
        # If not, create a new asset
        # Sleep for 30 seconds, so that asset gets confirmed
        time.sleep(35)
        assets = list_assets()
        asset_id = ''
        for asset in assets['assets']:
            if asset['asset_genesis']['name'] == 'BTC':
                asset_id = asset['asset_genesis']['asset_id']
        new_asset = Asset(
            amount=DEFAULT_BTC_BALANCE,
            asset_id=asset_id,
            currency='BTC'
        )
        db.add(new_asset)

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

    db.add(fiat_balance)
    db.add(btc_balance)
    db.commit()

    response_data = {
        "id": new_wallet.id,
        "lightning_address": new_wallet.lightning_address,  # Corrected field name
        "withdrawal_fee": new_wallet.withdrawal_fee,  # Corrected field name
        "preferred_fiat_currency": new_wallet.preferred_fiat_currency,
        "balances": [
            {"amount": fiat_balance.amount, "currency": fiat_balance.currency},
            {"amount": btc_balance.amount, "currency": btc_balance.currency}
        ]
    }
    return response_data

@app.get('/api/wallets/{wallet_id}', response_model=WalletResponseSchema)
async def get_wallet_by_id(
    wallet_id: str = Path(..., title="The ID of the wallet to retrieve"),
    db: Session = Depends(get_db)
):
    db_wallet = get_wallet_from_db(wallet_id, db)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    response_data = {
        "id": db_wallet.id,
        "balances": db_wallet.balances,
        "lightning_address": db_wallet.lightning_address,
        "withdrawal_fee": db_wallet.withdrawal_fee,
        "preferred_fiat_currency": db_wallet.preferred_fiat_currency
    }
    return response_data

@app.get('/api/wallets', response_model=List[WalletResponseSchema])
def get_all_wallets(db: Session = Depends(get_db)):
    wallets = db.query(Wallet).all()
    return wallets


def get_wallet_from_db(wallet_id: str, db: Session = Depends(get_db)) -> Wallet:
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()


def forex(amount_to_send, sender_fiat_currency, receiver_fiat_currency):
    if sender_fiat_currency == receiver_fiat_currency:
        raise HTTPException(status_code=400, detail="Sender and receiver fiat currencies cannot be the same")
    rate_key = f"{receiver_fiat_currency}/{sender_fiat_currency}"

    return amount_to_send * rates[rate_key]




@app.get("/api/payments/{wallet_id}/", response_model=PaymentsResponse) 
async def get_payments_for_wallet(wallet_id: str, db: Session = Depends(get_db)):
    sender_payments = db.query(Payment).filter(Payment.source_wallet_id == wallet_id).all()
    receiver_payments = db.query(Payment).filter(Payment.receiver_wallet_id == wallet_id).all()
    all_payments = sender_payments + receiver_payments
    payments_response = []
    
    for payment in all_payments:
        sender_wallet = db.query(Wallet).get(payment.source_wallet_id)
        receiver_wallet = db.query(Wallet).get(payment.receiver_wallet_id)
        
        sent_payment = payment.source_wallet_id == wallet_id
        receive_payment = payment.receiver_wallet_id == wallet_id
        
        payment_response = PaymentResponse(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            timestamp=payment.timestamp,
            payment_status=payment.payment_status,
            sender_wallet=sender_wallet.__dict__,
            receiver_wallet=receiver_wallet.__dict__,
            sent_payment=sent_payment,
            receive_payment=receive_payment,
        )
        payments_response.append(payment_response)
        
    return PaymentsResponse(payments=payments_response)

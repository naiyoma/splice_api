from pydantic import BaseModel
from typing import List, Literal
from typing import Optional
from datetime import datetime

Currency = Literal["NGN", "KES", "BTC"]

class WalletCreateSchema(BaseModel):
    phoneNumber: str
    withdrawalFee: int
    preferredFiatCurrency: Currency

class BalanceBase(BaseModel):
    amount: float
    currency: Currency

class Balance(BalanceBase):
    id: int
    walletId: str

    class Config:
        orm_mode = True

class BalanceResponse(BaseModel):
    amount: float
    currency: Currency


class WalletResponseSchema(BaseModel):
    id: str
    lightning_address: str
    preferred_fiat_currency: str
    withdrawal_fee: int
    balances: List[BalanceResponse] = []

    class Config:
        orm_mode = True


class InvoiceRequestSchema(BaseModel):
    walletId: str
    destionationAddress: str
    amount: float
    currency: Currency

class InvoiceResponseSchema(BaseModel):
    invoice: str
    amount: float
    currency: Currency

class PaymentRequestSchema(BaseModel):
    sourceAddress: str
    amount: float
    currency: Currency
    destinationAddress: str
    tapdAddress: str

class PaymentResponseSchema(BaseModel):
    proofOfPayment: str
    amount: float
    currency: Currency
    destinationAddress: str

class ClaimPaymentResponseSchema(BaseModel):
    succeeded: bool

class RateResponseSchema(BaseModel):
    rate: float

class CalculateRequestSchema(BaseModel):
    source: str
    destination: str
    amount: float
    rate: float

class CalculateResponseSchema(BaseModel):
    amount: float
    currency: Currency

class RampInvoiceRequestSchema(BaseModel):
    amount: float
    currency: Currency

class RampInvoiceResponseSchema(BaseModel):
    destinationAddress: str

class RampPaymentRequestSchema(BaseModel):
    destinationAddress: str
    amount: float
    currency: Currency
    lightningAddress: str

class RampPaymentResponseSchema(BaseModel):
    paymentId: str
    status: str

class WalletResponse(BaseModel):
    id: str
    phone_number: str
    lightning_address: str
    withdrawal_fee: int
    preferred_fiat_currency: str


class PaymentFilterRequest(BaseModel):
    sender_wallet_id: Optional[str] = None
    receiver_wallet_id: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    timestamp: datetime
    payment_status: str
    sender_wallet: WalletResponse
    receiver_wallet: WalletResponse
    sent_payment: bool = False
    receive_payment: bool = False

class PaymentsResponse(BaseModel):
    payments: List[PaymentResponse] = []



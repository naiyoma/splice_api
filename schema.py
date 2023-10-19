from pydantic import BaseModel
from typing import List


class WalletCreateSchema(BaseModel):
    phoneNumber: str
    withdrawalFee: int
    preferredFiatCurrency: str

class BalanceBase(BaseModel):
    amount: float
    currency: str

class Balance(BalanceBase):
    id: int
    walletId: str

    class Config:
        orm_mode = True

class BalanceResponse(BaseModel):
    amount: float
    currency: str


class WalletResponseSchema(BaseModel):
    id: str
    lightingAddress: str
    withdrawalFee: int
    balances: List[BalanceResponse] = []

    class Config:
        orm_mode = True


class InvoiceRequestSchema(BaseModel):
    walletId: str
    destionationAddress: str
    amount: float
    currency: str

class InvoiceResponseSchema(BaseModel):
    invoice: str
    amount: float
    currency: str

class PaymentRequestSchema(BaseModel):
    sourceAddress: str
    amount: float
    currency: str
    destinationAddress: str
    tapdAddress: str

class PaymentResponseSchema(BaseModel):
    proofOfPayment: str
    amount: float
    currency: str
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
    currency: str

class RampInvoiceRequestSchema(BaseModel):
    amount: float
    currency: str

class RampInvoiceResponseSchema(BaseModel):
    destinationAddress: str

class RampPaymentRequestSchema(BaseModel):
    destinationAddress: str
    amount: float
    currency: str
    lightningAddress: str

class RampPaymentResponseSchema(BaseModel):
    paymentId: str
    status: str
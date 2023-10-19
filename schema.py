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
    lighting_address: str
    withdrawal_fee: int
    balances: List[BalanceResponse] = []

    class Config:
        orm_mode = True


class WalletDetailResponseSchema(BaseModel):
    walletID: str
    fiatBalance: float
    btcBalance: float
    lightingAddress: str
    withdrawalFee: int

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

from pydantic import BaseModel

class TestUserSchema(BaseModel):
    name:str
    age:int

    class Config:
        orm_mode = True

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

class WalletResponseSchema(BaseModel):
    id: str
    lighting_address: str
    withdrawal_fee: int
    balances: list[Balance] = []

    class Config:
        orm_mode = True
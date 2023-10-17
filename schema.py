from pydantic import BaseModel

class TestUserSchema(BaseModel):
    name:str
    age:int

    class Config:
        orm_mode = True

class WalletCreateSchema(BaseModel):
    phone_number: str
    withdrawalFee: int

class WalletResponseSchema(BaseModel):
    id: str
    fiatBalance: str
    btcBalance: int
    lightingAddress: str
    withdrawalFee: int
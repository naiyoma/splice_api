from pydantic import BaseModel

class TestUserSchema(BaseModel):
    name:str
    age:int

    class Config:
        orm_mode = True
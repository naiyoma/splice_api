import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import TestUserSchema
from models import TestUser

import os
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
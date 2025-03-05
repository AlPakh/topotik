from fastapi import FastAPI
from db import database, User
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.get("/users")
def get_users():
    session = Session(bind=database)
    users = session.query(User).all()
    return users

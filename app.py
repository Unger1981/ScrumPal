from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from Classes import AuthUser ,Base , pwd_context
from dotenv import load_dotenv




load_dotenv()
# FastAPI app
app = FastAPI()

# SQLAlchemy Setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure your models are properly created in the database
Base.metadata.create_all(bind=engine)

# JWT Secret und Algorithmus
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token Ablaufzeit in Minuten

# Pydantic Models
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()  # Create a new session
    try:
        return db  # Return the session directly
    finally:
        db.close()  # Close the session after use



@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = AuthUser(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}






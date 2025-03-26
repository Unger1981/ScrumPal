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

#Table constructor for DB
#Base.metadata.create_all(bind=engine)

# SQLAlchemy Setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# JWT Secret und Algorithmus
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
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
    new_user = AuthUser(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        print(db_user)
        print(pwd_context.verify(user.password, db_user.password_hash))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Dict for Token Data
    token_data = {
        "sub": db_user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates JWT Token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
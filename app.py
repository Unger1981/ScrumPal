from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timedelta
from Classes import AuthUser, User, pwd_context
from database import SessionLocal, init_db  # Achte darauf, dass init_db hier importiert wird
from token_functions import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme


load_dotenv()


app = FastAPI()

# Init database
#init_db()   !!! Potential function to check wheater DB exist or not. Clarify with Michal

# Pydantic-Modelle
class RegisterUser(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_type: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency for db !!!!! Refactor to database.py soon
def get_db():
    db = SessionLocal()  
    try:
        return db 
    finally:
        db.close()  

# Registrierungs-Endpunkt
@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    existing_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = AuthUser(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

# Login-Endpunkt
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Token-Daten
    token_data = {
        "sub": db_user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

# Benutzererstellung für Admins
@app.post("/create_user")
def create_user(user: UserCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verifiziere den Token
    user_info = verify_token(token)
    
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    db_auth_user = db.query(AuthUser).filter(AuthUser.email == user_info['sub']).first()
    
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=db_auth_user.email,  # E-Mail stuck to auth user email
        user_type=user.user_type,  
        auth_user_id=db_auth_user.id  #Relation auth user
    )
    # Neuen User in die DB einfügen
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}


@app.get("/users")
def get_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Verifiziere den Token
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_auth_user = db.query(AuthUser).filter(AuthUser.email == user_info['sub']).first()
    
    if not db_auth_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AuthUser not found")
    db_users = db.query(User).filter(User.auth_user_id == db_auth_user.id).all()

    return db_users
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timedelta
from Classes import AuthUser, User, Project, pwd_context
from database import SessionLocal, init_db  # Achte darauf, dass init_db hier importiert wird
from token_functions import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme


load_dotenv()


app = FastAPI()

# Init database
init_db()   #!!! Potential function to check wheater DB exist or not. Clarify with Michal

# Pydantic-Modelle  Refactor into an own module
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

class ProjectCreate(BaseModel):
    name: str
    description: str
       


# Dependency for db !!!!! Refactor to database.py soon
def get_db():
    db = SessionLocal()  
    try:
        return db 
    finally:
        db.close()  

@app.post("/register",status_code=201)
def register(user: RegisterUser, db: Session = Depends(get_db)):
    """Register a new user."""
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
    """Login and return an access token."""
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


@app.post("/create_user",status_code=201)
def create_user(user: UserCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new user."""
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
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}


@app.get("/users")
def get_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get all users."""                
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_auth_user = db.query(AuthUser).filter(
        AuthUser.email == user_info['sub']
    ).first()
    
    if not db_auth_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AuthUser not found")
    db_users = db.query(User).filter(User.auth_user_id == db_auth_user.id).all()

    return db_users

@app.delete("/delete_user/{user_id}")
def delete_user(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete a user by ID."""
    user_info = verify_token(token)
    if not user_info:       
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_user = db.query(User).filter(
        User.id == user_id,
        User.email == user_info['sub']
    ).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"User with ID {user_id} successfully deleted"}

#Projects

@app.post("/create_projects/{user_id}", status_code=201)
def create_project(user_id: int ,project: ProjectCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new project by user.id with ownership."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(
        User.email == user_info['sub'],
        User.id == user_id,
        User.user_type == 'Owner' # Assuming only Owner can create projects
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_project = Project(
    name=project.name,
    description=project.description,
    created_by=user.id,  # Assuming created_by is the ID of the user creating the project
    created_at=datetime.utcnow()
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
# token_utils.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from Classes import tokens
from sqlalchemy.orm import Session  
from database import  get_db
import jwt
import os

# JWT Konfiguration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates JWT Token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Verifies the JWT token and returns the payload.
    """
    if token in blacklisted_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is already blacklisted")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def blacklist_token(token: str, db: Session):
    """
    Blacklists a token by adding it to a blacklist db.
    If Token cant be stored in DB, it will be stored in a temporary blacklist.
    This function checks if the token is already blacklisted and stores it in the database if not.
    If the token is already blacklisted, it raises an HTTPException.
    Args:
        token (str): The JWT token to be blacklisted.
        db (Session): The database session to interact with the tokens table.
    Raises:
        HTTPException: If the token is already blacklisted or if there is an error during the database operation.
    """

    blacklisted_token= token 
    try:
        db_token =db.query(tokens).filter(tokens.token == blacklisted_token).one_or_none()
    except Exception as e:    
        print(f"[ERROR] DB Token query failed: {e}")
        raise HTTPException(status_code=500, detail="Error querying Token in DB")
    if not db_token:
        try:
            new_token = tokens(
            token=token
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            if token in blacklisted_tokens:
                del blacklisted_tokens[token]
            print("[INFO] Token added to DB blacklist")
        except Exception as e:
            db.rollback()
            if not token in blacklisted_tokens:
            # If the token is not in the temporary blacklist, add it
                blacklisted_tokens[token] = True
            print(f"[ERROR] DB Token creation failed: {e} Stored in temporary blacklist")
            raise HTTPException(status_code=500, detail="Error creating Token in DB")    
 


blacklisted_tokens = {}   # temporary for blacklisted tokens IMPLEMENTATON in DB in progress for multi threading support



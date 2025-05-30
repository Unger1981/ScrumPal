# token_utils.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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


def blacklist_token(token: str):
    """
    Blacklists a token by adding it to a blacklist.
    This is a placeholder function; actual implementation would require a database or in-memory store.
    """
  
    blacklisted_token= token 
    if blacklisted_token in blacklisted_tokens:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already blacklisted")
    blacklisted_tokens[token] = True  # Add token to blacklist



blacklisted_tokens = {}   # Placeholder for blacklisted tokens IMPLEMENTATON in DB in progress for multi threading support
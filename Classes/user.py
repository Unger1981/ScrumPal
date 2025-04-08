from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

import sys


class User(Base):
    """Model representing a user profile."""
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String, unique=True, nullable=False)
    user_type = Column(String(100), default='Member')
    auth_user_id = Column(Integer, ForeignKey('auth_users.id'), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
   
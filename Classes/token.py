from database import Base
from sqlalchemy import Column, Integer, String, DateTime, func



class tokens(Base):
    """Model representing a token stored for Logout feature."""
    __tablename__ = 'Tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), nullable=False, unique=True)
    blacklisted_at = Column(DateTime, nullable=False, server_default=func.now())
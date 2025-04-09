from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, relationship
from passlib.context import CryptContext
from database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthUser(Base):
    """Model representing an authenticated user."""
    __tablename__ = 'auth_users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relatio User !!!!! Dont forget next time idiot
    users = relationship('User', back_populates='auth_user') 

    def verify_password(self, password: str) -> bool:
        """Verify if the given password matches the stored password hash."""
        return pwd_context.verify(password, self.password_hash)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Change the password if the old password is verified successfully."""
        if self.verify_password(old_password):
            self.password_hash = pwd_context.hash(new_password)
            return True
        return False

    def __repr__(self):
        """Return a string representation of the AuthUser instance."""
        return f"email={self.email}, created_at={self.created_at})"

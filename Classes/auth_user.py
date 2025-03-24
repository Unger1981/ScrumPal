from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

import sys
print(sys.path)  # Gibt die Suchpfade aus, um zu sehen, ob Classes enthalten ist
# SQLAlchemy-Base definieren
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthUser(Base):
    __tablename__ = 'Auth_users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # Automatisch gesetzt

    def __init__(self,  email: str, password: str):
        self.email = email
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Check if password is correct"""
        return pwd_context.verify(password, self.password_hash)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """Changes the password if verify_password returns True."""
        if self.verify_password(old_password):
            self.password_hash = pwd_context.hash(new_password)
            return True
        return False

    def __repr__(self):
        """Dunder method to represent the object as a string"""
        return f"email={self.email}, created_at={self.created_at})"


user = AuthUser("test@example.com", "geheim123")

print(user.verify_password("geheim123"))  # True
print(user.verify_password("falsch"))  # False

# Passwort ändern
user.change_password("geheim123", "neuesPasswort")
print(user.verify_password("geheim123"))  # False
print(user.verify_password("neuesPasswort"))  # True

print(user.__repr__())  # AuthUser(username=testuser,
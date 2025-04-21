from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .auth_user import AuthUser
from .project_members import project_members
from database import Base

class User(Base):
    """Model representing a user profile."""
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String, nullable=False)
    user_type = Column(String(100), default='Member')
    auth_user_id = Column(Integer, ForeignKey('auth_users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship zu Projekten
    projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    projects = relationship( "Project",secondary=project_members,back_populates="members")

    # AuthUser-Beziehung
    auth_user = relationship('AuthUser', back_populates='users')  

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default='Active')
    created_by = Column(Integer, ForeignKey('Users.id'), nullable=False)  # Der ForeignKey auf 'Users.id'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehung zum User (Creator des Projekts)
    creator = relationship("User", back_populates="projects", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status}, created_at={self.created_at})>"

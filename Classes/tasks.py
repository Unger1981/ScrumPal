from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from .user import User



class Task(Base):
    """Model representing a task in a project management system."""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_to = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=False)
    status = Column(String(50), default='To Do')
    priority = Column(String(50), default='Normal')
    due_date = Column(DateTime, nullable=True)
    type = Column(String(50), default='Task')
    estimated_duration = Column(Integer, nullable=True)  
    created_by = Column(Integer,  nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referencing relationsship for parent child
    parent_task = relationship("Task", remote_side=[id], backref="sub_tasks", uselist=False)


   

    def __repr__(self):
        return f"<Task(title={self.title}, status={self.status}, created_at={self.created_at})>"

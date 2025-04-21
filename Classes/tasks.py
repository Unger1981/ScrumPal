from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base



class Task(Base):
    """Model representing a task in a project management system."""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    assigned_to = Column(Integer, ForeignKey('project_members.id'), nullable=True)
    status = Column(String(50), default='To Do')
    type = Column(String(50), default='Task')
    estimated_duration = Column(Integer, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Self-referencing relationsship for parent child
    parent_task = relationship("Task", remote_side=[id], backref="sub_tasks", uselist=False)

    # Relationship with Project memb
    assigned_member = relationship("ProjectMember", back_populates="tasks", foreign_keys=[assigned_to])

    def __repr__(self):
        return f"<Task(title={self.title}, status={self.status}, created_at={self.created_at})>"

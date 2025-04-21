from sqlalchemy import Table, Column, Integer, ForeignKey
from database import Base

project_members = Table(
    'project_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('Users.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
)

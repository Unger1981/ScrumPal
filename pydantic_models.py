from pydantic import BaseModel, EmailStr 
from enum import Enum
from datetime import datetime



class RegisterUser(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    user_type: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProjectCreate(BaseModel):
    user_id: int	
    name: str
    description: str

class ProjectUser(BaseModel):
    project_id: int
    owner_id: int    
    new_user_id: int
    new_user_mail: EmailStr

class TaskType(str, Enum):
    backlog = "Backlog"
    sprint = "Sprint"
    task = "Task"    

class TaskCreate(BaseModel):
    title: str
    description: str
    parent_task_id: int = None
    created_by: int 
    assigned_to: int = None
    project_id: int
    status: str = "To Do"
    priority: str = "Normal"
    due_date: datetime = None
    type: TaskType
    estimated_duration: int = None  


   
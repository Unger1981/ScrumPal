from datetime import datetime, timedelta
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session  
from Classes import AuthUser, User, Project, project_members, Task, pwd_context
from database import init_db, get_db  # Achte darauf, dass init_db hier importiert wird
from token_functions import( create_access_token, verify_token, blacklist_token,
ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme)
from pydantic_models import (RegisterUser, UserCreate, UserLogin,
ProjectCreate, ProjectUser,TaskType, TaskCreate)

app = FastAPI()

# Init database
init_db()   #!!! Potential function to check wheater DB exist or not. Clarify with Michal

# Login/Register/Logout

@app.post("/register",status_code=201)
def register(user: RegisterUser, db: Session = Depends(get_db)):
    """Register a new user."""
    existing_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    try:
        new_user = AuthUser(email=user.email, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] User registration failed: {e}")
    return {"message": "User registered successfully"}


@app.post("/login")

def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login and return an access token."""
    db_user = db.query(AuthUser).filter(AuthUser.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Token-Daten
    token_data = {
        "sub": db_user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Logout endpoint to blacklist the token."""
    try:
        blacklist_token(token,db)
    except Exception as e:     
        print(f"[ERROR] Token blacklisting failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error blacklisting token")
    return {"message": "Logged out successfully"}

# USER

@app.post("/create_user",status_code=201)
def create_user(user: UserCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new user."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_auth_user = db.query(AuthUser).filter(AuthUser.email == user_info['sub']).first()
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=db_auth_user.email, 
        user_type=user.user_type,  
        auth_user_id=db_auth_user.id  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}


@app.get("/users")
def get_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get all users."""                
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_auth_user = db.query(AuthUser).filter(
        AuthUser.email == user_info['sub']
    ).first()
    if not db_auth_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AuthUser not found")
    db_users = db.query(User).filter(User.auth_user_id == db_auth_user.id).all()

    return db_users


@app.delete("/delete_user/{user_id}")
def delete_user(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete a user by ID."""
    user_info = verify_token(token)
    if not user_info:       
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    db_user = db.query(User).filter(
        User.id == user_id,
        User.email == user_info['sub']
    ).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    try:
        db.delete(db_user)
        db.commit()
        return {"message": f"User with ID {user_id} successfully deleted"}
    except Exception as e:
        db.rollback()
        print(f"[ERROR] User deletion failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting user")

# PROJECTS

@app.post("/create_projects", status_code=201)
def create_project(project: ProjectCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new project by user.id with ownership."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(
        User.email == user_info['sub'],
        User.id == project.user_id,
        User.user_type == 'Owner'
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        new_project = Project(
        name=project.name,
        description=project.description,
        product_owner_id=project.user_id, 
        created_by=project.user_id,
        created_at=datetime.utcnow()
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Project creation failed: {e}")
        raise HTTPException(status_code=500, detail="Error creating project")    
    return  {"message": f"Project created successfully", "project_id": new_project.id}


@app.get("/projects/{user_id}", status_code=200)
def get_projects(user_id:int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get all projects by user.id. if member or owner of project."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    projects = db.query(Project).filter(
        (Project.product_owner_id == user_id) |
        (Project.members.any(User.id == user_id))
    ).all()
    if not projects:        
        raise HTTPException(status_code=404, detail="No projects found for this user")
    projects = [project for project in projects if project.product_owner_id == user_id or user_id in [member.id for member in project.members]]
    return projects


@app.delete("/delete_project/{project_id}", status_code=204)
def delete_project(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete a project by ID. Only the product owner can delete the project."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_project = db.query(Project).filter(
        Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_user = db.query(User).filter(
        User.id == db_project.product_owner_id,
        User.email == user_info['sub']
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found with necessary permissions")
    try:
        db.delete(db_project)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Project deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Error deleting project")    
    return {"message": f"Project with ID {project_id} successfully deleted"}    
    
# PROJECT MEMBERS JUNCTION TABLE

@app.post("/add_user_to_project", status_code=201)
def add_user_to_project(project_user:ProjectUser, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Add a user to a project. Only the product owner can add users to the project."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_project = db.query(Project).filter(
        Project.id == project_user.project_id,
        Project.product_owner_id == project_user.owner_id  
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found with necessary permissions")        
   
    user_to_add = db.query(User).filter(
            User.id == project_user.new_user_id,
            User.email == project_user.new_user_mail
        ).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User to add not found")
    
    existing_link = db.execute(
        select(project_members).where(
            project_members.c.user_id == user_to_add.id,
            project_members.c.project_id == db_project.id
        )
    ).first()

    if existing_link:
        raise HTTPException(status_code=400, detail="User is already in the project")
    try:
               # Fixed duo to problems with duplicate check (internal 500 error)
        db.execute(
            project_members.insert().values(
                user_id=user_to_add.id,
                project_id=db_project.id
            )
        )
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Adding user to project failed: {e}")
        raise HTTPException(status_code=500, detail="Error adding user to project")    

    return {"message": f"User ID {project_user.new_user_id} added to project ID {project_user.project_id}"}


@app.delete("/remove_user_from_project", status_code=200)
def remove_user_from_project(project_user:ProjectUser, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Remove a user from a project. Only the product owner can remove users from the project."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_project = db.query(Project).filter(
        Project.id == project_user.project_id,
        Project.product_owner_id == project_user.owner_id  
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found with necessary permissions")        
    
    user_to_remove = db.query(User).filter(
            User.id == project_user.new_user_id,
            User.email == project_user.new_user_mail
        ).first()
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User to remove not found")
    
    existing_link = db.execute(
        select(project_members).where(
            project_members.c.user_id == user_to_remove.id,
            project_members.c.project_id == db_project.id
        )
    ).first()

    if not existing_link:
        raise HTTPException(status_code=400, detail="User is not in the project")
    
    try:
        db.execute(
            project_members.delete().where(
                project_members.c.user_id == user_to_remove.id,
                project_members.c.project_id == db_project.id
                                          )
                    )
        db.commit()
        db.refresh(db_project)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Removing user from project failed: {e}")
        raise HTTPException(status_code=500, detail="Error removing user from project")    

    return {"message": f"User ID {project_user.new_user_id} removed from project ID {project_user.project_id}"}


@app.get("/project_members/{project_id}", status_code=200)
def get_project_members(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get all members of a project. If member or owner of project"""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_project = db.query(Project).filter(
        Project.id == project_id
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        members = db.query(User).join(project_members).filter(
            project_members.c.project_id == project_id
        ).all()
        owner = db.query(User).filter(
            User.id == db_project.product_owner_id
        ).first()
        if owner:
            members.append(owner)  # Add the owner to the list of members
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Fetching project members failed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching project members")
    
    return members

#TASKS

@app.post("/create_task", status_code=201)          
def create_task(task: TaskCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Create a new task."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_project = db.query(Project).filter(
        Project.id == task.project_id, 
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    if db_project.product_owner_id == task.created_by and task.type in TaskType.__members__.values():
        try:    
            create_task_entity(task.type, task, db)
            return {"message": "Task created successfully"}
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Task creation failed: {e}")
            raise HTTPException(status_code=500, detail="Error creating task")    
    user_by_auth_user = db.query(User).filter(
        user_info["sub"] == User.email,
        User.id == task.created_by
    ).first()
    if not user_by_auth_user:   
        raise HTTPException(status_code=404, detail="User not assigned to login user")
    is_member =db.execute(
        select(project_members).where(
            project_members.c.user_id == task.created_by,
                )
    ).first()
    if not is_member:
        raise HTTPException(status_code=403, detail="User is not a member of the project or product owner")
    if is_member and user_by_auth_user and task.type == "Task" and task.parent_task_id is not None:
        try:
           create_task_entity(task.type, task, db)
           return {"message": f"Task created successfully"}
        except Exception as e:      
            db.rollback()
            print(f"[ERROR] Task creation failed: {e}")
            raise HTTPException(status_code=500, detail="Error creating task")
    else:
        raise HTTPException(status_code=403, detail="Wrong Task Type")
    

@app.get("/tasks/{user_id}", status_code=200)
def get_tasks(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get all tasks of a user."""
    try:
        user_info = verify_token(token)
        if not user_info:
            raise HTTPException(status_code=401, detail="Invalid token")
        db_user = db.query(User).filter(
            User.email == user_info['sub'],
            User.id == user_id	
        ).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="No User found")
        db_tasks = db.query(Task).filter(
            (Task.assigned_to == user_id) |
            (Task.created_by == user_id)
        ).all()
        return db_tasks
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Fetching tasks failed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tasks")


@app.delete("/delete_task/{task_id}", status_code=204)
def delete_task(task_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Delete a task by ID."""
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_task = db.query(Task).filter(
        Task.id == task_id
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        db.delete(db_task)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Task deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Error deleting task")    
    return {"message": f"Task with ID {task_id} successfully deleted"}    
    

def create_task_entity(Task_type: str, task: TaskCreate, db: Session):
    """Create a new task entity in db dependign on type."""
    new_task = Task(
            title=task.title,
            description=task.description,
            parent_task_id=task.parent_task_id,
            created_by=task.created_by,
            assigned_to=task.assigned_to,
            project_id=task.project_id,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            type=Task_type,
            estimated_duration=task.estimated_duration
         )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": f"Task created successfully", "task_id": new_task.id}
    
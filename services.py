import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from Classes import Task
from pydantic_models import TaskCreate



def validate_password(password: str) -> bool:
    """
    Validates a password based on the following criteria:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character (e.g., !@#$%^&*()-_=+[]{}|;:'",.<>?/)
    
    :param password: The password to validate.
    :return: True if the password is valid, False otherwise.
    """
    try:
        if len(password) < 8:	
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
        
        if not re.search(r'[a-z]', password):
            return False
        
        if not re.search(r'\d', password):
            return False
        
        if not re.search(r'[!@#$%^&*()\-_+=\[\]{}|;:\'",.<>?]', password):
            return False
        
        return True
    except Exception as e:
        print(f"[ERROR] Password validation failed: {e}")
        raise HTTPException(status_code=500, detail="Error validating password")
    

def create_task_entity(Task_type: str, task: TaskCreate, db: Session):
    """Create a new task entity in db dependign on type.    
    Args:
        Task_type (str): The type of the task to create.
        task (TaskCreate): The task data to create.
        db (Session): The database session.
    Raises:
        HTTPException: If there is an error during task creation.
    Returns:
        dict: A message indicating successful task creation and the task ID.
    """ 
    try:
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
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Task creation failed: {e}")
        raise HTTPException(status_code=500, detail="Error creating task in DB")
    
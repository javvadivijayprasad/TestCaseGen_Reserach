from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Get a single task by ID"""
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    completed: Optional[bool] = None
) -> List[models.Task]:
    """Get all tasks with optional filtering"""
    query = db.query(models.Task)
    
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    
    return query.offset(skip).limit(limit).all()


def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    """Create a new task"""
    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(
    db: Session, 
    task_id: int, 
    task_update: schemas.TaskUpdate
) -> Optional[models.Task]:
    """Update an existing task"""
    db_task = get_task(db, task_id)
    
    if db_task is None:
        return None
    
    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Delete a task by ID"""
    db_task = get_task(db, task_id)
    
    if db_task is None:
        return False
    
    db.delete(db_task)
    db.commit()
    return True
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, models, schemas
from app.database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="A simple REST API for managing tasks",
    version="1.0.0"
)


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """Welcome endpoint"""
    return {
        "message": "Welcome to Task Manager API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.post(
    "/tasks/",
    response_model=schemas.Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"]
)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db)
) -> models.Task:
    """Create a new task"""
    return crud.create_task(db=db, task=task)


@app.get(
    "/tasks/",
    response_model=List[schemas.Task],
    tags=["Tasks"]
)
def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(get_db)
) -> List[models.Task]:
    """Get all tasks with optional filtering"""
    return crud.get_tasks(db=db, skip=skip, limit=limit, completed=completed)


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    tags=["Tasks"]
)
def read_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> models.Task:
    """Get a specific task by ID"""
    db_task = crud.get_task(db=db, task_id=task_id)
    
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return db_task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    tags=["Tasks"]
)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
) -> models.Task:
    """Update a specific task"""
    db_task = crud.update_task(db=db, task_id=task_id, task_update=task_update)
    
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return db_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"]
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a specific task"""
    success = crud.delete_task(db=db, task_id=task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    return None
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas import TaskCreate, TaskOut
from app.auth import get_db, get_current_user
from app.crud import (
    create_task,
    get_tasks,
    get_task,
    get_tasks_by_date,
    get_tasks_by_user,
    get_tasks_by_status,
    update_task,
    delete_task,
)
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter()


@router.post("/", response_model=TaskOut)
def create_new_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new task"""
    return create_task(
        db=db,
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=task.user_id,
        start_date=task.start_date,
        end_date=task.end_date,
        jira_link=task.jira_link,
        created_by=task.created_by,
        pull_requests_links=task.pull_requests_links,
        priority=task.priority,
    )


@router.get("/", response_model=List[TaskOut])
def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tasks with pagination"""
    return get_tasks(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskOut)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a specific task by ID"""
    db_task = get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.get("/date/{start_date}/{end_date}", response_model=List[TaskOut])
def read_tasks_by_date(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tasks within a specific date range"""
    return get_tasks_by_date(
        db, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )


@router.get("/user/{user_id}", response_model=List[TaskOut])
def read_tasks_by_user(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tasks assigned to a specific user"""
    return get_tasks_by_user(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/status/{status}", response_model=List[TaskOut])
def read_tasks_by_status(
    status: str,
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of tasks to return"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tasks with a specific status"""
    return get_tasks_by_status(db, status=status, skip=skip, limit=limit)


@router.put("/{task_id}", response_model=TaskOut)
def update_existing_task(
    task_id: int,
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update an existing task"""
    db_task = update_task(
        db=db,
        task_id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
        user_id=task.user_id,
        start_date=task.start_date,
        end_date=task.end_date,
        jira_link=task.jira_link,
        pull_requests_links=task.pull_requests_links,
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update only the status of a task"""
    db_task = update_task(db=db, task_id=task_id, status=status)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.patch("/{task_id}/assign", response_model=TaskOut)
def assign_task_to_user(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Assign a task to a different user"""
    db_task = update_task(db=db, task_id=task_id, user_id=user_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.delete("/{task_id}")
def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a task"""
    db_task = delete_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"msg": "Task deleted successfully"}

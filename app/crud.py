from app.models import Item, Task, User
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException


def create_item(db: Session, title: str, description: str):
    db_item = Item(title=title, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session):
    return db.query(Item).all()


def update_item(db: Session, item_id: int, title: str, description: str):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db_item.title = title
        db_item.description = description
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def create_task(db: Session, title: str, description: str, status: str, user_id: int, 
                start_date: datetime, end_date: datetime, jira_link: str, 
                created_by: int, pull_requests_links: str):
    # Validate that user_id exists
    if user_id and not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    
    # Validate that created_by exists
    if created_by and not db.query(User).filter(User.id == created_by).first():
        raise HTTPException(status_code=400, detail=f"User with id {created_by} does not exist")
    
    db_task = Task(
        title=title,
        description=description,
        status=status,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        jira_link=jira_link,
        created_by=created_by,
        pull_requests_links=pull_requests_links
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()


def get_tasks_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.status == status).offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, title: str = None, description: str = None,
                status: str = None, user_id: int = None, start_date: datetime = None,
                end_date: datetime = None, jira_link: str = None, 
                pull_requests_links: str = None):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        if title is not None:
            db_task.title = title
        if description is not None:
            db_task.description = description
        if status is not None:
            db_task.status = status
        if user_id is not None:
            db_task.user_id = user_id
        if start_date is not None:
            db_task.start_date = start_date
        if end_date is not None:
            db_task.end_date = end_date
        if jira_link is not None:
            db_task.jira_link = jira_link
        if pull_requests_links is not None:
            db_task.pull_requests_links = pull_requests_links
        db.commit()
        db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

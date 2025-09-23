from app.models import Item, Task, User
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import case
from sentence_transformers import SentenceTransformer
from app.database import collection

model = SentenceTransformer("all-MiniLM-L6-v2")


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


def create_task(
    db: Session,
    title: str,
    description: str,
    status: str,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    jira_link: str,
    created_by: int,
    pull_requests_links: str,
    priority: str,
):
    # Validate that user_id exists
    if user_id and not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(
            status_code=400, detail=f"User with id {user_id} does not exist"
        )

    # Validate that created_by exists
    if created_by and not db.query(User).filter(User.id == created_by).first():
        raise HTTPException(
            status_code=400, detail=f"User with id {created_by} does not exist"
        )

    db_task = Task(
        title=title,
        description=description,
        status=status,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        jira_link=jira_link,
        created_by=created_by,
        pull_requests_links=pull_requests_links,
        priority=priority,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Generate and store the embedding for the task description
    embeddings = model.encode(description)

    collection.add(
        ids=[str(db_task.id)],
        embeddings=embeddings,
        metadatas=[{"task_id": db_task.id, "title": title, "description": description}],
    )

    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(
            Task.id,
            Task.title,
            Task.description,
            Task.status,
            Task.user_id,
            Task.start_date,
            Task.end_date,
            Task.jira_link,
            Task.created_by,
            Task.pull_requests_links,
            Task.priority,
            User.username,
        )
        .join(User, Task.user_id == User.id)
        .order_by(
            # Custom ordering for priority: high -> medium -> low
            case(
                (Task.priority == "high", 1),
                (Task.priority == "medium", 2),
                (Task.priority == "low", 3),
                else_=4,
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()
    )


def get_tasks_by_status(db: Session, status: str, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.status == status).offset(skip).limit(limit).all()


def get_tasks_by_date(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(Task)
        .filter(Task.start_date >= start_date, Task.end_date <= end_date)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_task(
    db: Session,
    task_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    user_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    jira_link: str = None,
    pull_requests_links: str = None,
):
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

        # Generate and store the embedding for the task description
        embedding = model.encode([f"{title} {description}"])[0]

        collection.add(
            ids=[str(db_task.id)],
            embeddings=[embedding],
            metadatas=[{"text": f"{title} {description}"}],
        )

    return db_task


def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task


def search_tasks(db: Session, query: str, top_k: int = 5):
    # Generate the embedding for the query
    query_embedding = model.encode([query])[0]

    # Perform the similarity search in the vector database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    # Destructure
    ids = results["ids"][0]
    # metadatas = [m["text"] for m in results["metadatas"][0]]
    distances = results["distances"][0]

    matching_task_ids = []
    for i in range(len(ids)):
        if round(distances[i]) <= 1:  # Adjust threshold as needed
            matching_task_ids.append(ids[i])

    task_ids = [int(id) for id in matching_task_ids]

    if not task_ids:
        return []

    # Retrieve the corresponding tasks from the relational database
    tasks = (
        db.query(Task)
        .filter(Task.id.in_(task_ids))
        .order_by(case(*[(Task.id == id, index) for index, id in enumerate(task_ids)]))
        .all()
    )

    return tasks

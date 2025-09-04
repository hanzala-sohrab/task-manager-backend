from app.models import Item
from sqlalchemy.orm import Session

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

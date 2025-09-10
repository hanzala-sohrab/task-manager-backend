from fastapi import APIRouter, Depends, HTTPException
from app.schemas import ItemCreate, ItemOut
from app.auth import get_db, get_current_user
from app.crud import create_item, get_items, update_item, delete_item
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


@router.post("/", response_model=ItemOut)
def create(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_item(db, item.title, item.description)


@router.get("/", response_model=List[ItemOut])
def read(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_items(db)


@router.put("/{item_id}", response_model=ItemOut)
def update(
    item_id: int,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_item = update_item(db, item_id, item.title, item.description)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/{item_id}")
def delete(
    item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    db_item = delete_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"msg": "Item deleted"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.table import Table
from app.database.deps import get_db
from app.core.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
 
router = APIRouter(prefix="/tables", tags=["Tables"])
 
class TableCreate(BaseModel):
    number: str
    name: Optional[str] = None
 
class TableOut(BaseModel):
    id: int
    number: str
    name: Optional[str]
    active: bool
    restaurant_id: int
    class Config:
        from_attributes = True
 
@router.post("/", response_model=TableOut)
def create_table(data: TableCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") not in ["dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    table = Table(number=data.number, name=data.name, restaurant_id=user.get("restaurant_id"))
    db.add(table)
    db.commit()
    db.refresh(table)
    return table
 
@router.get("/restaurant/{restaurant_id}", response_model=list[TableOut])
def list_tables(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Table).filter(Table.restaurant_id == restaurant_id, Table.active == True).all()
 
@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Mesa nao encontrada")
    if user.get("role") not in ["dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    db.delete(table)
    db.commit()
    return {"message": "Mesa removida"}
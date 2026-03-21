from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.restaurant import Restaurant
from app.models.user import User
from app.models.order import Order
from app.models.product import Product
from app.database.deps import get_db
from app.core.security import hash_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

class RestaurantCreate(BaseModel):
    name: str

class RestaurantOut(BaseModel):
    id: int
    name: str
    active: bool
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    restaurant_id: Optional[int] = None

@router.post("/", response_model=RestaurantOut)
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    r = Restaurant(name=data.name)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("/", response_model=list[RestaurantOut])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante nao encontrado")
    db.delete(r)
    db.commit()
    return {"message": "Restaurante removido"}

@router.patch("/{restaurant_id}/toggle")
def toggle_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Restaurante nao encontrado")
    r.active = not r.active
    db.commit()
    return {"id": r.id, "active": r.active}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_restaurants = db.query(Restaurant).count()
    active_restaurants = db.query(Restaurant).filter(Restaurant.active == True).count()
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_users = db.query(User).filter(User.role != 'admin').count()
    return {
        "total_restaurants": total_restaurants,
        "active_restaurants": active_restaurants,
        "total_orders": total_orders,
        "total_products": total_products,
        "total_users": total_users
    }

@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
        restaurant_id=data.restaurant_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Usuario criado com sucesso", "id": user.id}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.database.deps import get_db
from app.core.auth import get_current_user, require_same_restaurant

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") not in ["dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/restaurant/{restaurant_id}", response_model=List[ProductOut])
def list_products(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") != "admin" and user.get("restaurant_id") != restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(Product).filter(Product.restaurant_id == restaurant_id).all()

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    if user.get("role") not in ["dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if user.get("role") != "admin" and product.restaurant_id != user.get("restaurant_id"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    if user.get("role") not in ["dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if user.get("role") != "admin" and product.restaurant_id != user.get("restaurant_id"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    db.delete(product)
    db.commit()
    return {"message": "Produto excluido com sucesso"}

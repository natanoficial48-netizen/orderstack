from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductCreate

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
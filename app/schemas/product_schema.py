from pydantic import BaseModel
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    restaurant_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    restaurant_id: int

    class Config:
        from_attributes = True

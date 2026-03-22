from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    observacao: Optional[str] = None

class OrderCreate(BaseModel):
    restaurant_id: int
    user_id: int
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    observacao: Optional[str] = None

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    status: str
    total: float
    created_at: datetime
    restaurant_id: int
    user_id: int
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

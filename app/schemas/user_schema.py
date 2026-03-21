from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    restaurant_id: Optional[int] = None

class UserLogin(BaseModel):
    email: str
    password: str

"""
Modelo de Usuário.

Representa quem acessa o sistema:
- Admin (dono da hamburgueria)
- Garçom
"""

from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String)

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
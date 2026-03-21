"""
Modelo de Restaurante.
"""

from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
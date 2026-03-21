from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.models.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))

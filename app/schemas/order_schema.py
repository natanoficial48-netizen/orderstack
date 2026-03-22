from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base
 
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pendente")
    total = Column(Float, default=0.0)
    impresso = Column(Boolean, default=False)
    table_id = Column(Integer, nullable=True)
    table_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    items = relationship("OrderItem", back_populates="order")
 
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer)
    unit_price = Column(Float)
    observacao = Column(String, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    order = relationship("Order", back_populates="items
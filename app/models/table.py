from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.models.base import Base
 
class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String)
    name = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
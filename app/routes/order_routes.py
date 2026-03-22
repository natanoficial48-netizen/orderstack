from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order_schema import OrderCreate, OrderOut
from app.database.deps import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut)
def create_order(data: OrderCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") not in ["garcom", "dono", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    order = Order(restaurant_id=data.restaurant_id, user_id=data.user_id, status="pendente")
    db.add(order)
    db.flush()
    total = 0.0
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {item.product_id} nao encontrado")
        order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, unit_price=product.price)
        db.add(order_item)
        total += product.price * item.quantity
    order.total = total
    db.commit()
    db.refresh(order)
    return order

@router.get("/restaurant/{restaurant_id}", response_model=List[OrderOut])
def list_orders(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") != "admin" and user.get("restaurant_id") != restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(Order).filter(Order.restaurant_id == restaurant_id).all()

@router.patch("/{order_id}/status")
def update_status(order_id: int, status: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    if user.get("role") != "admin" and user.get("restaurant_id") != order.restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    order.status = status
    db.commit()
    return {"message": f"Status atualizado para '{status}'"}

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    if user.get("role") != "admin" and user.get("restaurant_id") != order.restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return order

@router.patch("/{order_id}/impresso")
def marcar_impresso(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    order.impresso = True
    db.commit()
    return {"message": "Pedido marcado como impresso"}

@router.get("/restaurant/{restaurant_id}/nao-impressos")
def pedidos_nao_impressos(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user.get("role") != "admin" and user.get("restaurant_id") != restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        Order.impresso == False
    ).all()
    return orders

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.restaurant import Restaurant
from app.database.deps import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/restaurant/{restaurant_id}/sales")
def get_sales(restaurant_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.restaurant_id == restaurant_id).all()
    total = sum(o.total for o in orders)
    entregues = [o for o in orders if o.status == "entregue"]
    return {
        "total_orders": len(orders),
        "total_delivered": len(entregues),
        "total_revenue": total,
        "average_ticket": total / len(entregues) if entregues else 0
    }

@router.get("/restaurant/{restaurant_id}/top-products")
def get_top_products(restaurant_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue")
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.restaurant_id == restaurant_id)
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )
    top = []
    for r in results:
        prod = db.query(Product).filter(Product.id == r.product_id).first()
        top.append({
            "product_id": r.product_id,
            "name": prod.name if prod else f"Produto #{r.product_id}",
            "total_qty": r.total_qty,
            "total_revenue": float(r.total_revenue)
        })
    return top

@router.get("/restaurant/{restaurant_id}/orders/history")
def get_history(restaurant_id: int, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .filter(Order.restaurant_id == restaurant_id)
        .order_by(Order.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": o.id,
            "status": o.status,
            "total": o.total,
            "user_id": o.user_id,
            "created_at": o.created_at.isoformat(),
            "items_count": len(o.items)
        }
        for o in orders
    ]

@router.get("/restaurant/{restaurant_id}/team")
def get_team(restaurant_id: int, db: Session = Depends(get_db)):
    users = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role != "admin"
    ).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]

@router.get("/restaurant/{restaurant_id}/info")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    return {"id": r.id, "name": r.name, "active": r.active}

@router.put("/restaurant/{restaurant_id}/info")
def update_restaurant(restaurant_id: int, data: dict, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if data.get("name"):
        r.name = data["name"]
    db.commit()
    return {"message": "Restaurante atualizado"}

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.restaurant import Restaurant
from app.database.deps import get_db
from app.core.auth import get_current_user
from datetime import datetime, date
 
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
 
@router.get("/restaurant/{restaurant_id}/sales")
def get_sales(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    orders = db.query(Order).filter(Order.restaurant_id == restaurant_id).all()
    total = sum(o.total for o in orders)
    entregues = [o for o in orders if o.status == "entregue"]
    return {
        "total_orders": len(orders),
        "total_delivered": len(entregues),
        "total_revenue": total,
        "average_ticket": total / len(entregues) if entregues else 0
    }
 
@router.get("/restaurant/{restaurant_id}/caixa-diario")
def get_caixa_diario(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    hoje = date.today()
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        func.date(Order.created_at) == hoje
    ).all()
    entregues = [o for o in orders if o.status == "entregue"]
    pendentes = [o for o in orders if o.status == "pendente"]
    em_preparo = [o for o in orders if o.status == "em preparo"]
    prontos = [o for o in orders if o.status == "pronto"]
    total = sum(o.total for o in entregues)
 
    # Breakdown por forma de pagamento
    pagamentos = {}
    for o in entregues:
        pm = o.payment_method or "nao informado"
        pagamentos[pm] = pagamentos.get(pm, 0) + o.total
 
    return {
        "data": hoje.strftime("%d/%m/%Y"),
        "total_pedidos": len(orders),
        "entregues": len(entregues),
        "em_andamento": len(pendentes) + len(em_preparo) + len(prontos),
        "faturamento": total,
        "ticket_medio": total / len(entregues) if entregues else 0,
        "pagamentos": pagamentos
    }
 
@router.get("/restaurant/{restaurant_id}/relatorio-mensal")
def get_relatorio_mensal(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
 
    def get_mes_data(mes, ano):
        orders = db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            extract('month', Order.created_at) == mes,
            extract('year', Order.created_at) == ano,
            Order.status == "entregue"
        ).all()
        total = sum(o.total for o in orders)
        return {"total_pedidos": len(orders), "faturamento": total, "ticket_medio": total / len(orders) if orders else 0}
 
    atual = get_mes_data(mes_atual, ano_atual)
    anterior = get_mes_data(mes_anterior, ano_anterior)
    if anterior["faturamento"] > 0:
        variacao = ((atual["faturamento"] - anterior["faturamento"]) / anterior["faturamento"]) * 100
    else:
        variacao = 100 if atual["faturamento"] > 0 else 0
 
    vendas_por_dia = []
    for dia in range(1, hoje.day + 1):
        orders_dia = db.query(Order).filter(
            Order.restaurant_id == restaurant_id,
            extract('day', Order.created_at) == dia,
            extract('month', Order.created_at) == mes_atual,
            extract('year', Order.created_at) == ano_atual,
            Order.status == "entregue"
        ).all()
        vendas_por_dia.append({"dia": dia, "faturamento": sum(o.total for o in orders_dia), "pedidos": len(orders_dia)})
 
    return {
        "mes_atual": {"nome": hoje.strftime("%B/%Y"), **atual},
        "mes_anterior": {"nome": date(ano_anterior, mes_anterior, 1).strftime("%B/%Y"), **anterior},
        "variacao_percentual": round(variacao, 1),
        "vendas_por_dia": vendas_por_dia
    }
 
@router.get("/restaurant/{restaurant_id}/top-products")
def get_top_products(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    results = (
        db.query(OrderItem.product_id, func.sum(OrderItem.quantity).label("total_qty"), func.sum(OrderItem.quantity * OrderItem.unit_price).label("total_revenue"))
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.restaurant_id == restaurant_id)
        .group_by(OrderItem.product_id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5).all()
    )
    top = []
    for r in results:
        prod = db.query(Product).filter(Product.id == r.product_id).first()
        top.append({"product_id": r.product_id, "name": prod.name if prod else f"Produto #{r.product_id}", "total_qty": r.total_qty, "total_revenue": float(r.total_revenue)})
    return top
 
@router.get("/restaurant/{restaurant_id}/orders/history")
def get_history(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    orders = db.query(Order).filter(Order.restaurant_id == restaurant_id).order_by(Order.created_at.desc()).limit(50).all()
    return [{"id": o.id, "status": o.status, "total": o.total, "user_id": o.user_id, "table_number": o.table_number, "payment_method": o.payment_method, "created_at": o.created_at.isoformat(), "items_count": len(o.items)} for o in orders]
 
@router.get("/restaurant/{restaurant_id}/team")
def get_team(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    users = db.query(User).filter(User.restaurant_id == restaurant_id, User.role != "admin").all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
 
@router.get("/restaurant/{restaurant_id}/info")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    return {"id": r.id, "name": r.name, "active": r.active}
 
@router.put("/restaurant/{restaurant_id}/info")
def update_restaurant(restaurant_id: int, data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if data.get("name"):
        r.name = data["name"]
    db.commit()
    return {"message": "Restaurante atualizado"}

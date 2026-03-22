from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
 
from app.database.connection import engine, SessionLocal
from app.models.base import Base
 
from app.models import restaurant
from app.models import user
from app.models import product
from app.models import order
from app.models import table
from app.models.user import User
from app.core.security import hash_password
 
from app.routes import auth_routes
from app.routes import product_routes
from app.routes import order_routes
from app.routes import restaurant_routes
from app.routes import dashboard_routes
from app.routes import table_routes
 
app = FastAPI(title="OrderStack API")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
 
Base.metadata.create_all(bind=engine)
 
def criar_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "admin@orderstack.com").first()
        if not existing:
            admin = User(
                name="Admin",
                email="admin@orderstack.com",
                password=hash_password("admin123"),
                role="admin",
                restaurant_id=None
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()
 
criar_admin()
 
app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(order_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(table_routes.router)
 
@app.get("/")
def home():
    return FileResponse("orderstack.html")
 
@app.get("/os-admin-x9k2m7")
def admin_panel():
    return FileResponse("admin.html")
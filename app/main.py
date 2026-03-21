from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.database.connection import engine
from app.models.base import Base

from app.models import restaurant
from app.models import user
from app.models import product
from app.models import order

from app.routes import auth_routes
from app.routes import product_routes
from app.routes import order_routes
from app.routes import restaurant_routes
from app.routes import dashboard_routes

app = FastAPI(title="OrderStack API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(order_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(dashboard_routes.router)

@app.get("/frontend")
def frontend():
    return FileResponse("orderstack.html")

@app.get("/")
def home():
    return {"message": "OrderStack API rodando!"}

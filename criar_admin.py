from app.models.base import Base
from app.models import restaurant, user, product, order
from app.database.connection import engine, SessionLocal
from app.models.user import User
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()
existing = db.query(User).filter(User.email == "admin@orderstack.com").first()
if existing:
    print("Admin ja existe")
else:
    admin = User(
        name="Admin",
        email="admin@orderstack.com",
        password=hash_password("admin123"),
        role="admin",
        restaurant_id=None
    )
    db.add(admin)
    db.commit()
    print("Admin criado com sucesso")
db.close()

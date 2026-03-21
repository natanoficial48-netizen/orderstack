from fastapi import Depends, HTTPException, Header
from app.core.security import decode_token
from typing import Optional

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token nao fornecido")
    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")

def require_role(*roles):
    def checker(user=Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return user
    return checker

def require_same_restaurant(restaurant_id: int, user=Depends(get_current_user)):
    if user.get("role") == "admin":
        return user
    if user.get("restaurant_id") != restaurant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user

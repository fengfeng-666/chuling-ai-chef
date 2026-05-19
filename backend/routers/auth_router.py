from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models import User
from auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api")


class RegisterBody(BaseModel):
    username: str
    password: str


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    if len(body.username) < 2 or len(body.username) > 50:
        raise HTTPException(status_code=400, detail="用户名长度需在 2-50 位之间")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")

    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "token": create_token(user.id),
        "user": {"id": user.id, "username": user.username},
    }


@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    return {
        "success": True,
        "token": create_token(user.id),
        "user": {"id": user.id, "username": user.username},
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "success": True,
        "user": {"id": user.id, "username": user.username},
    }

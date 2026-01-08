import uuid
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import UserCreate, UserLogin, UserResponse, Token
from app.db import fake_users_db

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user_id = str(uuid.uuid4())
    fake_users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "hashed_password": get_password_hash(user.password),
    }
    return {"username": user.username}


@router.post("/login", response_model=Token)
def login(user: UserLogin):
    db_user = fake_users_db.get(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    access_token = create_access_token(
        user_id=db_user["id"],
        username=user.username,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer", "user": {"username": user.username}}

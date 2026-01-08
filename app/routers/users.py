from fastapi import APIRouter, Depends
from app.core.security import get_current_user, require_role
from app.models.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}


@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"你好, {current_user['username']}! 这是受保护的路由"}


@router.get("/admin")
def admin_route(current_user: dict = Depends(require_role(["admin"]))):
    return {"message": f"你好管理员 {current_user['username']}!"}

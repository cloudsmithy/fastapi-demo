from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials
from app.core.config import settings
import json

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)
basic_scheme = HTTPBasic(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user_id: str, username: str, expires_delta: Optional[timedelta] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=15))
    to_encode = {
        "sub": user_id,           # 唯一ID
        "username": username,      # 用户名
        "iss": settings.ISSUER,   # 签发者
        "iat": now,               # 签发时间
        "exp": expire,            # 过期时间
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def parse_request_context(request: Request) -> Optional[dict]:
    """解析 x-amzn-request-context header"""
    if ctx := request.headers.get("x-amzn-request-context"):
        try:
            return json.loads(ctx)
        except:
            pass
    return None


def get_lambda_context(request: Request) -> dict:
    """从请求头获取 Lambda 上下文信息"""
    lambda_ctx = request.headers.get("x-amzn-lambda-context")
    
    result = {
        "lambda_context": None,
        "request_context": None,
        "cognito_identity": None,
    }
    
    if lambda_ctx:
        try:
            result["lambda_context"] = json.loads(lambda_ctx)
        except:
            pass
    
    if ctx := parse_request_context(request):
        result["request_context"] = ctx
        result["cognito_identity"] = ctx.get("identity", {})
    
    return result


def get_current_user(
    bearer_credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    basic_credentials: HTTPBasicCredentials = Depends(basic_scheme),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 方式1: Bearer Token (JWT)
    if bearer_credentials:
        try:
            payload = jwt.decode(
                bearer_credentials.credentials,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"require": ["sub", "exp", "iss"]},
                issuer=settings.ISSUER,
            )
            return {"user_id": payload.get("sub"), "username": payload.get("username"), "role": payload.get("role", "user")}
        except JWTError:
            pass
    
    # 方式2: Basic Auth (用户名密码)
    if basic_credentials:
        from app.db import fake_users_db
        user = fake_users_db.get(basic_credentials.username)
        if user and verify_password(basic_credentials.password, user["hashed_password"]):
            return {"user_id": user["id"], "username": basic_credentials.username, "role": user.get("role", "user")}
    
    raise credentials_exception


def require_role(allowed_roles: list):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return current_user
    return role_checker

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.security import get_lambda_context, parse_request_context
from app.routers import auth, form, users

app = FastAPI(
    title="FastAPI Demo",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改成具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_root_path(request: Request) -> str:
    """根据请求动态计算 root_path，仅 API Gateway 默认域名需要 stage 前缀"""
    if ctx := parse_request_context(request):
        stage = ctx.get("stage")
        domain = ctx.get("domainName", "")
        if stage and stage != "$default" and "execute-api" in domain:
            return f"/{stage}"
    return ""


@app.middleware("http")
async def set_root_path(request: Request, call_next):
    if root_path := get_root_path(request):
        request.scope["root_path"] = root_path
    # 清除 OpenAPI schema 缓存，让 FastAPI 根据当前 root_path 重新生成
    app.openapi_schema = None
    return await call_next(request)


# Routers
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户"])
app.include_router(form.router, prefix="/form", tags=["表单"])


@app.get("/")
def root(request: Request, lambda_ctx: dict = Depends(get_lambda_context)):
    return {
        "message": "Welcome to FastAPI",
        "headers": dict(request.headers),
        "lambda_context": lambda_ctx["lambda_context"],
        "request_context": lambda_ctx["request_context"],
        "cognito_identity": lambda_ctx["cognito_identity"],
    }


@app.get("/health")
def health_check(lambda_ctx: dict = Depends(get_lambda_context)):
    ctx = lambda_ctx.get("lambda_context") or {}
    return {
        "status": "healthy",
        "function_name": ctx.get("env_config", {}).get("function_name"),
    }

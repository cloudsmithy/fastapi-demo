from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Depends
from app.routers import auth, users, form
from app.core.security import get_lambda_context, parse_request_context

app = FastAPI(
    title="FastAPI Demo",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.middleware("http")
async def set_root_path(request: Request, call_next):
    if ctx := parse_request_context(request):
        if stage := ctx.get("stage"):
            request.scope["root_path"] = f"/{stage}"
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境改成具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "status": "healthy",
        "function_name": lambda_ctx["lambda_context"].get("env_config", {}).get("function_name") if lambda_ctx["lambda_context"] else None,
    }

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, form

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

app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户"])
app.include_router(form.router, prefix="/form", tags=["表单"])


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

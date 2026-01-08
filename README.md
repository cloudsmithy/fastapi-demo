# FastAPI Demo

带 JWT 认证和角色权限的 FastAPI 项目。

## 功能

- 用户注册/登录
- JWT + Basic Auth 双认证方式
- 角色权限控制 (user/admin)
- Swagger 文档自动生成

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 修改 SECRET_KEY

# 启动服务
uvicorn app.main:app --reload
# 或
fastapi dev app/main.py
```

访问 http://localhost:8000/docs 查看 API 文档。

## API 端点

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /auth/register | 注册 | 否 |
| POST | /auth/login | 登录 | 否 |
| GET | /users/me | 当前用户信息 | 是 |
| GET | /users/protected | 受保护路由 | 是 |
| GET | /users/admin | 管理员路由 | admin |

## Docker

```bash
# 构建
docker build -t fastapi-demo .

# 运行
docker run -p 8000:8000 -e SECRET_KEY=your-secret fastapi-demo
```

## 推送到 ECR

```bash
# 1. 登录 ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# 2. 创建仓库（首次）
aws ecr create-repository --repository-name fastapi-demo

# 3. 打标签
docker tag fastapi-demo:latest <account-id>.dkr.ecr.<region>.amazonaws.com/fastapi-demo:latest

# 4. 推送
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/fastapi-demo:latest
```

## 项目结构

```
app/
├── main.py          # 入口
├── db.py            # 数据存储
├── core/
│   ├── config.py    # 配置
│   └── security.py  # 认证逻辑
├── models/
│   └── user.py      # 数据模型
└── routers/
    ├── auth.py      # 认证路由
    ├── users.py     # 用户路由
    └── form.py      # 表单示例
```

# TicketService

一个可运行的工单系统基础版本，包含：
- FastAPI 后端 API
- 独立 FastAPI 认证服务
- Kong API Gateway
- SQLite + SQLAlchemy 数据层
- Alembic 迁移骨架
- React + Vite 前端页面

## 目录

先在项目根目录创建共享虚拟环境，并安装后端相关依赖：
- `frontend`: 前端界面

python3 -m venv .venv
.venv/bin/python -m pip install -r ticket/requirements.txt -r auth_service/requirements.txt
```

启动 ticket 服务：

```bash
cd ticket
../.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

## 认证服务启动

认证服务独立运行在 `8002` 端口：

```bash
cd auth_service
../.venv/bin/python -m uvicorn app.main:app --reload --port 8002
```

## API Gateway

Kong 运行在 HTTPS `8443` 端口，前端应通过网关访问后端 API：

```bash
curl -k https://localhost:8443/api/health
curl -k https://localhost:8443/api/auth/health
```

本地开发证书在 `apigw/certs/kong.crt`，私钥在 `apigw/certs/kong.key`。这是开发用自签名证书，浏览器调用前需要信任该证书。

路由规则：

- `/api/auth/*` -> `auth_service`，转发时去掉 `/api/auth` 前缀
- `/api/ticket/*` -> `ticket`，转发时去掉 `/api/ticket` 前缀，并由 Kong 校验 JWT

认证流程：

1. 前端调用 `POST /api/auth/login`，使用用户名和密码换取 JWT。
2. JWT 默认 1 小时过期。
3. 前端访问 ticket/comment API 时发送 `Authorization: Bearer <token>`。
4. Kong 校验 JWT 签名和过期时间。
5. Kong 将用户信息传给后端请求头：`X-Authenticated-User-Id`、`X-Authenticated-Username`、`X-Authenticated-Phone-Number`、`X-Authenticated-Department`。

开发默认值在 `apigw/kong.yml`、`ticket/.env.example` 和 `auth_service/.env.example` 中保持一致。生产环境应替换 `JWT_SECRET` 和 `GATEWAY_SHARED_SECRET`。

Kong 的 Podman 启动命令见 `apigw/README.md`。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 默认 API

- `GET /health`
- `GET /api/health` via Kong
- `GET /api/auth/health` via Kong
- `POST /api/auth/register` via Kong
- `POST /api/auth/login` via Kong
- `GET /api/ticket/tickets` via Kong，需要 Bearer token
- `POST /api/ticket/tickets` via Kong，需要 Bearer token
- `GET /api/ticket/tickets/{ticket_id}` via Kong，需要 Bearer token
- `PATCH /api/ticket/tickets/{ticket_id}/status` via Kong，需要 Bearer token
- `GET /api/ticket/comments/ticket/{ticket_id}` via Kong，需要 Bearer token
- `POST /api/ticket/comments` via Kong，需要 Bearer token

## Alembic

```bash
cd ticket
../.venv/bin/python -m alembic upgrade head
```

说明：当前版本为了快速演示在 `app.main` 中也包含了 `Base.metadata.create_all`，后续建议只保留 Alembic 迁移路径。

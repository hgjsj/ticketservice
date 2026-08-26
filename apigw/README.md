# API Gateway

本目录保存 Kong Gateway 的 DB-less 配置。当前只把后端 API 放在网关后面，前端仍然通过 Vite 独立运行。

## 路由

- Gateway: `https://localhost:8443`
- Ticket API via gateway: `https://localhost:8443/api/ticket`
- Auth API via gateway: `https://localhost:8443/api/auth`
- Ticket service upstream: `http://host.containers.internal:8000`
- Auth service upstream: `http://host.containers.internal:8002`

示例：

```bash
curl -k https://localhost:8443/api/health
curl -k https://localhost:8443/api/ticket/tickets
curl -k https://localhost:8443/api/auth/health
```

`-k` 用于本地自签名证书测试。浏览器访问时需要信任 `apigw/certs/kong.crt`，否则浏览器会拦截前端对 HTTPS 网关的请求。

## 自签名证书

当前证书文件：

- `apigw/certs/kong.crt`
- `apigw/certs/kong.key`

重新生成本地证书：

```bash
openssl req -x509 -nodes -newkey rsa:2048 -sha256 -days 365 \
  -keyout apigw/certs/kong.key \
  -out apigw/certs/kong.crt \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

chmod 644 apigw/certs/kong.key
```

`chmod 644` 是为了让容器内的 Kong 进程能读取挂载进来的开发私钥。生产环境不要用这个自签名证书。

Kong 会转发：

- `/api/auth/register` -> auth service `/register`
- `/api/auth/login` -> auth service `/login`
- `/api/ticket/tickets` -> ticket service `/tickets`
- `/api/ticket/comments/...` -> ticket service `/comments/...`

## JWT 鉴权

`/api/auth/*` 不需要 token，用于注册和登录。

`/api/ticket/*` 的 ticket/comment API 会由 Kong 的 `jwt` 插件统一校验：

- JWT 使用 `HS256`
- JWT `iss` 必须是 `ticket-service-auth`
- JWT `exp` 必须有效，默认由 auth service 设置为 1 小时
- 开发默认签名密钥是 `change-me`

Kong 验证通过后，会把 JWT 中的用户信息传给后端：

- `X-Authenticated-User-Id`
- `X-Authenticated-Username`
- `X-Authenticated-Phone-Number`
- `X-Authenticated-Department`
- `X-Gateway-Secret`

生产环境应替换 `jwt_secrets.secret` 和 `X-Gateway-Secret` 的值，并同步到服务环境变量。

## 使用 Podman 启动 Kong

先确保 ticket service 运行在宿主机 `8000` 端口，auth service 运行在宿主机 `8002` 端口，然后执行：

```bash
podman run -d --name ticketservice-kong \
  -e KONG_DATABASE=off \
  -e KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml \
  -e KONG_PROXY_LISTEN="0.0.0.0:8443 ssl" \
  -e KONG_SSL_CERT=/kong/ssl/kong.crt \
  -e KONG_SSL_CERT_KEY=/kong/ssl/kong.key \
  -e KONG_PROXY_ACCESS_LOG=/dev/stdout \
  -e KONG_ADMIN_ACCESS_LOG=/dev/stdout \
  -e KONG_PROXY_ERROR_LOG=/dev/stderr \
  -e KONG_ADMIN_ERROR_LOG=/dev/stderr \
  -e KONG_ADMIN_LISTEN=0.0.0.0:8001 \
  -p 8443:8443 \
  -p 8001:8001 \
  -v "$PWD/apigw/kong.yml:/kong/declarative/kong.yml:Z" \
  -v "$PWD/apigw/certs/kong.crt:/kong/ssl/kong.crt:Z" \
  -v "$PWD/apigw/certs/kong.key:/kong/ssl/kong.key:Z" \
  docker.xuanyuan.run/kong/kong-gateway:3.8
```

停止并删除容器：

```bash
podman rm -f ticketservice-kong
```

# Ops

使用 Docker Compose 启动 EMQX 与后端（开发用途）。

## 启动

```powershell
cd ops
# Windows PowerShell
docker compose up
```

启动后：
- 后端: http://localhost:8000/health
- EMQX 控制台: http://localhost:18083 （默认账户/密码见官方文档）

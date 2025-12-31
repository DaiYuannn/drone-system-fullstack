# 运行指南（开发首跑）

## 1) 启动后端（本机）

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

若相对导入报错（作为包运行），可使用：

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir ..
```

打开 http://localhost:8000/health

## 2) 打开前端

- 编辑 `frontend/index.html`，将 `YOUR_MAPBOX_TOKEN` 替换为你的 token。
- 双击打开或用 VS Code Live Server 打开。
- 在控件中连接 `ws://localhost:8000/ws`，点击“发送 path.update”，应收到 ack。

## 3) （可选）Docker Compose 启动 EMQX 与后端

```powershell
cd ops
docker compose up
```

## 4) 运行测试

```powershell
# backend 测试
cd backend
.\.venv\Scripts\Activate.ps1
python -m unittest

# rc_host 协议测试
cd ..\rc_host
python -m unittest
```

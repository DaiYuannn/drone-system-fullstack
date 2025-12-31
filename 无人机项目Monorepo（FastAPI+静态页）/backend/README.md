# Backend (FastAPI)

最小可运行后端，提供：
- GET /health 健康检查
- POST /api/planning 直线路径占位实现
- WS /ws 简单回声与 path.update 确认

## 开发环境

Windows 下建议使用 Python 3.10+ 与 venv。

### 安装依赖

1) 建立并激活虚拟环境（PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 运行

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

如在包导入报错（相对导入）时，请使用：

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --app-dir ..
```

### 测试

```powershell
python -m unittest
```

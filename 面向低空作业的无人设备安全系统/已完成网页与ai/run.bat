@echo off
REM 启动后端服务
start "Drone Backend" cmd /k uvicorn main:app --reload
timeout /t 5 /nobreak >nul
REM 使用Chrome打开前端页面
REM start chrome "file:///%CD%/index.html"
REM 使用默认浏览器打开前端页面（兼容路径格式）
start "" "file:///%CD:\=/%/index.html"
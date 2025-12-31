@echo off
REM Windows无人机测试运行脚本

echo === Windows无人机定位系统测试 ===
echo 时间: %date% %time%

REM 检查是否在test环境中
if not defined CONDA_DEFAULT_ENV (
    echo 错误: 未检测到conda环境
    echo 请先激活test环境:
    echo   conda activate test
    echo 或运行环境激活脚本:
    echo   "%USERPROFILE%\drone_positioning_test\activate_test_env.bat"
    pause
    exit /b 1
)

if not "%CONDA_DEFAULT_ENV%"=="test" (
    echo 错误: 当前不在test环境中 ^(当前: %CONDA_DEFAULT_ENV%^)
    echo 请先激活test环境:
    echo   conda activate test
    pause
    exit /b 1
)

echo 当前环境: %CONDA_DEFAULT_ENV%

REM 设置项目目录
set PROJECT_DIR=%USERPROFILE%\drone_positioning_test

REM 检查项目目录是否存在
if not exist "%PROJECT_DIR%" (
    echo 错误: 项目目录不存在 %PROJECT_DIR%
    echo 请先运行环境部署脚本: setup_windows_test_env.bat
    pause
    exit /b 1
)

echo 项目目录: %PROJECT_DIR%

REM 加载环境变量
if exist "%PROJECT_DIR%\config\env_vars.bat" (
    echo 加载环境变量...
    call "%PROJECT_DIR%\config\env_vars.bat"
) else (
    echo 警告: 环境变量文件不存在
    echo 使用默认配置...
    set DRONE_SERVER_HOST=服务器IP
    set DRONE_SERVER_PORT=5000
    set DRONE_ID=test_drone_001_windows
)

echo.
echo 配置信息:
echo   服务器地址: %DRONE_SERVER_HOST%:%DRONE_SERVER_PORT%
echo   无人机ID: %DRONE_ID%
echo   项目目录: %PROJECT_DIR%

REM 切换到项目目录
cd /d "%PROJECT_DIR%"

REM 检查Python和依赖
echo.
echo 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python不可用
    pause
    exit /b 1
)

echo 检查依赖包...
python -c "import requests, PIL, numpy, qrcode, socketio; print('所有依赖包检查通过')" 2>nul
if %errorlevel% neq 0 (
    echo 警告: 部分依赖包可能缺失
    echo 尝试安装缺失的包...
    pip install requests pillow numpy qrcode[pil] python-socketio[client]
)

REM 检查服务器连接
echo.
echo 检查服务器连接...
python -c "import requests; response = requests.get('http://%DRONE_SERVER_HOST%:%DRONE_SERVER_PORT%/api/health', timeout=5); print(f'服务器连接成功: {response.status_code}') if response.status_code == 200 else print(f'服务器响应异常: {response.status_code}')" 2>nul
if %errorlevel% neq 0 (
    echo 错误: 服务器连接失败
    echo 请检查:
    echo   1. 服务器是否运行在 %DRONE_SERVER_HOST%:%DRONE_SERVER_PORT%
    echo   2. 网络连接是否正常
    echo   3. 防火墙设置是否正确
    echo.
    echo 是否继续运行测试？^(y/n^)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo 测试取消
        pause
        exit /b 1
    )
)

echo.
echo === 开始运行测试 ===
echo.

REM 将测试脚本复制到项目目录
if exist "%~dp0test_upload_windows.py" (
    copy "%~dp0test_upload_windows.py" "%PROJECT_DIR%\" >nul
    echo 测试脚本已复制到项目目录
)

REM 运行测试脚本
python test_upload_windows.py

REM 保存退出代码
set test_result=%errorlevel%

echo.
echo === 测试完成 ===

REM 显示结果
if %test_result% equ 0 (
    echo 结果: 测试成功
    echo 报告: %PROJECT_DIR%\logs\windows_test_report.json
    echo Web: http://%DRONE_SERVER_HOST%:%DRONE_SERVER_PORT%
) else (
    echo 结果: 测试失败 ^(退出代码: %test_result%^
    echo 日志: %PROJECT_DIR%\logs\drone_test.log
)

echo.
echo 按任意键退出...
pause >nul

exit /b %test_result%
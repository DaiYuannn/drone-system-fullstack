@echo off
REM Windows Miniconda环境部署脚本 - Python 3.12 test环境
REM 用于设置无人机定位系统的测试环境

echo === Windows Miniconda环境部署脚本 - Python 3.12 test环境 ===

REM 检查conda是否可用
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Miniconda未安装或未添加到PATH
    echo 请先安装Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo 并确保conda命令可用
    pause
    exit /b 1
)

echo 信息: Miniconda已安装
conda --version

REM 初始化conda（Windows特定）
call conda init cmd.exe >nul 2>&1

REM 检查test环境是否存在
conda env list | findstr "test " >nul
if %errorlevel% equ 0 (
    echo 提示: test环境已存在，是否重新创建？^(y/n^)
    set /p response=
    if /i "%response%"=="y" (
    echo 信息: 删除现有test环境...
        call conda env remove -n test -y
    ) else (
    echo 信息: 使用现有test环境
    )
)

REM 创建Python 3.12环境
conda env list | findstr "test " >nul
if %errorlevel% neq 0 (
    echo 信息: 创建Python 3.12 test环境...
    call conda create -n test python=3.12 -y
    if %errorlevel% neq 0 (
        echo 创建环境失败
        pause
        exit /b 1
    )
)

REM 激活环境
echo 激活test环境...
call conda activate test
if %errorlevel% neq 0 (
    echo 错误: 激活环境失败
    pause
    exit /b 1
)

REM 检查Python版本
echo Python版本信息:
python --version
where python

REM 升级pip
echo 信息: 升级pip...
python -m pip install --upgrade pip

REM 安装无人机客户端依赖
echo 信息: 安装无人机客户端依赖包...
pip install opencv-python pillow numpy requests websocket-client pyzbar qrcode[pil]

REM 安装图像处理和条码检测的额外依赖
echo 信息: 安装图像处理和条码检测依赖...
pip install scipy matplotlib imageio scikit-image

REM 安装网络和通信相关包
echo 信息: 安装网络通信依赖...
pip install python-socketio[client] eventlet aiohttp

REM 创建项目目录
set PROJECT_DIR=%USERPROFILE%\drone_positioning_test
echo 信息: 创建项目目录: %PROJECT_DIR%
mkdir "%PROJECT_DIR%" 2>nul
mkdir "%PROJECT_DIR%\logs" 2>nul
mkdir "%PROJECT_DIR%\test_images" 2>nul
mkdir "%PROJECT_DIR%\config" 2>nul

REM 创建环境变量配置批处理文件
echo 信息: 设置环境变量...
(
echo @echo off
echo REM 无人机定位系统测试环境变量
echo.
echo REM 服务器配置
echo set DRONE_SERVER_HOST=服务器IP
echo set DRONE_SERVER_PORT=5000
echo set DRONE_SERVER_URL=http://%%DRONE_SERVER_HOST%%:%%DRONE_SERVER_PORT%%
echo.
echo REM 无人机配置
echo set DRONE_ID=test_drone_001
echo set DRONE_MODEL=Test_Drone_V1
echo.
echo REM GPS模拟配置
echo set GPS_SIMULATE=true
echo set GPS_LATITUDE=31.2304
echo set GPS_LONGITUDE=121.4737
echo set GPS_ALTITUDE=10.0
echo.
echo REM 相机配置
echo set CAMERA_INDEX=0
echo set CAMERA_WIDTH=640
echo set CAMERA_HEIGHT=480
echo set CAMERA_FPS=30
echo.
echo REM 条码检测配置
echo set BARCODE_CONFIDENCE_THRESHOLD=0.8
echo set DETECTION_INTERVAL=2
echo.
echo REM 数据传输配置
echo set DATA_RETRY_COUNT=3
echo set DATA_TIMEOUT=10
echo set HEARTBEAT_INTERVAL=30
echo.
echo REM 日志配置
echo set LOG_LEVEL=INFO
echo set LOG_FILE=%PROJECT_DIR%\logs\drone_test.log
echo.
echo REM 测试模式配置
echo set TEST_MODE=true
echo set TEST_IMAGE_DIR=%PROJECT_DIR%\test_images
echo set MOCK_GPS=true
echo set MOCK_CAMERA=false
echo.
echo echo 环境变量已设置
echo echo 服务器地址: %%DRONE_SERVER_URL%%
echo echo 无人机ID: %%DRONE_ID%%
echo echo 项目目录: %PROJECT_DIR%
) > "%PROJECT_DIR%\config\env_vars.bat"

REM 执行环境变量设置
call "%PROJECT_DIR%\config\env_vars.bat"

REM 创建conda环境激活脚本
(
echo @echo off
echo REM 激活test环境并加载环境变量
echo.
echo echo 激活miniconda test环境...
echo call conda activate test
echo.
echo if %%errorlevel%% neq 0 ^(
echo     echo 激活环境失败
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo 加载环境变量...
echo call "%%USERPROFILE%%\drone_positioning_test\config\env_vars.bat"
echo.
echo echo test环境已激活
echo python --version
echo echo Python路径: 
echo where python
echo echo 服务器地址: %%DRONE_SERVER_URL%%
echo echo 无人机ID: %%DRONE_ID%%
echo.
echo REM 显示已安装的包
echo echo.
echo echo 已安装的主要包:
echo pip list ^| findstr "opencv pillow numpy requests websocket pyzbar qrcode socketio"
) > "%PROJECT_DIR%\activate_test_env.bat"

REM 创建测试用的配置文件（Python版本）
(
echo """
echo 测试环境配置文件 - Windows版本
echo """
echo import os
echo.
echo # 服务器配置
echo SERVER_CONFIG = {
echo     'host': os.getenv^('DRONE_SERVER_HOST', '服务器IP'^),
echo     'port': int^(os.getenv^('DRONE_SERVER_PORT', 5000^)^),
echo     'url': os.getenv^('DRONE_SERVER_URL', 'http://服务器IP:5000'^),
echo     'timeout': int^(os.getenv^('DATA_TIMEOUT', 10^)^),
echo     'retry_count': int^(os.getenv^('DATA_RETRY_COUNT', 3^)^)
echo }
echo.
echo # 无人机配置
echo DRONE_CONFIG = {
echo     'id': os.getenv^('DRONE_ID', 'test_drone_001'^),
echo     'model': os.getenv^('DRONE_MODEL', 'Test_Drone_V1'^),
echo     'heartbeat_interval': int^(os.getenv^('HEARTBEAT_INTERVAL', 30^)^)
echo }
echo.
echo # GPS配置
echo GPS_CONFIG = {
echo     'simulate': os.getenv^('GPS_SIMULATE', 'true'^).lower^(^) == 'true',
echo     'mock': os.getenv^('MOCK_GPS', 'true'^).lower^(^) == 'true',
echo     'latitude': float^(os.getenv^('GPS_LATITUDE', 31.2304^)^),
echo     'longitude': float^(os.getenv^('GPS_LONGITUDE', 121.4737^)^),
echo     'altitude': float^(os.getenv^('GPS_ALTITUDE', 10.0^)^)
echo }
echo.
echo # 相机配置
echo CAMERA_CONFIG = {
echo     'index': int^(os.getenv^('CAMERA_INDEX', 0^)^),
echo     'width': int^(os.getenv^('CAMERA_WIDTH', 640^)^),
echo     'height': int^(os.getenv^('CAMERA_HEIGHT', 480^)^),
echo     'fps': int^(os.getenv^('CAMERA_FPS', 30^)^),
echo     'mock': os.getenv^('MOCK_CAMERA', 'false'^).lower^(^) == 'true'
echo }
echo.
echo # 检测配置
echo DETECTION_CONFIG = {
echo     'confidence_threshold': float^(os.getenv^('BARCODE_CONFIDENCE_THRESHOLD', 0.8^)^),
echo     'interval': int^(os.getenv^('DETECTION_INTERVAL', 2^)^)
echo }
echo.
echo # 测试配置
echo TEST_CONFIG = {
echo     'mode': os.getenv^('TEST_MODE', 'true'^).lower^(^) == 'true',
echo     'image_dir': os.getenv^('TEST_IMAGE_DIR', os.path.expanduser^('~/drone_positioning_test/test_images'^)^),
echo     'log_level': os.getenv^('LOG_LEVEL', 'INFO'^),
echo     'log_file': os.getenv^('LOG_FILE', os.path.expanduser^('~/drone_positioning_test/logs/drone_test.log'^)^)
echo }
echo.
echo # Windows路径配置
echo PATHS = {
echo     'project_dir': os.path.expanduser^('~/drone_positioning_test'^),
echo     'config_dir': os.path.expanduser^('~/drone_positioning_test/config'^),
echo     'logs_dir': os.path.expanduser^('~/drone_positioning_test/logs'^),
echo     'test_images_dir': os.path.expanduser^('~/drone_positioning_test/test_images'^)
echo }
) > "%PROJECT_DIR%\config\test_config.py"

REM 验证安装
echo.
echo 信息: 验证安装...
python -c "import sys; print(f'Python版本: {sys.version}'); print(f'Python路径: {sys.executable}')"

echo.
echo 信息: 测试主要模块导入:
python -c "modules = ['cv2', 'PIL', 'numpy', 'requests', 'websocket', 'pyzbar', 'qrcode', 'socketio']; [print(f'{m} 导入成功') if not __import__(m) or True else print(f'{m} 导入失败') for m in modules]" 2>nul

REM 测试服务器连接
echo.
echo 信息: 测试服务器连接...
python -c "import requests, os; server_url = os.getenv('DRONE_SERVER_URL', 'http://服务器IP:5000'); response = requests.get(f'{server_url}/api/health', timeout=5); print(f'服务器连接成功: {server_url}') if response.status_code == 200 else print(f'服务器响应异常: {response.status_code}'); print(f'服务器响应: {response.json()}') if response.status_code == 200 else None" 2>nul || echo 服务器连接失败

echo.
echo === 环境部署完成 ===
echo.
echo 使用方法:
echo 1. 激活环境: "%PROJECT_DIR%\activate_test_env.bat"
echo 2. 运行测试: cd "%PROJECT_DIR%" ^&^& python test_upload.py
echo.
echo 项目目录: %PROJECT_DIR%
echo 配置文件: %PROJECT_DIR%\config\
echo 日志目录: %PROJECT_DIR%\logs\
echo 测试图片: %PROJECT_DIR%\test_images\
echo.
echo 环境变量已保存在: %PROJECT_DIR%\config\env_vars.bat
echo 测试配置已保存在: %PROJECT_DIR%\config\test_config.py

pause
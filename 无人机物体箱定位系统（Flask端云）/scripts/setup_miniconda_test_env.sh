#!/bin/bash
# Miniconda环境部署脚本 - Python 3.12 test环境
# 用于设置无人机定位系统的测试环境

set -e

echo "=== Miniconda环境部署脚本 - Python 3.12 test环境 ==="

# 检查miniconda是否已安装
if ! command -v conda &> /dev/null; then
    echo "错误: Miniconda未安装，请先安装Miniconda"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Miniconda已安装"
conda --version

# 初始化conda（如果需要）
eval "$(conda shell.bash hook)"

# 检查test环境是否存在
if conda env list | grep -q "^test "; then
    echo "提示: test环境已存在，是否重新创建？(y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "删除现有test环境..."
        conda env remove -n test -y
    else
        echo "使用现有test环境"
    fi
fi

# 创建Python 3.12环境
if ! conda env list | grep -q "^test "; then
    echo "创建Python 3.12 test环境..."
    conda create -n test python=3.12 -y
fi

# 激活环境
echo "激活test环境..."
conda activate test

# 检查Python版本
echo "Python版本信息:"
python --version
which python

# 安装基础依赖
echo "安装基础Python包..."
pip install --upgrade pip

# 安装无人机客户端依赖
echo "安装无人机客户端依赖包..."
pip install opencv-python pillow numpy requests websocket-client pyzbar qrcode[pil] gpspoller

# 安装用于图像处理和条码检测的额外依赖
echo "安装图像处理和条码检测依赖..."
pip install scipy matplotlib imageio scikit-image

# 安装网络和通信相关包
echo "安装网络通信依赖..."
pip install python-socketio[client] eventlet aiohttp

# 创建项目目录
PROJECT_DIR="$HOME/drone_positioning_test"
echo "创建项目目录: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/test_images"
mkdir -p "$PROJECT_DIR/config"

# 设置环境变量
echo "设置环境变量..."

# 创建环境变量配置文件
cat > "$PROJECT_DIR/config/env_vars.sh" << 'EOF'
#!/bin/bash
# 无人机定位系统测试环境变量

# 服务器配置
export DRONE_SERVER_HOST="服务器IP"
export DRONE_SERVER_PORT="5000"
export DRONE_SERVER_URL="http://${DRONE_SERVER_HOST}:${DRONE_SERVER_PORT}"

# 无人机配置
export DRONE_ID="test_drone_001"
export DRONE_MODEL="Test_Drone_V1"

# GPS模拟配置
export GPS_SIMULATE="true"
export GPS_LATITUDE="31.2304"    # 上海坐标
export GPS_LONGITUDE="121.4737"
export GPS_ALTITUDE="10.0"

# 相机配置
export CAMERA_INDEX="0"
export CAMERA_WIDTH="640"
export CAMERA_HEIGHT="480"
export CAMERA_FPS="30"

# 条码检测配置
export BARCODE_CONFIDENCE_THRESHOLD="0.8"
export DETECTION_INTERVAL="2"  # 检测间隔秒数

# 数据传输配置
export DATA_RETRY_COUNT="3"
export DATA_TIMEOUT="10"
export HEARTBEAT_INTERVAL="30"

# 日志配置
export LOG_LEVEL="INFO"
export LOG_FILE="$HOME/drone_positioning_test/logs/drone_test.log"

# 测试模式配置
export TEST_MODE="true"
export TEST_IMAGE_DIR="$HOME/drone_positioning_test/test_images"
export MOCK_GPS="true"
export MOCK_CAMERA="false"

echo "环境变量已设置"
echo "服务器地址: $DRONE_SERVER_URL"
echo "无人机ID: $DRONE_ID"
echo "项目目录: $HOME/drone_positioning_test"
EOF

# 使环境变量生效
chmod +x "$PROJECT_DIR/config/env_vars.sh"
source "$PROJECT_DIR/config/env_vars.sh"

# 创建conda环境激活脚本
cat > "$PROJECT_DIR/activate_test_env.sh" << 'EOF'
#!/bin/bash
# 激活test环境并加载环境变量

echo "激活miniconda test环境..."
eval "$(conda shell.bash hook)"
conda activate test

echo "加载环境变量..."
source "$HOME/drone_positioning_test/config/env_vars.sh"

echo "test环境已激活"
echo "Python版本: $(python --version)"
echo "Python路径: $(which python)"
echo "服务器地址: $DRONE_SERVER_URL"
echo "无人机ID: $DRONE_ID"

# 显示已安装的包
echo ""
echo "已安装的主要包:"
pip list | grep -E "(opencv|pillow|numpy|requests|websocket|pyzbar|qrcode|socketio)"
EOF

chmod +x "$PROJECT_DIR/activate_test_env.sh"

# 创建测试用的配置文件
cat > "$PROJECT_DIR/config/test_config.py" << 'EOF'
"""
测试环境配置文件
"""
import os

# 服务器配置
SERVER_CONFIG = {
    'host': os.getenv('DRONE_SERVER_HOST', '服务器IP'),
    'port': int(os.getenv('DRONE_SERVER_PORT', 5000)),
    'url': os.getenv('DRONE_SERVER_URL', 'http://服务器IP:5000'),
    'timeout': int(os.getenv('DATA_TIMEOUT', 10)),
    'retry_count': int(os.getenv('DATA_RETRY_COUNT', 3))
}

# 无人机配置
DRONE_CONFIG = {
    'id': os.getenv('DRONE_ID', 'test_drone_001'),
    'model': os.getenv('DRONE_MODEL', 'Test_Drone_V1'),
    'heartbeat_interval': int(os.getenv('HEARTBEAT_INTERVAL', 30))
}

# GPS配置
GPS_CONFIG = {
    'simulate': os.getenv('GPS_SIMULATE', 'true').lower() == 'true',
    'mock': os.getenv('MOCK_GPS', 'true').lower() == 'true',
    'latitude': float(os.getenv('GPS_LATITUDE', 31.2304)),
    'longitude': float(os.getenv('GPS_LONGITUDE', 121.4737)),
    'altitude': float(os.getenv('GPS_ALTITUDE', 10.0))
}

# 相机配置
CAMERA_CONFIG = {
    'index': int(os.getenv('CAMERA_INDEX', 0)),
    'width': int(os.getenv('CAMERA_WIDTH', 640)),
    'height': int(os.getenv('CAMERA_HEIGHT', 480)),
    'fps': int(os.getenv('CAMERA_FPS', 30)),
    'mock': os.getenv('MOCK_CAMERA', 'false').lower() == 'true'
}

# 检测配置
DETECTION_CONFIG = {
    'confidence_threshold': float(os.getenv('BARCODE_CONFIDENCE_THRESHOLD', 0.8)),
    'interval': int(os.getenv('DETECTION_INTERVAL', 2))
}

# 测试配置
TEST_CONFIG = {
    'mode': os.getenv('TEST_MODE', 'true').lower() == 'true',
    'image_dir': os.getenv('TEST_IMAGE_DIR', os.path.expanduser('~/drone_positioning_test/test_images')),
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': os.getenv('LOG_FILE', os.path.expanduser('~/drone_positioning_test/logs/drone_test.log'))
}

# 路径配置
PATHS = {
    'project_dir': os.path.expanduser('~/drone_positioning_test'),
    'config_dir': os.path.expanduser('~/drone_positioning_test/config'),
    'logs_dir': os.path.expanduser('~/drone_positioning_test/logs'),
    'test_images_dir': os.path.expanduser('~/drone_positioning_test/test_images')
}
EOF

# 验证安装
echo ""
echo "验证安装..."
python -c "
import sys
print(f'Python版本: {sys.version}')
print(f'Python路径: {sys.executable}')

# 测试主要模块导入
modules = ['cv2', 'PIL', 'numpy', 'requests', 'websocket', 'pyzbar', 'qrcode', 'socketio']
for module in modules:
    try:
        __import__(module)
    print(f'{module} 导入成功')
    except ImportError as e:
    print(f'{module} 导入失败: {e}')
"

# 测试服务器连接
echo ""
echo "测试服务器连接..."
python -c "
import requests
import os

server_url = os.getenv('DRONE_SERVER_URL', 'http://服务器IP:5000')
try:
    response = requests.get(f'{server_url}/api/health', timeout=5)
    if response.status_code == 200:
    print(f'服务器连接成功: {server_url}')
        print(f'服务器响应: {response.json()}')
    else:
    print(f'服务器响应异常: {response.status_code}')
except Exception as e:
    print(f'服务器连接失败: {e}')
"

echo ""
echo "=== 环境部署完成 ==="
echo ""
echo "使用方法:"
echo "1. 激活环境: source $PROJECT_DIR/activate_test_env.sh"
echo "2. 运行测试: cd $PROJECT_DIR && python test_upload.py"
echo ""
echo "项目目录: $PROJECT_DIR"
echo "配置文件: $PROJECT_DIR/config/"
echo "日志目录: $PROJECT_DIR/logs/"
echo "测试图片: $PROJECT_DIR/test_images/"
echo ""
echo "环境变量已保存在: $PROJECT_DIR/config/env_vars.sh"
echo "测试配置已保存在: $PROJECT_DIR/config/test_config.py"
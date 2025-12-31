#!/bin/bash
set -e
# 无人机物体箱定位系统 - Linux启动脚本

# 脚本路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVER_DIR="$PROJECT_ROOT/server_side"

# 配置文件
CONFIG_FILE="$SERVER_DIR/config.py"

# Python虚拟环境路径（可以根据需要修改）
VENV_PATH="/opt/drone_positioning/venv"

# 日志文件
LOG_FILE="/var/log/drone_positioning/startup.log"

# 创建日志目录
sudo mkdir -p /var/log/drone_positioning
sudo mkdir -p /var/lib/drone_positioning

# 函数：打印带时间戳的日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | sudo tee -a "$LOG_FILE"
}

# 函数：检查命令是否成功
check_success() {
    if [ $? -eq 0 ]; then
        log "SUCCESS: $1"
    else
        log "ERROR: $1 失败"
        exit 1
    fi
}

log "=== 开始启动无人机物体箱定位系统 ==="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    log "ERROR: Python3 未安装，请先安装 Python3"
    exit 1
fi

# 检查是否存在虚拟环境，如果不存在则创建
if [ ! -d "$VENV_PATH" ]; then
    log "创建Python虚拟环境: $VENV_PATH"
    sudo python3 -m venv "$VENV_PATH"
    check_success "Python虚拟环境创建"
    
    # 升级pip
    sudo "$VENV_PATH/bin/pip" install --upgrade pip
    check_success "pip升级"
fi

# 激活虚拟环境
log "激活Python虚拟环境"
source "$VENV_PATH/bin/activate"
check_success "虚拟环境激活"

# 读取环境变量文件（如果存在）
if [ -f "/etc/drone_positioning/env" ]; then
    log "加载环境变量 /etc/drone_positioning/env"
    # shellcheck disable=SC1091
    source "/etc/drone_positioning/env"
fi

# 安装依赖
log "安装Python依赖包"
cd "$SERVER_DIR"
pip install -r requirements.txt
check_success "依赖包安装"

# 设置权限
log "设置文件权限"
sudo chown -R $USER:$USER /var/lib/drone_positioning
sudo chmod -R 755 /var/lib/drone_positioning
sudo chown -R $USER:$USER /var/log/drone_positioning
sudo chmod -R 755 /var/log/drone_positioning

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 启动应用
log "启动Flask应用"
cd "$SERVER_DIR"
log "使用Python解释器: $(which python)"
python app.py &

# 获取进程ID
APP_PID=$!
log "应用已启动，进程ID: $APP_PID"

# 保存PID到文件
echo $APP_PID | sudo tee /var/run/drone_positioning.pid

log "=== 系统启动完成 ==="
log "Web界面访问地址: http://localhost:5000"
log "API接口地址: http://localhost:5000/api/"
log "进程ID文件: /var/run/drone_positioning.pid"
log "日志文件: /var/log/drone_positioning/"

# 等待应用启动
sleep 5

# 检查应用是否正常运行
if ps -p $APP_PID > /dev/null; then
    log "应用运行正常"
    
    # 测试HTTP接口
    if curl -s http://localhost:5000/api/health > /dev/null; then
        log "HTTP接口测试成功"
    else
        log "WARNING: HTTP接口测试失败"
    fi
    # 端口监听检查
    if command -v ss &> /dev/null; then
        ss -tlnp | grep :5000 >/dev/null && log "端口5000监听正常" || log "WARNING: 端口5000未监听"
    else
        netstat -tlnp | grep :5000 >/dev/null && log "端口5000监听正常" || log "WARNING: 端口5000未监听（建议安装 iproute2 提供 ss）"
    fi
else
    log "ERROR: 应用启动失败"
    exit 1
fi
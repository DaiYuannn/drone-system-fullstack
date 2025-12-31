#!/bin/bash
# 无人机物体箱定位系统 - Linux系统安装脚本

set -e  # 遇到错误立即退出

# 配置变量
PROJECT_NAME="drone-positioning"
INSTALL_DIR="/opt/drone_positioning"
VENV_PATH="$INSTALL_DIR/venv"
SERVICE_NAME="drone-positioning"
USER_NAME="drone"
GROUP_NAME="drone"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的日志
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查命令是否成功
check_success() {
    if [ $? -eq 0 ]; then
        log_success "$1"
    else
        log_error "$1 失败"
        exit 1
    fi
}

# 函数：检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此脚本: sudo $0"
        exit 1
    fi
}

# 函数：检测Linux发行版
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    log_info "检测到操作系统: $OS $VERSION"
}

# 函数：安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖包..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y python3 python3-pip python3-venv python3-dev \
                          build-essential curl wget git \
                          sqlite3 libsqlite3-dev \
                          nginx supervisor
        check_success "系统依赖包安装"
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum install -y python3 python3-pip python3-devel \
                      gcc gcc-c++ make curl wget git \
                      sqlite sqlite-devel \
                      nginx supervisor
        check_success "系统依赖包安装"
        
    elif command -v dnf &> /dev/null; then
        # Fedora
        dnf update -y
        dnf install -y python3 python3-pip python3-devel \
                      gcc gcc-c++ make curl wget git \
                      sqlite sqlite-devel \
                      nginx supervisor
        check_success "系统依赖包安装"
        
    else
        log_error "不支持的包管理器，请手动安装依赖"
        exit 1
    fi
}

# 函数：创建系统用户
create_user() {
    log_info "创建系统用户和组..."
    
    # 创建组
    if ! getent group "$GROUP_NAME" &> /dev/null; then
        groupadd "$GROUP_NAME"
        log_success "创建组: $GROUP_NAME"
    else
        log_info "组已存在: $GROUP_NAME"
    fi
    
    # 创建用户
    if ! getent passwd "$USER_NAME" &> /dev/null; then
        useradd -r -g "$GROUP_NAME" -d "$INSTALL_DIR" -s /bin/bash "$USER_NAME"
        log_success "创建用户: $USER_NAME"
    else
        log_info "用户已存在: $USER_NAME"
    fi
}

# 函数：创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    # 创建主要目录
    mkdir -p "$INSTALL_DIR"
    mkdir -p /var/lib/drone_positioning
    mkdir -p /var/log/drone_positioning
    mkdir -p /etc/drone_positioning
    
    # 复制项目文件（从仓库根目录）
    log_info "复制项目文件到 $INSTALL_DIR"
    cp -r "$PROJECT_ROOT/server_side/"* "$INSTALL_DIR/"
    cp -r "$PROJECT_ROOT/drone_side" "$INSTALL_DIR/"
    # 可选：创建应用日志目录，兼容当前配置
    mkdir -p "$INSTALL_DIR/logs"
    
    # 设置权限
    chown -R "$USER_NAME:$GROUP_NAME" "$INSTALL_DIR"
    chown -R "$USER_NAME:$GROUP_NAME" /var/lib/drone_positioning
    chown -R "$USER_NAME:$GROUP_NAME" /var/log/drone_positioning
    
    chmod -R 755 "$INSTALL_DIR"
    chmod -R 755 /var/lib/drone_positioning
    chmod -R 755 /var/log/drone_positioning
    
    log_success "目录结构创建完成"

    # 创建环境变量文件（若不存在）
    if [ ! -f /etc/drone_positioning/env ]; then
        cat > /etc/drone_positioning/env << 'EOF'
# 环境变量配置（被 systemd 和启动脚本读取）
# 设置管理端口令牌以启用 /api/admin/* 管理端点
# 使用前请用安全的随机字符串替换以下示例
ADMIN_TOKEN=
EOF
        chown $USER_NAME:$GROUP_NAME /etc/drone_positioning/env || true
        chmod 640 /etc/drone_positioning/env || true
        log_info "已创建 /etc/drone_positioning/env（请设置 ADMIN_TOKEN）"
    fi
}

# 函数：设置Python虚拟环境
setup_python_environment() {
    log_info "设置Python虚拟环境..."
    
    # 创建虚拟环境
    python3 -m venv "$VENV_PATH"
    check_success "Python虚拟环境创建"
    
    # 激活虚拟环境并安装依赖
    source "$VENV_PATH/bin/activate"
    
    # 升级pip
    pip install --upgrade pip
    check_success "pip升级"
    
    # 安装项目依赖
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        pip install -r "$INSTALL_DIR/requirements.txt"
        check_success "项目依赖安装"
    else
        log_warning "未找到requirements.txt文件"
    fi
    
    # 设置虚拟环境权限
    chown -R "$USER_NAME:$GROUP_NAME" "$VENV_PATH"
}

# 函数：安装systemd服务
install_systemd_service() {
    log_info "安装systemd服务..."
    
    # 复制服务文件
    if [ -f "$SCRIPT_DIR/drone-positioning.service" ]; then
        cp "$SCRIPT_DIR/drone-positioning.service" /etc/systemd/system/
        check_success "服务文件复制"
    else
        log_error "服务文件不存在: drone-positioning.service"
        exit 1
    fi
    
    # 重新加载systemd
    systemctl daemon-reload
    check_success "systemd重新加载"
    
    # 启用服务
    systemctl enable "$SERVICE_NAME"
    check_success "服务启用"
}

# 函数：配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW
        ufw allow 5000/tcp
        log_success "UFW防火墙规则添加"
        
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --reload
        log_success "firewalld防火墙规则添加"
        
    else
        log_warning "未检测到防火墙管理工具，请手动开放端口5000"
    fi
}

# 函数：初始化数据库
initialize_database() {
    log_info "初始化数据库..."
    
    # 切换到项目用户执行
    sudo -u "$USER_NAME" bash << EOF
    cd "$INSTALL_DIR"
    source "$VENV_PATH/bin/activate"
    python -c "
from database import DatabaseManager
db = DatabaseManager()
if db.connect():
    if db.create_tables():
        print('数据库初始化成功')
    else:
        print('数据库表创建失败')
        exit(1)
else:
    print('数据库连接失败')
    exit(1)
"
EOF
    
    check_success "数据库初始化"
}

# 函数：创建便捷脚本
create_convenience_scripts() {
    log_info "创建便捷管理脚本..."
    
    # 创建启动脚本
    cat > /usr/local/bin/drone-start << 'EOF'
#!/bin/bash
systemctl start drone-positioning
echo "无人机定位系统已启动"
systemctl status drone-positioning --no-pager
EOF
    
    # 创建停止脚本
    cat > /usr/local/bin/drone-stop << 'EOF'
#!/bin/bash
systemctl stop drone-positioning
echo "无人机定位系统已停止"
EOF
    
    # 创建重启脚本
    cat > /usr/local/bin/drone-restart << 'EOF'
#!/bin/bash
systemctl restart drone-positioning
echo "无人机定位系统已重启"
systemctl status drone-positioning --no-pager
EOF
    
    # 创建状态检查脚本
    cat > /usr/local/bin/drone-status << 'EOF'
#!/bin/bash
echo "=== 服务状态 ==="
systemctl status drone-positioning --no-pager
echo ""
echo "=== 端口监听 ==="
netstat -tlnp | grep :5000 || echo "端口5000未监听"
echo ""
echo "=== 最近日志 ==="
journalctl -u drone-positioning --no-pager -n 10
EOF
    
    # 设置执行权限
    chmod +x /usr/local/bin/drone-*
    
    log_success "便捷管理脚本创建完成"
}

# 主安装流程
main() {
    log_info "开始安装无人机物体箱定位系统..."
    
    # 检查权限
    check_root
    
    # 检测操作系统
    detect_os
    
    # 安装系统依赖
    install_system_dependencies
    
    # 创建用户
    create_user
    
    # 创建目录结构
    create_directories
    
    # 设置Python环境
    setup_python_environment
    
    # 安装systemd服务
    install_systemd_service
    
    # 配置防火墙
    configure_firewall
    
    # 初始化数据库
    initialize_database
    
    # 创建便捷脚本
    create_convenience_scripts
    
    log_success "安装完成！"
    
    echo ""
    echo "=== 安装信息 ==="
    echo "安装目录: $INSTALL_DIR"
    echo "服务名称: $SERVICE_NAME"
    echo "用户/组: $USER_NAME:$GROUP_NAME"
    echo "数据目录: /var/lib/drone_positioning"
    echo "日志目录: /var/log/drone_positioning"
    echo ""
    echo "=== 管理命令 ==="
    echo "启动服务: drone-start 或 systemctl start $SERVICE_NAME"
    echo "停止服务: drone-stop 或 systemctl stop $SERVICE_NAME"
    echo "重启服务: drone-restart 或 systemctl restart $SERVICE_NAME"
    echo "查看状态: drone-status 或 systemctl status $SERVICE_NAME"
    echo "查看日志: journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "=== 访问地址 ==="
    echo "Web界面: http://localhost:5000"
    echo "API接口: http://localhost:5000/api/"
    echo ""
    
    log_info "正在启动服务..."
    systemctl start "$SERVICE_NAME"
    
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "服务启动成功！"
        echo ""
        echo "安装和启动完成，系统已准备就绪！"
    else
        log_error "服务启动失败，请检查日志: journalctl -u $SERVICE_NAME"
        exit 1
    fi
}

# 运行主函数
main "$@"
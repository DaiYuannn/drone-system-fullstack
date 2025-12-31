#!/bin/bash
# 无人机物体箱定位系统 - 部署管理脚本

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "无人机物体箱定位系统 - 部署管理脚本"
    echo ""
    echo "用法:"
    echo "  $0 install     - 安装系统到Linux服务器"
    echo "  $0 start       - 启动服务"
    echo "  $0 stop        - 停止服务"
    echo "  $0 restart     - 重启服务"
    echo "  $0 status      - 查看服务状态"
    echo "  $0 logs        - 查看服务日志"
    echo "  $0 uninstall   - 卸载系统"
    echo "  $0 help        - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 install     # 全新安装系统"
    echo "  $0 start       # 启动服务"
    echo "  $0 status      # 检查运行状态"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[错误]${NC} 需要root权限，请使用: sudo $0 $1"
        exit 1
    fi
}

# 安装系统
install_system() {
    echo -e "${BLUE}[信息]${NC} 开始安装无人机物体箱定位系统..."
    
    if [ ! -f "$SCRIPT_DIR/install_linux.sh" ]; then
        echo -e "${RED}[错误]${NC} 安装脚本不存在: install_linux.sh"
        exit 1
    fi
    
    chmod +x "$SCRIPT_DIR/install_linux.sh"
    "$SCRIPT_DIR/install_linux.sh"
}

# 启动服务
start_service() {
    echo -e "${BLUE}[信息]${NC} 启动无人机定位系统服务..."
    
    if command -v drone-start &> /dev/null; then
        drone-start
    elif systemctl list-unit-files | grep -q drone-positioning; then
        systemctl start drone-positioning
        echo -e "${GREEN}[成功]${NC} 服务已启动"
    else
        echo -e "${YELLOW}[警告]${NC} 系统尚未安装，请先运行: $0 install"
        exit 1
    fi
}

# 停止服务
stop_service() {
    echo -e "${BLUE}[信息]${NC} 停止无人机定位系统服务..."
    
    if command -v drone-stop &> /dev/null; then
        drone-stop
    elif systemctl list-unit-files | grep -q drone-positioning; then
        systemctl stop drone-positioning
        echo -e "${GREEN}[成功]${NC} 服务已停止"
    else
        echo -e "${YELLOW}[警告]${NC} 系统尚未安装"
        exit 1
    fi
}

# 重启服务
restart_service() {
    echo -e "${BLUE}[信息]${NC} 重启无人机定位系统服务..."
    
    if command -v drone-restart &> /dev/null; then
        drone-restart
    elif systemctl list-unit-files | grep -q drone-positioning; then
        systemctl restart drone-positioning
        echo -e "${GREEN}[成功]${NC} 服务已重启"
    else
        echo -e "${YELLOW}[警告]${NC} 系统尚未安装，请先运行: $0 install"
        exit 1
    fi
}

# 查看服务状态
show_status() {
    echo -e "${BLUE}[信息]${NC} 查看无人机定位系统状态..."
    
    if command -v drone-status &> /dev/null; then
        drone-status
    elif systemctl list-unit-files | grep -q drone-positioning; then
        systemctl status drone-positioning --no-pager
        echo ""
        echo -e "${BLUE}[信息]${NC} 端口监听状态:"
        if command -v ss &> /dev/null; then
            ss -tlnp | grep :5000 || echo "端口5000未监听"
        else
            netstat -tlnp | grep :5000 || echo "端口5000未监听（建议安装 iproute2 以使用 ss）"
        fi
    else
        echo -e "${YELLOW}[警告]${NC} 系统尚未安装"
        echo "要安装系统，请运行: $0 install"
    fi
}

# 查看日志
show_logs() {
    echo -e "${BLUE}[信息]${NC} 查看无人机定位系统日志..."
    
    if systemctl list-unit-files | grep -q drone-positioning; then
        echo "实时日志 (按 Ctrl+C 退出):"
        journalctl -u drone-positioning -f
    else
        echo -e "${YELLOW}[警告]${NC} 系统尚未安装"
        exit 1
    fi
}

# 卸载系统
uninstall_system() {
    echo -e "${YELLOW}[警告]${NC} 即将卸载无人机物体箱定位系统"
    echo -e "${RED}[注意]${NC} 这将删除所有数据和配置文件！"
    echo ""
    read -p "确认卸载? (输入 'yes' 确认): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "取消卸载"
        exit 0
    fi
    
    echo -e "${BLUE}[信息]${NC} 开始卸载系统..."
    
    # 停止服务
    if systemctl list-unit-files | grep -q drone-positioning; then
        systemctl stop drone-positioning 2>/dev/null
        systemctl disable drone-positioning 2>/dev/null
        rm -f /etc/systemd/system/drone-positioning.service
        systemctl daemon-reload
    fi
    
    # 删除文件
    rm -rf /opt/drone_positioning
    rm -rf /var/lib/drone_positioning
    rm -rf /var/log/drone_positioning
    rm -f /usr/local/bin/drone-*
    
    # 删除用户（可选）
    if getent passwd drone &> /dev/null; then
        userdel drone 2>/dev/null
    fi
    
    if getent group drone &> /dev/null; then
        groupdel drone 2>/dev/null
    fi
    
    echo -e "${GREEN}[成功]${NC} 系统卸载完成"
}

# 主函数
main() {
    case "${1:-help}" in
        install)
            check_root install
            install_system
            ;;
        start)
            check_root start
            start_service
            ;;
        stop)
            check_root stop
            stop_service
            ;;
        restart)
            check_root restart
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        uninstall)
            check_root uninstall
            uninstall_system
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}[错误]${NC} 未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"

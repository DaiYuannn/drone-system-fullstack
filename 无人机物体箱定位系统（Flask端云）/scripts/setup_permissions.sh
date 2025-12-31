#!/bin/bash
# 无人机物体箱定位系统 - 权限设置脚本

echo "设置脚本文件权限..."

# 为所有shell脚本添加执行权限
chmod +x deploy.sh
chmod +x install_linux.sh  
chmod +x start_server.sh
chmod +x stop_server.sh

echo "权限设置完成！"
echo ""
echo "现在你可以运行以下命令："
echo "  ./deploy.sh install    # 安装系统"
echo "  ./deploy.sh start      # 启动服务"
echo "  ./deploy.sh status     # 查看状态"
echo ""
echo "或者直接使用：" 
echo "  ./start_server.sh      # 独立启动脚本"
echo "  ./stop_server.sh       # 独立停止脚本"
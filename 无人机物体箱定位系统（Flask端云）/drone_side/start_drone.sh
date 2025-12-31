#!/bin/bash

# 无人机端启动脚本

set -e

echo "启动无人机物体箱定位系统"
echo "=============================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "Python3未安装，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 检查配置文件
if [ ! -f "config.py" ]; then
    echo "配置文件不存在，请检查config.py"
    exit 1
fi

# 检查模型文件
if [ ! -f "models/yolov8n_barcode.pt" ]; then
    echo "YOLO模型文件不存在，请下载模型文件到 models/ 目录"
    echo "   下载命令: wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O models/yolov8n_barcode.pt"
fi

# 创建日志目录
mkdir -p logs

# 检查摄像头权限
echo "检查摄像头权限..."
if [ -c "/dev/video0" ]; then
    echo "摄像头设备检测成功"
else
    echo "摄像头设备未检测到，请检查摄像头连接"
fi

# 检查GPS设备
echo "检查GPS设备..."
if [ -c "/dev/ttyUSB0" ]; then
    echo "GPS设备检测成功"
else
    echo "GPS设备未检测到，将在无GPS模式下运行"
fi

# 启动程序
echo "启动无人机系统..."
echo "按 Ctrl+C 停止程序"
echo ""

python main.py

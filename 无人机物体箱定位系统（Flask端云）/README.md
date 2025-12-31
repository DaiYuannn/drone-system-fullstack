# 无人机物体箱定位系统

基于计算机视觉和GPS定位的无人机物体箱检测与定位系统。

## 项目结构

```
ICSAC/
├── README.md                 # 项目主文档
├── config.py                 # 主配置文件
├── drone_side/              # 无人机端代码
│   ├── main.py              # 主程序入口
│   ├── barcode_detector.py  # 条码检测模块
│   ├── camera_handler.py    # 摄像头处理模块
│   ├── data_transmitter.py  # 数据传输模块
│   ├── gps_handler.py       # GPS处理模块
│   ├── config.py            # 无人机端配置
│   ├── requirements.txt     # 无人机端依赖
│   ├── linux_deploy/       # Linux嵌入式部署工具
│   └── embedded/           # 嵌入式设备优化模块
├── server_side/             # 服务器端代码
│   ├── app.py               # Flask应用主程序
│   ├── database.py          # 数据库处理模块
│   ├── config.py            # 服务器端配置
│   ├── requirements.txt     # 服务器端依赖
│   └── templates/           # Web界面模板
├── tests/                   # 测试文件（分类组织）
│   ├── windows/             # Windows平台专用测试
│   ├── simulation/          # 模拟测试工具
│   ├── integration/         # 集成测试
│   └── requirements_test.txt # 测试依赖
├── federated_learning/      # 联邦学习通信优化框架
│   ├── encryption/          # 数据通信加密模块
│   ├── big_little/          # Big.Little模型架构
│   ├── pervasive_fl/        # PervasiveFL框架
│   └── privacy_computing/   # 隐私计算优化
├── scripts/                 # 部署和工具脚本
│   ├── deploy.sh            # Linux部署脚本
│   ├── install_linux.sh     # Linux安装脚本
│   ├── setup_client.sh      # 客户端设置脚本
│   ├── start_server.sh      # 服务器启动脚本
│   ├── stop_server.sh       # 服务器停止脚本
│   └── drone-positioning.service # 系统服务配置
└── docs/                    # 项目文档
    ├── README_Linux部署指南.md
    ├── README_Windows测试指南.md
    ├── README_公网部署指南.md
    ├── README_测试程序使用说明.md
    ├── MIGRATION_SUMMARY.md
    ├── DEVELOPMENT_ROADMAP.md  # 开发路线图
    ├── TASK_TRACKER.md         # 任务追踪表
    └── 无人机物体箱定位项目规划.md
```

## 快速开始

### 1. 服务器端部署（Linux）

```bash
# 安装依赖和设置环境
./scripts/install_linux.sh

# 部署服务器
./scripts/deploy.sh

# 启动服务器
./scripts/start_server.sh
```

### 2. 无人机端运行

```bash
cd drone_side
pip install -r requirements.txt
python main.py
```

### 3. 测试系统

#### Windows平台测试
```bash
cd tests/windows
python setup_windows_test_env.bat
python run_windows_test.bat
```

#### 模拟测试
```bash
cd tests/simulation
python create_test_images.py    # 生成测试图片
python gps_simulator.py         # GPS模拟
python flight_controller_test.py # 飞控模拟
```

#### 集成测试
```bash
cd tests/integration
python data_transmission_tester.py  # 数据传输测试
python test_upload.py               # 上传功能测试
```

## 主要功能

- **实时条码检测**: 使用OpenCV和pyzbar进行QR码/条码检测
- **GPS定位**: 获取无人机精确位置信息
- **数据传输**: WebSocket实时数据传输到服务器
- **Web界面**: 实时监控无人机状态和检测结果
- **多平台支持**: 支持Linux服务器部署和Windows客户端测试

## 依赖要求

### 服务器端
- Python 3.8+
- Flask
- Flask-SocketIO
- SQLite

### 无人机端
- Python 3.8+
- OpenCV
- pyzbar
- Pillow
- python-socketio

## 配置说明

主要配置文件：
- `config.py` - 全局配置
- `drone_side/config.py` - 无人机端配置  
- `server_side/config.py` - 服务器端配置

### 服务器地址配置

为避免将真实公网地址硬编码在仓库中，示例与脚本中的地址均以“服务器IP”表示。请根据你的实际服务器地址进行配置：

- 临时运行/测试（Windows 批处理示例）：
    - 在运行前设置环境变量（当前会话生效）：
        - `set DRONE_SERVER_HOST=服务器IP`
        - `set DRONE_SERVER_PORT=5000`
    - 或使用 `tests\windows\set_test_server_env.bat` 按提示输入服务器地址。

- 无人机端（drone_side）：
    - 默认从环境变量读取，优先级：`SERVER_HOST` > 代码默认值。
    - 推荐在设备上设置：
        - Linux: `export SERVER_HOST=服务器IP`
        - Windows: `set SERVER_HOST=服务器IP`

- 服务器端（server_side）：
    - `server_side/config.py` 中的 `FLASK_CONFIG.host/port` 控制监听地址与端口；`public_ip` 字段仅用于展示或外链拼接，不影响监听。
    - 若需在服务环境中引用公网地址，可在 `/etc/drone_positioning/env` 中添加：
        - `PUBLIC_IP=服务器IP`
        - 并在应用中读取 `os.getenv('PUBLIC_IP')` 使用（如用于生成外链）。

- 文档与示例中出现的 `http://服务器IP:5000` 请替换为你的实际地址，例如 `http://203.0.113.10:5000`。


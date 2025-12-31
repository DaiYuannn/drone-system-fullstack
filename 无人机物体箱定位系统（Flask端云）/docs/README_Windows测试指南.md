# Windows无人机定位系统测试指南

## 概述

本指南说明如何在Windows系统上使用miniconda的test环境进行无人机定位系统的测试，通过公网地址(服务器IP:5000)上传测试数据。

注意：所有批处理/脚本输出均为纯 ASCII 文本，避免在 Windows cmd 或 PowerShell 中出现乱码。请确保文件保存为 UTF-8 编码（无 BOM）或系统默认编码可正确显示中文。

## 准备工作

### 1. 安装要求
- Windows 10/11
- Miniconda或Anaconda
- 网络连接（访问公网服务器）

### 2. 检查Miniconda
确保conda命令可用：
```cmd
conda --version
```

## 快速开始

### 第一步：环境部署
1. 运行环境部署脚本：
```cmd
setup_windows_test_env.bat
```

这将：
- 创建Python 3.12的test环境
- 安装所有必需依赖包
- 设置环境变量和配置文件
- 创建项目目录结构

### 第二步：激活环境
```cmd
conda activate test
```

或使用生成的激活脚本：
```cmd
%USERPROFILE%\drone_positioning_test\activate_test_env.bat
```

### 第三步：运行测试
#### 方法1：快速测试（推荐）
```cmd
python quick_test_windows.py
```

#### 方法2：完整测试
```cmd
python test_upload_windows.py
```

#### 方法3：使用批处理脚本
```cmd
run_windows_test.bat
```

## 文件说明

### 核心脚本
- `setup_windows_test_env.bat` - Windows环境部署脚本
- `quick_test_windows.py` - 快速测试脚本（基础依赖）
- `test_upload_windows.py` - 完整测试脚本（所有功能）
- `run_windows_test.bat` - 测试运行脚本

### 生成的文件结构
```
%USERPROFILE%\drone_positioning_test\
├── config\
│   ├── env_vars.bat           # 环境变量配置
│   └── test_config.py         # Python配置文件
├── logs\
│   ├── drone_test.log         # 测试日志
│   └── windows_test_report.json # 测试报告
├── test_images\               # 生成的测试图片
└── activate_test_env.bat      # 环境激活脚本
```

## 配置说明

### 默认配置
- **服务器地址**: `服务器IP:5000`
- **无人机ID**: `test_drone_001_windows`
- **GPS模拟**: 启用（上海坐标：31.2304, 121.4737）
- **测试模式**: 启用

### 环境变量（可自定义）
```cmd
set DRONE_SERVER_HOST=服务器IP
set DRONE_SERVER_PORT=5000
set DRONE_ID=test_drone_001_windows
set GPS_LATITUDE=31.2304
set GPS_LONGITUDE=121.4737
```

## 测试内容

### 快速测试 (quick_test_windows.py)
1. 服务器连接测试
2. 无人机注册测试
3. 数据上传测试（3次）

### 完整测试 (test_upload_windows.py)
1. API健康检查
2. 无人机注册
3. WebSocket连接测试
4. 状态更新测试
5. 数据上传测试（5次）
6. 条码图片生成
7. GPS模拟数据

## 测试数据

### 模拟条码数据
- `WIN-BOX001-ELECTRONICS`
- `WIN-BOX002-MEDICAL`  
- `WIN-BOX003-FOOD`
- `WIN-BOX004-CLOTHING`
- `WIN-BOX005-TOOLS`

### GPS模拟数据
- 基础坐标：上海市中心 (31.2304°N, 121.4737°E)
- 随机偏移：±100米范围
- 高度：10±5米

## 故障排除

### 常见问题

#### 1. 服务器连接失败
```
服务器连接失败
```
**解决方案**：
- 检查网络连接
- 确认服务器运行状态
- 检查防火墙设置
- 验证服务器地址：http://服务器IP:5000

#### 2. conda环境问题
```
错误: 未检测到conda环境
```
**解决方案**：
```cmd
conda activate test
```

#### 3. 依赖包缺失
```
ModuleNotFoundError: No module named 'requests'
```
**解决方案**：
```cmd
pip install requests pillow numpy qrcode[pil] python-socketio[client]
```

#### 4. 权限问题
**解决方案**：
- 以管理员身份运行命令提示符
- 检查文件夹权限

### 日志查看
- 测试日志：`%USERPROFILE%\drone_positioning_test\logs\drone_test.log`
- 测试报告：`%USERPROFILE%\drone_positioning_test\logs\windows_test_report.json`

## Web界面访问

测试成功后，可以通过以下地址查看上传的数据：
- **服务器地址**: http://服务器IP:5000
- **API健康检查**: http://服务器IP:5000/api/health
- **数据查看**: 在Web界面查看实时数据

## 测试清单

在运行测试前，请确认：

- [ ] Miniconda已安装且conda命令可用
- [ ] 网络可以访问服务器IP:5000
- [ ] 已运行`setup_windows_test_env.bat`
- [ ] test环境已激活
- [ ] 防火墙允许Python网络连接

# 无人机物体箱定位系统 - Linux手动部署指南

## 系统概述

本系统是一个用于无人机物体箱定位的实时监控平台，采用Flask + WebSocket架构，使用SQLite数据库存储数据，支持Linux系统手动部署。

约定：所有 shell 脚本的输出为纯 ASCII 文本，以避免在不同发行版/终端下的编码兼容问题。建议将脚本保存为 UTF-8 无 BOM 编码，并在需要显示中文的地方使用 echo 纯文本说明或注释。

## 系统架构

- **后端服务**: Flask + Python-SocketIO + SQLite
- **前端界面**: HTML5 + JavaScript + WebSocket
- **数据存储**: SQLite数据库
- **部署方式**: Linux systemd服务
- **通信协议**: HTTP REST API + WebSocket

## 系统要求

### 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 20GB可用空间
- 网络: 支持HTTP访问

### 软件要求
- 操作系统: Ubuntu 18.04+ / CentOS 7+ / Debian 10+ / RHEL 8+
- Python: 3.8+
- 系统权限: sudo管理员权限

## 快速安装

### 自动安装（推荐）

1. 下载项目文件到服务器
2. 给安装脚本执行权限：
   ```bash
   chmod +x install_linux.sh
   ```
3. 运行安装脚本：
   ```bash
   sudo ./install_linux.sh
   ```

安装脚本会自动完成以下操作：
- 安装系统依赖包
- 创建专用用户和目录
- 设置Python虚拟环境
- 安装项目依赖
- 配置systemd服务
- 初始化数据库
- 配置防火墙
- 创建管理脚本

### 手动安装

如果自动安装失败，可以按以下步骤手动安装：

#### 1. 安装系统依赖

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv python3-dev \
                        build-essential curl wget git \
                        sqlite3 libsqlite3-dev
```

CentOS/RHEL:
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel \
                   gcc gcc-c++ make curl wget git \
                   sqlite sqlite-devel
```

#### 2. 创建系统用户

```bash
sudo groupadd drone
sudo useradd -r -g drone -d /opt/drone_positioning -s /bin/bash drone
```

#### 3. 创建目录结构

```bash
sudo mkdir -p /opt/drone_positioning
sudo mkdir -p /var/lib/drone_positioning
sudo mkdir -p /var/log/drone_positioning
sudo mkdir -p /etc/drone_positioning
```

#### 4. 复制项目文件

```bash
sudo cp -r server_side/* /opt/drone_positioning/
sudo cp -r drone_side /opt/drone_positioning/
sudo chown -R drone:drone /opt/drone_positioning
sudo chown -R drone:drone /var/lib/drone_positioning
sudo chown -R drone:drone /var/log/drone_positioning
```

#### 5. 设置Python环境

```bash
sudo -u drone python3 -m venv /opt/drone_positioning/venv
sudo -u drone /opt/drone_positioning/venv/bin/pip install --upgrade pip
sudo -u drone /opt/drone_positioning/venv/bin/pip install -r /opt/drone_positioning/requirements.txt
```

#### 6. 初始化数据库

```bash
sudo -u drone bash -c "
cd /opt/drone_positioning
source venv/bin/activate
python -c '
from database import DatabaseManager
db = DatabaseManager()
if db.connect() and db.create_tables():
    print(\"数据库初始化成功\")
else:
    print(\"数据库初始化失败\")
    exit(1)
'
"
```

#### 7. 安装systemd服务

```bash
sudo cp drone-positioning.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable drone-positioning
```

## 服务管理

### 启动服务
```bash
sudo systemctl start drone-positioning
# 或使用便捷命令
drone-start
```

### 停止服务
```bash
sudo systemctl stop drone-positioning
# 或使用便捷命令
drone-stop
```

### 重启服务
```bash
sudo systemctl restart drone-positioning
# 或使用便捷命令
drone-restart
```

### 查看服务状态
```bash
sudo systemctl status drone-positioning
# 或使用便捷命令
drone-status
```

### 查看实时日志
```bash
sudo journalctl -u drone-positioning -f
```

### 查看历史日志
```bash
sudo journalctl -u drone-positioning --since "1 hour ago"
```

## 配置文件

### 主配置文件位置
`/opt/drone_positioning/config.py`

### 关键配置项

```python
# 服务器配置
FLASK_CONFIG = {
    'host': '0.0.0.0',      # 监听地址
    'port': 5000,           # 监听端口
    'debug': False          # 调试模式
}

# 数据库配置
DB_CONFIG = {
    'path': '/var/lib/drone_positioning/drone_data.db',
    'timeout': 30.0,
    'check_same_thread': False
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'file': '/var/log/drone_positioning/app.log'
}
```

## 目录结构

```
/opt/drone_positioning/          # 主程序目录
├── app.py                       # Flask主程序
├── config.py                    # 配置文件
├── database.py                  # 数据库操作模块
├── requirements.txt             # Python依赖
├── venv/                        # Python虚拟环境
└── templates/                   # HTML模板
    └── index.html

/var/lib/drone_positioning/      # 数据存储目录
└── drone_data.db               # SQLite数据库文件

/var/log/drone_positioning/      # 日志目录
├── app.log                     # 应用日志
└── startup.log                 # 启动日志

/etc/systemd/system/             # 系统服务
└── drone-positioning.service   # systemd服务文件
```

## 防火墙配置

### Ubuntu/Debian (UFW)
```bash
sudo ufw allow 5000/tcp
sudo ufw reload
```

### CentOS/RHEL (firewalld)
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 传统iptables
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables-save
```

## 访问系统

### Web界面
- 地址: `http://服务器IP:5000`
- 功能: 实时监控、数据查看、系统状态

### API接口

#### 健康检查
```bash
curl http://localhost:5000/api/health
```

#### 数据上传（无人机使用）
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-01T12:00:00",
    "drone_id": "drone_001",
    "barcode_data": "123456789",
    "confidence": 0.95,
    "gps": {
      "latitude": 39.9042,
      "longitude": 116.4074,
      "altitude": 100
    }
  }'
```

#### 获取位置数据
```bash
curl http://localhost:5000/api/positions?limit=10
```

#### 获取无人机状态
```bash
curl http://localhost:5000/api/drones
```

#### 获取统计信息
```bash
curl http://localhost:5000/api/statistics
```

## 性能优化

### 数据库优化
- 定期清理旧数据：`curl -X POST http://localhost:5000/api/cleanup`
- 数据库备份：`sqlite3 /var/lib/drone_positioning/drone_data.db .dump > backup.sql`

### 系统监控
```bash
# 查看系统资源使用
top -p $(pgrep -f "python.*app.py")

# 查看端口监听状态
netstat -tlnp | grep :5000

# 查看磁盘使用
df -h /var/lib/drone_positioning
du -sh /var/log/drone_positioning
```

## 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看详细错误信息
sudo journalctl -u drone-positioning --no-pager
```

#### 2. 端口被占用
```bash
# 查看端口占用
sudo netstat -tlnp | grep :5000
# 或者
sudo ss -tlnp | grep :5000
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la /opt/drone_positioning/
ls -la /var/lib/drone_positioning/
ls -la /var/log/drone_positioning/

# 修复权限
sudo chown -R drone:drone /opt/drone_positioning
sudo chown -R drone:drone /var/lib/drone_positioning
sudo chown -R drone:drone /var/log/drone_positioning
```

#### 4. 数据库问题
```bash
# 检查数据库文件
sudo -u drone sqlite3 /var/lib/drone_positioning/drone_data.db ".tables"

# 重新初始化数据库
sudo -u drone bash -c "
cd /opt/drone_positioning
source venv/bin/activate
python -c 'from database import DatabaseManager; db = DatabaseManager(); db.connect(); db.create_tables()'
"
```

#### 5. Python依赖问题
```bash
# 重新安装依赖
sudo -u drone /opt/drone_positioning/venv/bin/pip install -r /opt/drone_positioning/requirements.txt
```

### 日志分析

#### 查看应用日志
```bash
sudo tail -f /var/log/drone_positioning/app.log
```

#### 查看系统日志
```bash
sudo journalctl -u drone-positioning -f
```

#### 日志级别调整
编辑 `/opt/drone_positioning/config.py`，修改日志级别：
```python
LOG_CONFIG = {
    'level': 'DEBUG',  # 可选: DEBUG, INFO, WARNING, ERROR
    'file': '/var/log/drone_positioning/app.log'
}
```

## 卸载系统

如需完全卸载系统：

```bash
# 停止并禁用服务
sudo systemctl stop drone-positioning
sudo systemctl disable drone-positioning

# 删除服务文件
sudo rm /etc/systemd/system/drone-positioning.service
sudo systemctl daemon-reload

# 删除程序文件
sudo rm -rf /opt/drone_positioning

# 删除数据文件（注意：会丢失所有数据）
sudo rm -rf /var/lib/drone_positioning

# 删除日志文件
sudo rm -rf /var/log/drone_positioning

# 删除用户（可选）
sudo userdel drone
sudo groupdel drone

# 删除便捷脚本
sudo rm /usr/local/bin/drone-*
```
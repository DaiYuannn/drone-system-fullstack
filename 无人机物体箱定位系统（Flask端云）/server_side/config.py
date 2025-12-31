"""
服务器端配置文件 - Linux手动部署版本
"""
import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / 'logs'
UPLOADS_DIR = BASE_DIR / 'uploads'
DATA_DIR = Path('/var/lib/drone_positioning')  # Linux系统数据目录

# 创建必要目录
for directory in [LOGS_DIR, UPLOADS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 如果有权限则创建系统数据目录，否则使用本地目录
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    DATA_DIR = BASE_DIR / 'data'
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# SQLite数据库配置（替换MySQL，简化部署）
DB_CONFIG = {
    'type': 'sqlite',
    'path': str(DATA_DIR / 'drone_positioning.db'),
    'timeout': 30,
    'check_same_thread': False
}

# Flask配置
FLASK_CONFIG = {
    'host': os.getenv('FLASK_HOST', '0.0.0.0'),
    'port': int(os.getenv('FLASK_PORT', '5000')),
    'debug': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
    'public_ip': '服务器IP'  # 公网IP地址（展示用途，可在运行时通过环境变量覆盖或忽略）
}

# WebSocket配置
WEBSOCKET_CONFIG = {
    'host': os.getenv('WS_HOST', '0.0.0.0'),
    'port': int(os.getenv('WS_PORT', '5001')),
    'cors_allowed_origins': "*",
    'async_mode': 'eventlet'
}

# 日志配置
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': str(LOGS_DIR / 'server.log'),
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 文件上传配置
UPLOAD_CONFIG = {
    'max_size': int(os.getenv('MAX_UPLOAD_SIZE', '16777216')),  # 16MB
    'allowed_extensions': {'png', 'jpg', 'jpeg', 'gif', 'bmp'},
    'upload_folder': str(UPLOADS_DIR)
}

# 系统配置
SYSTEM_CONFIG = {
    'max_connections': int(os.getenv('MAX_CONNECTIONS', '100')),
    'heartbeat_timeout': int(os.getenv('HEARTBEAT_TIMEOUT', '60')),  # 秒
    'data_retention_days': int(os.getenv('DATA_RETENTION_DAYS', '30')),
    'user': 'drone',
    'group': 'drone',
    'pid_file': '/var/run/drone_server.pid',
    'systemd_service': 'drone-positioning.service'
}

# 安全配置
SECURITY_CONFIG = {
    'max_content_length': 16 * 1024 * 1024,  # 16MB
    'rate_limit': 100,  # 每分钟请求数
    'allowed_origins': ['*'],  # 生产环境应限制具体域名
    'api_key_required': False,  # 设为True启用API密钥验证
    # 管理端点令牌（优先读取环境变量 ADMIN_TOKEN）
    'admin_token': os.getenv('ADMIN_TOKEN', '')
}

# API配置
API_CONFIG = {
    'version': 'v1',
    'timeout': 30,
    'max_batch_size': 100,
    'enable_cors': True
}

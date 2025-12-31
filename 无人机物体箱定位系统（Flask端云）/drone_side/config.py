"""
无人机端配置文件
"""
import os

# 服务器配置
SERVER_HOST = os.getenv('SERVER_HOST', '服务器IP')  # 公网服务器IP（请替换为实际地址或通过环境变量覆盖）
SERVER_PORT = int(os.getenv('SERVER_PORT', '5000'))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# 无人机配置
DRONE_ID = os.getenv('DRONE_ID', 'DRONE-001')

# 摄像头配置
CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
CAMERA_WIDTH = int(os.getenv('CAMERA_WIDTH', '640'))
CAMERA_HEIGHT = int(os.getenv('CAMERA_HEIGHT', '480'))

# YOLO模型配置
MODEL_PATH = os.getenv('MODEL_PATH', 'models/yolov8n_barcode.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))

# MAVLink配置
MAVLINK_CONNECTION = os.getenv('MAVLINK_CONNECTION', '/dev/ttyUSB0')
MAVLINK_BAUD = int(os.getenv('MAVLINK_BAUD', '57600'))

# 数据处理与安全配置
DATA_UPLOAD_INTERVAL = int(os.getenv('DATA_UPLOAD_INTERVAL', '1'))  # 秒
MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))

# 加密开关（PLAINTEXT/AES-GCM/可插拔名称，仅作为标识；实际算法由security/crypto_algo.py决定）
ENCRYPTION_ENABLED = os.getenv('ENCRYPTION_ENABLED', 'true').lower() == 'true'
ENCRYPTION_ALGO = os.getenv('ENCRYPTION_ALGO', 'AES-GCM')

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/drone.log')

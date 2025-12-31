#!/usr/bin/env python3
"""
飞控测试程序配置文件
"""

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent
TEST_IMAGES_DIR = BASE_DIR / "test_images"
TEST_RESULTS_DIR = BASE_DIR / "test_results"
LOGS_DIR = BASE_DIR / "logs"

# 创建必要的目录
for directory in [TEST_IMAGES_DIR, TEST_RESULTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# 服务器配置
SERVER_CONFIG = {
    'url': 'http://localhost:5000',
    'timeout': 10,
    'retry_attempts': 3,
    'retry_delay': 2.0
}

# GPS模拟器配置
GPS_CONFIG = {
    'center_latitude': 39.9087,      # 北京天安门纬度
    'center_longitude': 116.3975,    # 北京天安门经度
    'flight_area_radius_km': 1.0,    # 飞行区域半径（公里）
    'min_altitude': 5.0,             # 最小飞行高度（米）
    'max_altitude': 50.0,            # 最大飞行高度（米）
    'flight_speed_mps': 5.0,         # 飞行速度（米/秒）
    'max_turn_angle': 30.0           # 最大转向角度（度）
}

# 无人机配置
DRONE_CONFIG = {
    'default_drone_id': 'DRONE-TEST-001',
    'battery_simulation': True,
    'signal_strength_simulation': True,
    'flight_time_limit_minutes': 30
}

# 条形码检测配置
BARCODE_CONFIG = {
    'supported_formats': ['QRCODE', 'CODE128', 'CODE39', 'EAN13', 'EAN8', 'PDF417', 'DATAMATRIX'],
    'min_confidence': 0.7,
    'max_detection_attempts': 3,
    'image_preprocessing': True,
    'quality_analysis': True
}

# 测试配置
TEST_CONFIG = {
    'default_test_interval': 2.0,     # 测试间隔（秒）
    'max_test_images': 50,            # 最大测试图片数
    'concurrent_upload_workers': 3,   # 并发上传线程数
    'batch_size': 10,                 # 批处理大小
    'generate_test_report': True,     # 生成测试报告
    'save_detection_images': True     # 保存检测结果图片
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': {
        'filename': str(LOGS_DIR / 'flight_test.log'),
        'max_bytes': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'encoding': 'utf-8'
    },
    'console_handler': {
        'enabled': True,
        'level': 'INFO'
    }
}

# 数据库配置（如果需要本地数据库）
DATABASE_CONFIG = {
    'type': 'sqlite',
    'path': str(BASE_DIR / 'test_database.db'),
    'tables': {
        'test_results': '''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                drone_id TEXT NOT NULL,
                image_path TEXT NOT NULL,
                barcode_data TEXT,
                barcode_type TEXT,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                confidence REAL,
                upload_success BOOLEAN,
                test_session_id TEXT
            )
        '''
    }
}

# 图片生成配置
IMAGE_GENERATION_CONFIG = {
    'default_image_count': 15,
    'image_size': (1024, 768),
    'qr_code_sizes': [150, 200, 250],
    'scene_types': ['warehouse', 'outdoor', 'indoor', 'factory'],
    'effect_types': ['none', 'blur', 'noise', 'dark', 'bright', 'contrast'],
    'barcode_data_prefixes': ['BOX', 'WAREHOUSE', 'FACTORY', 'CONTAINER', 'PACKAGE']
}

# 性能监控配置
PERFORMANCE_CONFIG = {
    'monitor_system_resources': True,
    'cpu_threshold': 80.0,           # CPU使用率阈值
    'memory_threshold': 80.0,        # 内存使用率阈值
    'disk_threshold': 90.0,          # 磁盘使用率阈值
    'network_timeout': 30.0          # 网络超时时间
}

# 错误处理配置
ERROR_HANDLING_CONFIG = {
    'max_retry_attempts': 3,
    'retry_delay_base': 1.0,         # 基础重试延迟（秒）
    'retry_delay_multiplier': 2.0,   # 重试延迟倍数
    'continue_on_error': True,       # 发生错误时是否继续
    'save_error_logs': True,         # 保存错误日志
    'error_screenshot': False        # 错误时截图（如果适用）
}

# 输出配置
OUTPUT_CONFIG = {
    'save_detailed_results': True,
    'save_statistics': True,
    'save_flight_path': True,
    'export_formats': ['json', 'csv'],
    'compress_results': False,
    'result_retention_days': 30      # 结果保留天数
}

# 验证配置
VALIDATION_CONFIG = {
    'validate_gps_coordinates': True,
    'gps_coordinate_bounds': {
        'min_latitude': -90.0,
        'max_latitude': 90.0,
        'min_longitude': -180.0,
        'max_longitude': 180.0,
        'min_altitude': 0.0,
        'max_altitude': 1000.0
    },
    'validate_barcode_format': True,
    'validate_confidence_range': True,
    'confidence_range': (0.0, 1.0)
}


def get_config() -> dict:
    """获取完整配置"""
    return {
        'server': SERVER_CONFIG,
        'gps': GPS_CONFIG,
        'drone': DRONE_CONFIG,
        'barcode': BARCODE_CONFIG,
        'test': TEST_CONFIG,
        'logging': LOGGING_CONFIG,
        'database': DATABASE_CONFIG,
        'image_generation': IMAGE_GENERATION_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'error_handling': ERROR_HANDLING_CONFIG,
        'output': OUTPUT_CONFIG,
        'validation': VALIDATION_CONFIG,
        'paths': {
            'base_dir': str(BASE_DIR),
            'test_images_dir': str(TEST_IMAGES_DIR),
            'test_results_dir': str(TEST_RESULTS_DIR),
            'logs_dir': str(LOGS_DIR)
        }
    }


def get_environment_config() -> dict:
    """获取环境相关配置"""
    return {
        'server_url': os.getenv('SERVER_URL', SERVER_CONFIG['url']),
        'drone_id': os.getenv('DRONE_ID', DRONE_CONFIG['default_drone_id']),
        'log_level': os.getenv('LOG_LEVEL', LOGGING_CONFIG['level']),
        'test_mode': os.getenv('TEST_MODE', 'full'),
        'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    }


def validate_config() -> bool:
    """验证配置的有效性"""
    try:
        # 检查必要的目录
        for directory in [TEST_IMAGES_DIR, TEST_RESULTS_DIR, LOGS_DIR]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
        
        # 验证GPS配置
        gps = GPS_CONFIG
        if not (-90 <= gps['center_latitude'] <= 90):
            raise ValueError(f"无效的中心纬度: {gps['center_latitude']}")
        
        if not (-180 <= gps['center_longitude'] <= 180):
            raise ValueError(f"无效的中心经度: {gps['center_longitude']}")
        
        if gps['min_altitude'] >= gps['max_altitude']:
            raise ValueError("最小高度必须小于最大高度")
        
        # 验证测试配置
        test = TEST_CONFIG
        if test['default_test_interval'] <= 0:
            raise ValueError("测试间隔必须大于0")
        
        if test['concurrent_upload_workers'] <= 0:
            raise ValueError("并发工作线程数必须大于0")
        
        return True
        
    except Exception as e:
        print(f"配置验证失败: {str(e)}")
        return False


def print_config_summary():
    """打印配置摘要"""
    print("飞控测试程序配置摘要")
    print("=" * 50)
    print(f"服务器URL: {SERVER_CONFIG['url']}")
    print(f"测试图片目录: {TEST_IMAGES_DIR}")
    print(f"测试结果目录: {TEST_RESULTS_DIR}")
    print(f"日志目录: {LOGS_DIR}")
    print(f"GPS中心位置: ({GPS_CONFIG['center_latitude']}, {GPS_CONFIG['center_longitude']})")
    print(f"飞行区域半径: {GPS_CONFIG['flight_area_radius_km']}km")
    print(f"默认无人机ID: {DRONE_CONFIG['default_drone_id']}")
    print(f"支持的条形码格式: {', '.join(BARCODE_CONFIG['supported_formats'])}")
    print(f"测试间隔: {TEST_CONFIG['default_test_interval']}秒")
    print("=" * 50)


if __name__ == "__main__":
    print_config_summary()
    
    if validate_config():
        print("✓ 配置验证通过")
    else:
        print("✗ 配置验证失败")
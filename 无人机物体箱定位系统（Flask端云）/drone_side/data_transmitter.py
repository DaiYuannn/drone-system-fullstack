"""
数据回传模块
将检测到的条形码和GPS数据发送到服务器
"""
import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import config
try:
    from .security.crypto_adapter import encrypt_payload
except Exception:
    # 兼容：无法导入则退化为明文
    def encrypt_payload(x):
        return x
try:
    from .security.field_adapter import transform_outgoing
except Exception:
    def transform_outgoing(x):
        return x

logger = logging.getLogger(__name__)

class DataTransmitter:
    def __init__(self, server_url: str = None, drone_id: str = None):
        """
        初始化数据发送器
        
        Args:
            server_url: 服务器URL
            drone_id: 无人机ID
        """
        self.server_url = server_url or config.SERVER_URL
        self.drone_id = drone_id or config.DRONE_ID
        self.upload_interval = config.DATA_UPLOAD_INTERVAL
        self.max_retry_attempts = config.MAX_RETRY_ATTEMPTS
        self.last_upload_time = 0
        
    def create_data_package(self, barcodes: List[dict], gps_position: tuple) -> Dict:
        """
        创建数据包
        
        Args:
            barcodes: 检测到的条形码列表
            gps_position: GPS位置 (lat, lon, alt)
            
        Returns:
            格式化的数据包
        """
        timestamp = datetime.now().isoformat()
        
        if gps_position:
            lat, lon, alt = gps_position
            gps_data = {
                "latitude": lat,
                "longitude": lon,
                "altitude": alt
            }
        else:
            gps_data = None
        
        # 为每个检测到的条形码创建数据包
        data_packages = []
        for barcode in barcodes:
            package = {
                "timestamp": timestamp,
                "drone_id": self.drone_id,
                "barcode_data": barcode['data'],
                "barcode_type": barcode['type'],
                "gps": gps_data,
                "confidence": barcode['confidence'],
                "bbox": barcode['bbox']
            }
            # 字段级隐私转换（可插拔）
            package = transform_outgoing(package)
            data_packages.append(package)
        
        return data_packages
    
    def upload_data(self, data_packages: List[Dict]) -> bool:
        """
        上传数据到服务器
        
        Args:
            data_packages: 数据包列表
            
        Returns:
            上传是否成功
        """
        if not data_packages:
            return True
        
        # 检查上传间隔
        current_time = time.time()
        if current_time - self.last_upload_time < self.upload_interval:
            return True
        
        for package in data_packages:
            success = self._upload_single_package(package)
            if not success:
                logger.error(f"数据包上传失败: {package['barcode_data']}")
                return False
        
        self.last_upload_time = current_time
        logger.info(f"成功上传 {len(data_packages)} 个数据包")
        return True
    
    def _upload_single_package(self, package: Dict) -> bool:
        """
        上传单个数据包
        
        Args:
            package: 数据包
            
        Returns:
            上传是否成功
        """
        url = f"{self.server_url}/api/upload"
        
        for attempt in range(self.max_retry_attempts):
            try:
                payload = encrypt_payload(package) if config.ENCRYPTION_ENABLED else package
                response = requests.post(
                    url,
                    json=payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        logger.debug(f"数据包上传成功: {package['barcode_data']}")
                        return True
                    else:
                        logger.warning(f"服务器返回错误: {result.get('message')}")
                else:
                    logger.warning(f"HTTP错误: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"上传请求失败 (尝试 {attempt + 1}/{self.max_retry_attempts}): {e}")
                
            if attempt < self.max_retry_attempts - 1:
                time.sleep(1)  # 重试前等待1秒
        
        return False
    
    def upload_heartbeat(self) -> bool:
        """
        发送心跳包
        
        Returns:
            发送是否成功
        """
        heartbeat_data = {
            "timestamp": datetime.now().isoformat(),
            "drone_id": self.drone_id,
            "type": "heartbeat",
            "status": "active"
        }
        
        url = f"{self.server_url}/api/heartbeat"
        
        try:
            payload = encrypt_payload(heartbeat_data) if config.ENCRYPTION_ENABLED else heartbeat_data
            response = requests.post(
                url,
                json=payload,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.debug("心跳包发送成功")
                return True
            else:
                logger.warning(f"心跳包发送失败: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"心跳包发送异常: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        测试与服务器的连接
        
        Returns:
            连接是否正常
        """
        url = f"{self.server_url}/api/health"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("服务器连接正常")
                return True
            else:
                logger.warning(f"服务器响应异常: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"无法连接到服务器: {e}")
            return False

"""
GPS数据处理模块
通过MAVLink协议获取无人机GPS位置信息
"""
import time
import logging
from typing import Tuple, Optional
from pymavlink import mavutil
import config

logger = logging.getLogger(__name__)

class GPSHandler:
    def __init__(self, connection_string: str = None, baud: int = None):
        """
        初始化GPS处理器
        
        Args:
            connection_string: MAVLink连接字符串
            baud: 波特率
        """
        self.connection_string = connection_string or config.MAVLINK_CONNECTION
        self.baud = baud or config.MAVLINK_BAUD
        self.connection = None
        self.last_position = None
        self.last_update_time = 0
        
    def connect(self) -> bool:
        """
        连接到飞控系统
        
        Returns:
            连接是否成功
        """
        try:
            self.connection = mavutil.mavlink_connection(
                self.connection_string, 
                baud=self.baud
            )
            
            # 等待心跳信号
            self.connection.wait_heartbeat()
            logger.info(f"飞控连接成功 - 系统ID: {self.connection.target_system}, "
                       f"组件ID: {self.connection.target_component}")
            return True
            
        except Exception as e:
            logger.error(f"飞控连接失败: {e}")
            return False
    
    def get_gps_position(self) -> Optional[Tuple[float, float, float]]:
        """
        获取当前GPS位置
        
        Returns:
            (纬度, 经度, 高度) 或 None
        """
        if not self.connection:
            logger.warning("飞控未连接")
            return None
        
        try:
            # 请求GPS位置信息
            self.connection.mav.request_data_stream_send(
                self.connection.target_system,
                self.connection.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_POSITION,
                1,  # 1Hz
                1   # 启用
            )
            
            # 获取GPS位置消息
            msg = self.connection.recv_match(type='GLOBAL_POSITION_INT', blocking=False)
            
            if msg:
                lat = msg.lat / 1e7  # 纬度
                lon = msg.lon / 1e7  # 经度
                alt = msg.alt / 1e3  # 高度（米）
                
                # 检查GPS数据有效性
                if self._is_valid_gps_data(lat, lon, alt):
                    self.last_position = (lat, lon, alt)
                    self.last_update_time = time.time()
                    return self.last_position
                else:
                    logger.warning("GPS数据无效")
                    return None
            else:
                # 如果没有新数据，返回上次有效位置
                if self.last_position and (time.time() - self.last_update_time) < 5:
                    return self.last_position
                return None
                
        except Exception as e:
            logger.error(f"获取GPS位置失败: {e}")
            return None
    
    def _is_valid_gps_data(self, lat: float, lon: float, alt: float) -> bool:
        """
        验证GPS数据的有效性
        
        Args:
            lat: 纬度
            lon: 经度
            alt: 高度
            
        Returns:
            数据是否有效
        """
        # 检查坐标范围
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
        
        # 检查高度范围（0-10000米）
        if not (0 <= alt <= 10000):
            return False
        
        # 检查是否为默认值（通常为0）
        if lat == 0 and lon == 0:
            return False
        
        return True
    
    def get_gps_status(self) -> dict:
        """
        获取GPS状态信息
        
        Returns:
            GPS状态字典
        """
        if not self.connection:
            return {"connected": False, "status": "未连接"}
        
        try:
            # 获取GPS状态消息
            msg = self.connection.recv_match(type='GPS_RAW_INT', blocking=False)
            
            if msg:
                return {
                    "connected": True,
                    "fix_type": msg.fix_type,
                    "satellites": msg.satellites_visible,
                    "hdop": msg.eph / 100.0,  # 水平精度
                    "vdop": msg.epv / 100.0,  # 垂直精度
                    "last_position": self.last_position,
                    "last_update": self.last_update_time
                }
            else:
                return {
                    "connected": True,
                    "status": "等待GPS数据",
                    "last_position": self.last_position
                }
                
        except Exception as e:
            logger.error(f"获取GPS状态失败: {e}")
            return {"connected": False, "error": str(e)}
    
    def disconnect(self):
        """断开飞控连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("飞控连接已断开")
    
    def __del__(self):
        """析构函数，确保连接被正确关闭"""
        self.disconnect()

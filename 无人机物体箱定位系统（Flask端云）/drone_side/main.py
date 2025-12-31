"""
无人机端主程序
整合所有模块，实现完整的物体箱定位功能
"""
import cv2
import time
import logging
import signal
import sys
import os
from datetime import datetime
from typing import List, Dict

# 导入自定义模块
from barcode_detector import BarcodeDetector
from gps_handler import GPSHandler
from camera_handler import CameraHandler
from data_transmitter import DataTransmitter
import config

# 配置日志
def setup_logging():
    """设置日志配置"""
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

class DroneSystem:
    def __init__(self):
        """初始化无人机系统"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个模块
        self.barcode_detector = None
        self.gps_handler = None
        self.camera_handler = None
        self.data_transmitter = None
        
        # 系统状态
        self.is_running = False
        self.detection_count = 0
        self.last_heartbeat = 0
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def initialize(self) -> bool:
        """
        初始化系统所有模块
        
        Returns:
            初始化是否成功
        """
        self.logger.info("开始初始化无人机系统...")
        
        try:
            # 初始化条形码检测器
            self.logger.info("初始化条形码检测器...")
            self.barcode_detector = BarcodeDetector()
            
            # 初始化GPS处理器
            self.logger.info("初始化GPS处理器...")
            self.gps_handler = GPSHandler()
            if not self.gps_handler.connect():
                self.logger.warning("GPS连接失败，将在无GPS模式下运行")
            
            # 初始化摄像头处理器
            self.logger.info("初始化摄像头处理器...")
            self.camera_handler = CameraHandler()
            if not self.camera_handler.initialize():
                self.logger.error("摄像头初始化失败")
                return False
            
            # 初始化数据发送器
            self.logger.info("初始化数据发送器...")
            self.data_transmitter = DataTransmitter()
            
            # 测试服务器连接
            if not self.data_transmitter.test_connection():
                self.logger.warning("无法连接到服务器，数据将无法上传")
            
            self.logger.info("系统初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {e}")
            return False
    
    def start(self):
        """启动系统"""
        if not self.initialize():
            self.logger.error("系统初始化失败，无法启动")
            return
        
        self.logger.info("启动无人机物体箱定位系统...")
        self.is_running = True
        
        # 启动摄像头捕获
        self.camera_handler.start_capture(self._process_frame)
        
        # 主循环
        self._main_loop()
    
    def _process_frame(self, frame):
        """
        处理摄像头帧
        
        Args:
            frame: 摄像头帧
        """
        try:
            # 检测条形码
            barcodes = self.barcode_detector.detect_barcodes(frame)
            
            if barcodes:
                self.logger.info(f"检测到 {len(barcodes)} 个条形码")
                
                # 获取GPS位置
                gps_position = self.gps_handler.get_gps_position()
                
                # 创建数据包并上传
                data_packages = self.data_transmitter.create_data_package(barcodes, gps_position)
                self.data_transmitter.upload_data(data_packages)
                
                self.detection_count += len(barcodes)
                
                # 在图像上绘制检测结果
                result_frame = self.barcode_detector.draw_detections(frame, barcodes)
                
                # 显示结果（可选）
                if config.LOG_LEVEL == 'DEBUG':
                    cv2.imshow('Barcode Detection', result_frame)
                    cv2.waitKey(1)
            
            # 定期发送心跳
            current_time = time.time()
            if current_time - self.last_heartbeat > 30:  # 每30秒发送一次心跳
                self.data_transmitter.upload_heartbeat()
                self.last_heartbeat = current_time
                
        except Exception as e:
            self.logger.error(f"帧处理失败: {e}")
    
    def _main_loop(self):
        """主循环"""
        self.logger.info("系统运行中...")
        
        try:
            while self.is_running:
                # 检查系统状态
                self._check_system_status()
                
                # 短暂休眠
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号")
        except Exception as e:
            self.logger.error(f"主循环异常: {e}")
        finally:
            self.shutdown()
    
    def _check_system_status(self):
        """检查系统状态"""
        # 检查GPS状态
        gps_status = self.gps_handler.get_gps_status()
        if not gps_status.get('connected', False):
            self.logger.warning("GPS连接异常")
        
        # 检查摄像头状态
        camera_info = self.camera_handler.get_camera_info()
        if camera_info.get('status') != '已初始化':
            self.logger.warning("摄像头状态异常")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"接收到信号 {signum}，开始关闭系统...")
        self.is_running = False
    
    def shutdown(self):
        """关闭系统"""
        self.logger.info("正在关闭系统...")
        
        self.is_running = False
        
        # 停止摄像头
        if self.camera_handler:
            self.camera_handler.stop_capture()
            self.camera_handler.release()
        
        # 断开GPS连接
        if self.gps_handler:
            self.gps_handler.disconnect()
        
        # 关闭OpenCV窗口
        cv2.destroyAllWindows()
        
        self.logger.info(f"系统已关闭，共检测到 {self.detection_count} 个条形码")

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建并启动系统
    drone_system = DroneSystem()
    
    try:
        drone_system.start()
    except Exception as e:
        logging.error(f"系统运行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

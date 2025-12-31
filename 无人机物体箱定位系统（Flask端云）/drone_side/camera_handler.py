"""
摄像头处理模块
负责摄像头初始化和视频流处理
"""
import cv2
import numpy as np
import logging
import threading
import time
from typing import Optional, Callable
import config

logger = logging.getLogger(__name__)

class CameraHandler:
    def __init__(self, camera_index: int = None, width: int = None, height: int = None):
        """
        初始化摄像头处理器
        
        Args:
            camera_index: 摄像头索引
            width: 图像宽度
            height: 图像高度
        """
        self.camera_index = camera_index or config.CAMERA_INDEX
        self.width = width or config.CAMERA_WIDTH
        self.height = height or config.CAMERA_HEIGHT
        self.cap = None
        self.is_running = False
        self.frame_callback = None
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def initialize(self) -> bool:
        """
        初始化摄像头
        
        Returns:
            初始化是否成功
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"无法打开摄像头 {self.camera_index}")
                return False
            
            # 设置摄像头参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲区延迟
            
            # 验证设置
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"摄像头初始化成功 - 分辨率: {actual_width}x{actual_height}, FPS: {actual_fps}")
            return True
            
        except Exception as e:
            logger.error(f"摄像头初始化失败: {e}")
            return False
    
    def start_capture(self, frame_callback: Callable[[np.ndarray], None] = None):
        """
        开始视频捕获
        
        Args:
            frame_callback: 帧处理回调函数
        """
        if not self.cap or not self.cap.isOpened():
            logger.error("摄像头未初始化")
            return
        
        self.frame_callback = frame_callback
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("视频捕获已启动")
    
    def _capture_loop(self):
        """视频捕获循环"""
        while self.is_running:
            ret, frame = self.cap.read()
            
            if not ret:
                logger.warning("无法读取摄像头帧")
                time.sleep(0.1)
                continue
            
            # 更新当前帧
            with self.frame_lock:
                self.current_frame = frame.copy()
            
            # 调用回调函数处理帧
            if self.frame_callback:
                try:
                    self.frame_callback(frame)
                except Exception as e:
                    logger.error(f"帧处理回调函数执行失败: {e}")
            
            # 控制帧率
            time.sleep(1/30)  # 30 FPS
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        获取当前帧
        
        Returns:
            当前帧图像或None
        """
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def stop_capture(self):
        """停止视频捕获"""
        self.is_running = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        
        logger.info("视频捕获已停止")
    
    def release(self):
        """释放摄像头资源"""
        self.stop_capture()
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("摄像头资源已释放")
    
    def set_camera_properties(self, **kwargs):
        """
        设置摄像头属性
        
        Args:
            **kwargs: 摄像头属性参数
        """
        if not self.cap or not self.cap.isOpened():
            logger.warning("摄像头未初始化，无法设置属性")
            return
        
        property_map = {
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'hue': cv2.CAP_PROP_HUE,
            'gain': cv2.CAP_PROP_GAIN,
            'exposure': cv2.CAP_PROP_EXPOSURE,
            'fps': cv2.CAP_PROP_FPS,
            'width': cv2.CAP_PROP_FRAME_WIDTH,
            'height': cv2.CAP_PROP_FRAME_HEIGHT
        }
        
        for key, value in kwargs.items():
            if key in property_map:
                self.cap.set(property_map[key], value)
                logger.info(f"设置摄像头属性 {key} = {value}")
            else:
                logger.warning(f"未知的摄像头属性: {key}")
    
    def get_camera_info(self) -> dict:
        """
        获取摄像头信息
        
        Returns:
            摄像头信息字典
        """
        if not self.cap or not self.cap.isOpened():
            return {"status": "未初始化"}
        
        info = {
            "status": "已初始化",
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST),
            "saturation": self.cap.get(cv2.CAP_PROP_SATURATION),
            "gain": self.cap.get(cv2.CAP_PROP_GAIN),
            "exposure": self.cap.get(cv2.CAP_PROP_EXPOSURE)
        }
        
        return info
    
    def __del__(self):
        """析构函数，确保资源被正确释放"""
        self.release()

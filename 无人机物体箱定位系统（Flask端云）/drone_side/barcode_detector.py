"""
条形码检测模块
使用YOLO模型检测物体箱条形码，并使用pyzbar解码
"""
import cv2
import numpy as np
from ultralytics import YOLO
from pyzbar import pyzbar
import logging
from typing import List, Tuple, Optional
import config

logger = logging.getLogger(__name__)

class BarcodeDetector:
    def __init__(self, model_path: str = None):
        """
        初始化条形码检测器
        
        Args:
            model_path: YOLO模型路径
        """
        self.model_path = model_path or config.MODEL_PATH
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO模型加载成功: {self.model_path}")
        except Exception as e:
            logger.error(f"YOLO模型加载失败: {e}")
            raise
    
    def detect_barcodes(self, frame: np.ndarray) -> List[dict]:
        """
        检测图像中的条形码
        
        Args:
            frame: 输入图像
            
        Returns:
            检测到的条形码信息列表
        """
        barcodes = []
        
        try:
            # YOLO检测
            results = self.model(frame, conf=self.confidence_threshold)
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # 获取边界框坐标
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        
                        # 提取条形码区域
                        barcode_roi = frame[y1:y2, x1:x2]
                        
                        # 解码条形码
                        decoded_barcodes = pyzbar.decode(barcode_roi)
                        
                        for decoded in decoded_barcodes:
                            barcode_data = decoded.data.decode('utf-8')
                            barcode_type = decoded.type
                            
                            barcode_info = {
                                'data': barcode_data,
                                'type': barcode_type,
                                'bbox': (x1, y1, x2, y2),
                                'confidence': confidence,
                                'roi': barcode_roi
                            }
                            barcodes.append(barcode_info)
                            
                            logger.info(f"检测到条形码: {barcode_data}, 置信度: {confidence:.2f}")
        
        except Exception as e:
            logger.error(f"条形码检测失败: {e}")
        
        return barcodes
    
    def draw_detections(self, frame: np.ndarray, barcodes: List[dict]) -> np.ndarray:
        """
        在图像上绘制检测结果
        
        Args:
            frame: 原始图像
            barcodes: 检测到的条形码信息
            
        Returns:
            绘制了检测结果的图像
        """
        result_frame = frame.copy()
        
        for barcode in barcodes:
            x1, y1, x2, y2 = barcode['bbox']
            confidence = barcode['confidence']
            data = barcode['data']
            
            # 绘制边界框
            cv2.rectangle(result_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"{data} ({confidence:.2f})"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # 绘制标签背景
            cv2.rectangle(result_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), (0, 255, 0), -1)
            
            # 绘制标签文字
            cv2.putText(result_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return result_frame
    
    def preprocess_image(self, frame: np.ndarray) -> np.ndarray:
        """
        图像预处理
        
        Args:
            frame: 原始图像
            
        Returns:
            预处理后的图像
        """
        # 转换为RGB格式（YOLO需要）
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return frame

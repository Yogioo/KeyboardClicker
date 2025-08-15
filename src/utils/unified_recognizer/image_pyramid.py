# -*- coding: utf-8 -*-
"""
图像金字塔处理器

构建多尺度图像金字塔并提取基础特征图，为统一识别算法提供多层次的图像表示。
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

class ImagePyramid:
    """图像金字塔处理器"""
    
    def __init__(self, pyramid_levels: int = 4, scale_factor: float = 0.5):
        """
        初始化图像金字塔处理器
        
        Args:
            pyramid_levels: 金字塔层数
            scale_factor: 缩放因子
        """
        self._pyramid_levels = pyramid_levels
        self._scale_factor = scale_factor
        self._logger = logging.getLogger(__name__)
    
    #region 金字塔构建
    def BuildPyramid(self, image: np.ndarray) -> List[np.ndarray]:
        """
        构建多尺度图像金字塔
        
        Args:
            image: 输入图像 (BGR格式)
            
        Returns:
            金字塔图像列表，从原始尺寸到最小尺寸
        """
        try:
            if image is None or image.size == 0:
                raise ValueError("输入图像无效")
            
            pyramid = [image.copy()]
            current_image = image.copy()
            
            for level in range(1, self._pyramid_levels):
                # 计算新尺寸
                height, width = current_image.shape[:2]
                new_width = int(width * self._scale_factor)
                new_height = int(height * self._scale_factor)
                
                # 避免尺寸过小
                if new_width < 32 or new_height < 32:
                    break
                
                # 缩放图像
                scaled_image = cv2.resize(current_image, (new_width, new_height), 
                                        interpolation=cv2.INTER_AREA)
                pyramid.append(scaled_image)
                current_image = scaled_image
            
            self._logger.info(f"构建了{len(pyramid)}层金字塔")
            return pyramid
            
        except Exception as e:
            self._logger.error(f"构建金字塔失败: {e}")
            return [image]
    #endregion
    
    #region 特征提取
    def ExtractBaseFeatures(self, pyramid: List[np.ndarray]) -> Dict[int, Dict[str, np.ndarray]]:
        """
        统一计算基础特征图
        
        Args:
            pyramid: 图像金字塔
            
        Returns:
            每层的基础特征字典
        """
        try:
            features = {}
            
            for level, img in enumerate(pyramid):
                level_features = self._ExtractSingleLevelFeatures(img)
                features[level] = level_features
                
            return features
            
        except Exception as e:
            self._logger.error(f"提取基础特征失败: {e}")
            return {}
    
    def _ExtractSingleLevelFeatures(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        提取单层图像的基础特征
        
        Args:
            image: 输入图像
            
        Returns:
            特征字典
        """
        features = {}
        
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 边缘检测
            features['edges'] = cv2.Canny(gray, 50, 150)
            
            # 梯度计算
            gradient_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            gradient_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            features['gradient_x'] = gradient_x
            features['gradient_y'] = gradient_y
            features['gradient_mag'] = np.sqrt(gradient_x**2 + gradient_y**2)
            
            # 颜色空间转换
            if len(image.shape) == 3:
                features['hsv'] = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                features['lab'] = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            else:
                # 对于灰度图，创建伪HSV和LAB
                features['hsv'] = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
                features['lab'] = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
                features['hsv'][:,:,2] = gray  # V通道使用灰度值
                features['lab'][:,:,0] = gray  # L通道使用灰度值
            
            # 形态学特征
            kernel = np.ones((3,3), np.uint8)
            features['morphology_open'] = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            features['morphology_close'] = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # 纹理特征 - LBP简化版本
            features['texture'] = self._ComputeSimpleLBP(gray)
            
        except Exception as e:
            self._logger.error(f"提取单层特征失败: {e}")
        
        return features
    
    def _ComputeSimpleLBP(self, image: np.ndarray) -> np.ndarray:
        """
        计算简化的LBP特征
        
        Args:
            image: 灰度图像
            
        Returns:
            LBP特征图
        """
        try:
            rows, cols = image.shape
            lbp = np.zeros((rows-2, cols-2), dtype=np.uint8)
            
            for i in range(1, rows-1):
                for j in range(1, cols-1):
                    center = image[i, j]
                    code = 0
                    
                    # 8邻域LBP
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            code |= (1 << k)
                    
                    lbp[i-1, j-1] = code
            
            return lbp
            
        except Exception as e:
            self._logger.error(f"计算LBP失败: {e}")
            return np.zeros((image.shape[0]-2, image.shape[1]-2), dtype=np.uint8)
    #endregion
    
    #region 工具方法
    def GetPyramidInfo(self, pyramid: List[np.ndarray]) -> Dict[str, any]:
        """
        获取金字塔信息
        
        Args:
            pyramid: 图像金字塔
            
        Returns:
            金字塔信息字典
        """
        info = {
            'levels': len(pyramid),
            'scales': [],
            'sizes': [],
            'total_pixels': 0
        }
        
        original_size = pyramid[0].shape[:2] if pyramid else (0, 0)
        
        for level, img in enumerate(pyramid):
            size = img.shape[:2]
            scale = size[0] / original_size[0] if original_size[0] > 0 else 0
            
            info['scales'].append(scale)
            info['sizes'].append(size)
            info['total_pixels'] += size[0] * size[1]
        
        return info
    
    def GetLevelImage(self, pyramid: List[np.ndarray], level: int) -> Optional[np.ndarray]:
        """
        获取指定层的图像
        
        Args:
            pyramid: 图像金字塔
            level: 层级索引
            
        Returns:
            指定层的图像，如果层级无效则返回None
        """
        if 0 <= level < len(pyramid):
            return pyramid[level]
        return None
    #endregion
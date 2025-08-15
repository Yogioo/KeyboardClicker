# -*- coding: utf-8 -*-
"""
ROI检测器

用于检测屏幕变化区域，只处理发生变化的部分以提升性能。
"""

import cv2
import numpy as np
import time
from typing import List, Tuple, Optional, Dict, Any
import logging

class ROIDetector:
    """感兴趣区域检测器"""
    
    def __init__(self, 
                 change_threshold: float = 0.05,
                 min_roi_size: int = 50,
                 max_roi_count: int = 10,
                 merge_distance: int = 30):
        """
        初始化ROI检测器
        
        Args:
            change_threshold: 变化阈值，0-1之间
            min_roi_size: 最小ROI尺寸
            max_roi_count: 最大ROI数量
            merge_distance: ROI合并距离
        """
        self._change_threshold = change_threshold
        self._min_roi_size = min_roi_size
        self._max_roi_count = max_roi_count
        self._merge_distance = merge_distance
        
        self._previous_image = None
        self._previous_hash = None
        self._logger = logging.getLogger(__name__)
        
        # 性能统计
        self._stats = {
            'total_detections': 0,
            'roi_hits': 0,
            'full_screen_fallbacks': 0,
            'average_roi_count': 0,
            'average_roi_coverage': 0.0
        }
    
    def DetectROI(self, current_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        检测感兴趣区域
        
        Args:
            current_image: 当前图像
            
        Returns:
            ROI列表，每个ROI为(x, y, width, height)
        """
        start_time = time.time()
        self._stats['total_detections'] += 1
        
        try:
            # 如果没有历史图像，返回全屏
            if self._previous_image is None:
                self._previous_image = current_image.copy()
                self._stats['full_screen_fallbacks'] += 1
                return [(0, 0, current_image.shape[1], current_image.shape[0])]
            
            # 快速哈希检查
            current_hash = self._ComputeImageHash(current_image)
            if current_hash == self._previous_hash:
                # 图像没有变化，返回空ROI列表
                return []
            
            # 检测变化区域
            rois = self._DetectChangedRegions(self._previous_image, current_image)
            
            # 更新历史图像
            self._previous_image = current_image.copy()
            self._previous_hash = current_hash
            
            # 更新统计信息
            if rois:
                self._stats['roi_hits'] += 1
                self._stats['average_roi_count'] = (
                    (self._stats['average_roi_count'] * (self._stats['roi_hits'] - 1) + len(rois)) / 
                    self._stats['roi_hits']
                )
                
                # 计算ROI覆盖率
                total_area = current_image.shape[0] * current_image.shape[1]
                roi_area = sum(w * h for _, _, w, h in rois)
                coverage = roi_area / total_area
                self._stats['average_roi_coverage'] = (
                    (self._stats['average_roi_coverage'] * (self._stats['roi_hits'] - 1) + coverage) / 
                    self._stats['roi_hits']
                )
            else:
                self._stats['full_screen_fallbacks'] += 1
            
            detection_time = time.time() - start_time
            self._logger.debug(f"ROI检测完成: {len(rois)}个区域，耗时{detection_time:.3f}秒")
            
            return rois
            
        except Exception as e:
            self._logger.error(f"ROI检测失败: {e}")
            self._stats['full_screen_fallbacks'] += 1
            return [(0, 0, current_image.shape[1], current_image.shape[0])]
    
    def _ComputeImageHash(self, image: np.ndarray) -> str:
        """计算图像快速哈希"""
        # 缩小图像用于快速比较
        small_image = cv2.resize(image, (32, 32))
        if len(small_image.shape) == 3:
            small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
        
        # 计算均值哈希
        mean_val = np.mean(small_image)
        hash_bits = (small_image > mean_val).astype(np.uint8)
        return hash_bits.tobytes().hex()
    
    def _DetectChangedRegions(self, prev_image: np.ndarray, curr_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """检测变化区域"""
        # 确保图像尺寸一致
        if prev_image.shape != curr_image.shape:
            self._logger.warning("图像尺寸不一致，返回全屏")
            return [(0, 0, curr_image.shape[1], curr_image.shape[0])]
        
        # 转换为灰度图
        if len(prev_image.shape) == 3:
            prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(curr_image, cv2.COLOR_BGR2GRAY)
        else:
            prev_gray = prev_image
            curr_gray = curr_image
        
        # 计算差异
        diff = cv2.absdiff(prev_gray, curr_gray)
        
        # 应用阈值
        threshold_val = int(255 * self._change_threshold)
        _, binary_diff = cv2.threshold(diff, threshold_val, 255, cv2.THRESH_BINARY)
        
        # 形态学操作去噪
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        binary_diff = cv2.morphologyEx(binary_diff, cv2.MORPH_CLOSE, kernel)
        binary_diff = cv2.morphologyEx(binary_diff, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(binary_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 提取边界框
        rois = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # 过滤太小的区域
            if w >= self._min_roi_size and h >= self._min_roi_size:
                rois.append((x, y, w, h))
        
        # 合并相近的ROI
        rois = self._MergeNearbyROIs(rois)
        
        # 限制ROI数量
        if len(rois) > self._max_roi_count:
            # 按面积排序，保留最大的几个
            rois.sort(key=lambda roi: roi[2] * roi[3], reverse=True)
            rois = rois[:self._max_roi_count]
        
        # 如果变化区域太多或太大，回退到全屏
        if len(rois) > self._max_roi_count // 2:
            total_area = curr_image.shape[0] * curr_image.shape[1]
            roi_area = sum(w * h for _, _, w, h in rois)
            if roi_area / total_area > 0.5:  # 如果ROI覆盖超过50%，使用全屏
                return [(0, 0, curr_image.shape[1], curr_image.shape[0])]
        
        return rois
    
    def _MergeNearbyROIs(self, rois: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """合并相近的ROI"""
        if len(rois) <= 1:
            return rois
        
        merged = []
        used = set()
        
        for i, roi1 in enumerate(rois):
            if i in used:
                continue
            
            x1, y1, w1, h1 = roi1
            merged_roi = [x1, y1, x1 + w1, y1 + h1]  # [x1, y1, x2, y2]
            
            for j, roi2 in enumerate(rois[i+1:], i+1):
                if j in used:
                    continue
                
                x2, y2, w2, h2 = roi2
                
                # 检查是否相近
                if self._AreROIsNearby(roi1, roi2):
                    # 合并ROI
                    merged_roi[0] = min(merged_roi[0], x2)
                    merged_roi[1] = min(merged_roi[1], y2)
                    merged_roi[2] = max(merged_roi[2], x2 + w2)
                    merged_roi[3] = max(merged_roi[3], y2 + h2)
                    used.add(j)
            
            # 转换回(x, y, w, h)格式
            final_roi = (
                merged_roi[0], 
                merged_roi[1], 
                merged_roi[2] - merged_roi[0], 
                merged_roi[3] - merged_roi[1]
            )
            merged.append(final_roi)
            used.add(i)
        
        return merged
    
    def _AreROIsNearby(self, roi1: Tuple[int, int, int, int], roi2: Tuple[int, int, int, int]) -> bool:
        """检查两个ROI是否相近"""
        x1, y1, w1, h1 = roi1
        x2, y2, w2, h2 = roi2
        
        # 计算中心点距离
        center1 = (x1 + w1 // 2, y1 + h1 // 2)
        center2 = (x2 + w2 // 2, y2 + h2 // 2)
        
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        return distance <= self._merge_distance
    
    def ExtractROIImage(self, image: np.ndarray, roi: Tuple[int, int, int, int]) -> np.ndarray:
        """提取ROI区域图像"""
        x, y, w, h = roi
        
        # 确保ROI在图像范围内
        x = max(0, min(x, image.shape[1] - 1))
        y = max(0, min(y, image.shape[0] - 1))
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        return image[y:y+h, x:x+w]
    
    def GetStats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if self._stats['total_detections'] == 0:
            return {
                'total_detections': 0,
                'roi_hits': 0,
                'full_screen_fallbacks': 0,
                'average_roi_count': 0.0,
                'average_coverage': 0.0,
                'average_processing_time': 0.0,
                'roi_hit_rate': 0.0,
                'fallback_rate': 0.0
            }
        
        roi_hit_rate = self._stats['roi_hits'] / self._stats['total_detections']
        fallback_rate = self._stats['full_screen_fallbacks'] / self._stats['total_detections']
        
        return {
            'total_detections': self._stats['total_detections'],
            'roi_hits': self._stats['roi_hits'],
            'full_screen_fallbacks': self._stats['full_screen_fallbacks'],
            'average_roi_count': self._stats['average_roi_count'],
            'average_coverage': self._stats['average_roi_coverage'],
            'average_processing_time': 0.0,  # 暂时设为0，后续可以添加时间统计
            'roi_hit_rate': roi_hit_rate,
            'fallback_rate': fallback_rate
        }
    
    def Reset(self):
        """重置检测器状态"""
        self._previous_image = None
        self._previous_hash = None
        self._stats = {
            'total_detections': 0,
            'roi_hits': 0,
            'full_screen_fallbacks': 0,
            'average_roi_count': 0,
            'average_roi_coverage': 0.0
        }
    
    def UpdateConfig(self, 
                    change_threshold: Optional[float] = None,
                    min_roi_size: Optional[int] = None,
                    max_roi_count: Optional[int] = None,
                    merge_distance: Optional[int] = None):
        """更新配置参数"""
        if change_threshold is not None:
            self._change_threshold = change_threshold
        if min_roi_size is not None:
            self._min_roi_size = min_roi_size
        if max_roi_count is not None:
            self._max_roi_count = max_roi_count
        if merge_distance is not None:
            self._merge_distance = merge_distance
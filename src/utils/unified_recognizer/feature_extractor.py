# -*- coding: utf-8 -*-
"""
统一特征提取器

从图像金字塔中提取统一的特征描述符，为元素分类提供丰富的特征信息。
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging

try:
    from skimage import measure
except ImportError:
    # 如果scikit-image不可用，使用OpenCV替代
    measure = None

class FeatureExtractor:
    """统一特征提取器"""
    
    def __init__(self, min_area: int = 50, max_area: int = 100000):
        """
        初始化特征提取器
        
        Args:
            min_area: 最小区域面积
            max_area: 最大区域面积
        """
        self._min_area = min_area
        self._max_area = max_area
        self._logger = logging.getLogger(__name__)
    
    #region 统一特征提取
    def ExtractUnifiedFeatures(self, pyramid_features: Dict[int, Dict[str, np.ndarray]]) -> List[Dict[str, Any]]:
        """
        从金字塔特征中提取统一的描述符
        
        Args:
            pyramid_features: 金字塔特征字典
            
        Returns:
            统一特征向量列表
        """
        try:
            # 使用第0层（原始图像）进行区域分割
            if 0 not in pyramid_features:
                self._logger.error("金字塔特征中缺少第0层")
                return []
            
            level0_features = pyramid_features[0]
            regions = self._SegmentRegions(level0_features)
            
            unified_features = []
            for region in regions:
                feature_vector = self._ExtractRegionFeatures(region, pyramid_features)
                if feature_vector:
                    unified_features.append(feature_vector)
            
            self._logger.info(f"提取了{len(unified_features)}个特征向量")
            return unified_features
            
        except Exception as e:
            self._logger.error(f"提取统一特征失败: {e}")
            return []
    
    def ExtractLevelFeatures(self, level: int, level_features: Dict[str, np.ndarray]) -> List[Dict[str, Any]]:
        """
        提取单个金字塔层级的特征（用于并行处理）
        
        Args:
            level: 金字塔层级
            level_features: 该层级的特征字典
            
        Returns:
            该层级的特征向量列表
        """
        try:
            # 对于非第0层，使用简化的区域分割
            if level == 0:
                regions = self._SegmentRegions(level_features)
            else:
                # 对于其他层级，使用更简单的分割策略
                regions = self._SegmentRegionsSimple(level_features)
            
            level_features_list = []
            pyramid_features = {level: level_features}  # 构造单层金字塔
            
            for region in regions:
                feature_vector = self._ExtractRegionFeatures(region, pyramid_features)
                if feature_vector:
                    feature_vector['pyramid_level'] = level  # 添加层级信息
                    level_features_list.append(feature_vector)
            
            return level_features_list
            
        except Exception as e:
            self._logger.error(f"提取层级{level}特征失败: {e}")
            return []
    
    def _SegmentRegionsSimple(self, level_features: Dict[str, np.ndarray]) -> List[Any]:
        """
        简化的区域分割（用于非第0层）
        
        Args:
            level_features: 单层特征字典
            
        Returns:
            候选区域列表
        """
        try:
            regions = []
            
            # 使用边缘图进行简化分割
            edges = level_features.get('edges')
            if edges is None:
                return regions
            
            # 寻找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if self._min_area <= area <= self._max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    region = {
                        'contour': contour,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'centroid': self._GetCentroid(contour)
                    }
                    regions.append(region)
            
            return regions
            
        except Exception as e:
            self._logger.error(f"简化区域分割失败: {e}")
            return []
    
    def _SegmentRegions(self, level_features: Dict[str, np.ndarray]) -> List[Any]:
        """
        区域分割 - 统一找出所有候选区域
        
        Args:
            level_features: 单层特征字典
            
        Returns:
            候选区域列表
        """
        try:
            regions = []
            
            # 使用边缘图进行初始分割
            edges = level_features.get('edges')
            if edges is None:
                return regions
            
            # 形态学处理，连接断裂的边缘
            kernel = np.ones((3, 3), np.uint8)
            edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # 寻找轮廓
            contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                if self._min_area <= area <= self._max_area:
                    # 获取边界框
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    region = {
                        'contour': contour,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'centroid': self._GetCentroid(contour)
                    }
                    regions.append(region)
            
            # 使用基于连通组件的方法作为补充
            if measure is not None:
                gradient_mag = level_features.get('gradient_mag', np.zeros_like(edges))
                threshold_img = (gradient_mag > np.mean(gradient_mag) + np.std(gradient_mag)).astype(np.uint8)
                
                # 标记连通组件
                labels = measure.label(threshold_img, connectivity=2)
                component_regions = measure.regionprops(labels)
                
                for region_props in component_regions:
                    if self._min_area <= region_props.area <= self._max_area:
                        bbox = region_props.bbox  # (min_row, min_col, max_row, max_col)
                        x, y = bbox[1], bbox[0]
                        w, h = bbox[3] - bbox[1], bbox[2] - bbox[0]
                        
                        region = {
                            'region_props': region_props,
                            'bbox': (x, y, w, h),
                            'area': region_props.area,
                            'centroid': region_props.centroid
                        }
                        regions.append(region)
            else:
                # 使用OpenCV连通组件分析作为替代
                gradient_mag = level_features.get('gradient_mag', np.zeros_like(edges))
                threshold_img = (gradient_mag > np.mean(gradient_mag) + np.std(gradient_mag)).astype(np.uint8)
                
                # OpenCV连通组件分析
                num_labels, labels_im, stats, centroids = cv2.connectedComponentsWithStats(threshold_img, connectivity=8)
                
                for i in range(1, num_labels):  # 跳过背景
                    area = stats[i, cv2.CC_STAT_AREA]
                    if self._min_area <= area <= self._max_area:
                        x = stats[i, cv2.CC_STAT_LEFT]
                        y = stats[i, cv2.CC_STAT_TOP]
                        w = stats[i, cv2.CC_STAT_WIDTH]
                        h = stats[i, cv2.CC_STAT_HEIGHT]
                        
                        region = {
                            'bbox': (x, y, w, h),
                            'area': area,
                            'centroid': centroids[i]
                        }
                        regions.append(region)
            
            return regions
            
        except Exception as e:
            self._logger.error(f"区域分割失败: {e}")
            return []
    
    def _ExtractRegionFeatures(self, region: Dict[str, Any], pyramid_features: Dict[int, Dict[str, np.ndarray]]) -> Optional[Dict[str, Any]]:
        """
        提取单个区域的特征
        
        Args:
            region: 区域信息
            pyramid_features: 金字塔特征
            
        Returns:
            特征向量字典
        """
        try:
            bbox = region['bbox']
            x, y, w, h = bbox
            
            # 基础几何特征
            feature_vector = {
                'bbox': bbox,
                'area': region['area'],
                'aspect_ratio': w / h if h > 0 else 1.0,
                'extent': region['area'] / (w * h) if w * h > 0 else 0.0,
                'centroid': region['centroid']
            }
            
            # 从第0层提取详细特征
            level0_features = pyramid_features.get(0, {})
            if level0_features:
                self._AddGeometricFeatures(feature_vector, region, level0_features)
                self._AddTextureFeatures(feature_vector, bbox, level0_features)
                self._AddColorFeatures(feature_vector, bbox, level0_features)
                self._AddStructuralFeatures(feature_vector, bbox, level0_features)
            
            return feature_vector
            
        except Exception as e:
            self._logger.error(f"提取区域特征失败: {e}")
            return None
    #endregion
    
    #region 特征计算方法
    def _AddGeometricFeatures(self, feature_vector: Dict[str, Any], region: Dict[str, Any], features: Dict[str, np.ndarray]):
        """添加几何特征"""
        try:
            # 如果有轮廓信息，计算更多几何特征
            if 'contour' in region:
                contour = region['contour']
                
                # 凸包相关特征
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                feature_vector['solidity'] = region['area'] / hull_area if hull_area > 0 else 0.0
                
                # 紧密度
                perimeter = cv2.arcLength(contour, True)
                feature_vector['compactness'] = 4 * np.pi * region['area'] / (perimeter * perimeter) if perimeter > 0 else 0.0
                
            elif 'region_props' in region:
                region_props = region['region_props']
                feature_vector['solidity'] = region_props.solidity
                feature_vector['compactness'] = region_props.area / (region_props.perimeter ** 2) if region_props.perimeter > 0 else 0.0
                feature_vector['eccentricity'] = region_props.eccentricity
                feature_vector['orientation'] = region_props.orientation
                
        except Exception as e:
            self._logger.error(f"添加几何特征失败: {e}")
    
    def _AddTextureFeatures(self, feature_vector: Dict[str, Any], bbox: Tuple[int, int, int, int], features: Dict[str, np.ndarray]):
        """添加纹理特征"""
        try:
            x, y, w, h = bbox
            
            # 边缘密度
            edges = features.get('edges')
            if edges is not None:
                roi_edges = edges[y:y+h, x:x+w]
                edge_density = np.sum(roi_edges > 0) / (w * h) if w * h > 0 else 0.0
                feature_vector['edge_density'] = edge_density
            
            # 梯度方差
            gradient_mag = features.get('gradient_mag')
            if gradient_mag is not None:
                roi_gradient = gradient_mag[y:y+h, x:x+w]
                feature_vector['gradient_variance'] = np.var(roi_gradient)
                feature_vector['gradient_mean'] = np.mean(roi_gradient)
            
            # LBP纹理特征
            texture = features.get('texture')
            if texture is not None and texture.shape[0] > y and texture.shape[1] > x:
                # 调整ROI边界以适应纹理图像尺寸
                tex_h, tex_w = texture.shape
                roi_y = min(y, tex_h - 1)
                roi_x = min(x, tex_w - 1)
                roi_h = min(h, tex_h - roi_y)
                roi_w = min(w, tex_w - roi_x)
                
                if roi_h > 0 and roi_w > 0:
                    roi_texture = texture[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                    lbp_hist, _ = np.histogram(roi_texture.flatten(), bins=16, range=(0, 256))
                    feature_vector['lbp_histogram'] = lbp_hist / np.sum(lbp_hist) if np.sum(lbp_hist) > 0 else lbp_hist
                
        except Exception as e:
            self._logger.error(f"添加纹理特征失败: {e}")
    
    def _AddColorFeatures(self, feature_vector: Dict[str, Any], bbox: Tuple[int, int, int, int], features: Dict[str, np.ndarray]):
        """添加颜色特征"""
        try:
            x, y, w, h = bbox
            
            # HSV颜色特征
            hsv = features.get('hsv')
            if hsv is not None:
                roi_hsv = hsv[y:y+h, x:x+w]
                feature_vector['hue_mean'] = np.mean(roi_hsv[:,:,0])
                feature_vector['saturation_mean'] = np.mean(roi_hsv[:,:,1])
                feature_vector['value_mean'] = np.mean(roi_hsv[:,:,2])
                feature_vector['saturation_std'] = np.std(roi_hsv[:,:,1])
                
                # 色调直方图
                hue_hist, _ = np.histogram(roi_hsv[:,:,0].flatten(), bins=16, range=(0, 180))
                feature_vector['hue_histogram'] = hue_hist / np.sum(hue_hist) if np.sum(hue_hist) > 0 else hue_hist
            
            # LAB颜色特征
            lab = features.get('lab')
            if lab is not None:
                roi_lab = lab[y:y+h, x:x+w]
                feature_vector['lightness_mean'] = np.mean(roi_lab[:,:,0])
                feature_vector['a_channel_mean'] = np.mean(roi_lab[:,:,1])
                feature_vector['b_channel_mean'] = np.mean(roi_lab[:,:,2])
                
        except Exception as e:
            self._logger.error(f"添加颜色特征失败: {e}")
    
    def _AddStructuralFeatures(self, feature_vector: Dict[str, Any], bbox: Tuple[int, int, int, int], features: Dict[str, np.ndarray]):
        """添加结构特征"""
        try:
            x, y, w, h = bbox
            
            # 边界对比度
            edges = features.get('edges')
            if edges is not None:
                # 计算边界像素的对比度
                border_pixels = []
                roi_edges = edges[max(0,y-1):y+h+1, max(0,x-1):x+w+1]
                
                # 上下边界
                if roi_edges.shape[0] > 0:
                    border_pixels.extend(roi_edges[0, :].flatten())
                    if roi_edges.shape[0] > 1:
                        border_pixels.extend(roi_edges[-1, :].flatten())
                
                # 左右边界
                if roi_edges.shape[1] > 0:
                    border_pixels.extend(roi_edges[:, 0].flatten())
                    if roi_edges.shape[1] > 1:
                        border_pixels.extend(roi_edges[:, -1].flatten())
                
                if border_pixels:
                    feature_vector['border_contrast'] = np.mean(border_pixels) / 255.0
                else:
                    feature_vector['border_contrast'] = 0.0
            
            # 连通性特征
            gradient_mag = features.get('gradient_mag')
            if gradient_mag is not None:
                roi_gradient = gradient_mag[y:y+h, x:x+w]
                # 计算梯度的连通性
                threshold = np.mean(roi_gradient) + 0.5 * np.std(roi_gradient)
                binary_gradient = (roi_gradient > threshold).astype(np.uint8)
                
                # 连通组件数量
                num_labels, _ = cv2.connectedComponents(binary_gradient)
                feature_vector['connectivity'] = num_labels - 1  # 减去背景
                
            # 对称性评分（简化版）
            if 'gradient_mag' in features:
                roi_gradient = features['gradient_mag'][y:y+h, x:x+w]
                if roi_gradient.shape[0] > 1 and roi_gradient.shape[1] > 1:
                    # 水平对称性
                    left_half = roi_gradient[:, :roi_gradient.shape[1]//2]
                    right_half = roi_gradient[:, roi_gradient.shape[1]//2:]
                    right_half_flipped = np.fliplr(right_half)
                    
                    min_width = min(left_half.shape[1], right_half_flipped.shape[1])
                    if min_width > 0:
                        left_resized = left_half[:, :min_width]
                        right_resized = right_half_flipped[:, :min_width]
                        symmetry_score = 1.0 - np.mean(np.abs(left_resized - right_resized)) / 255.0
                        feature_vector['symmetry_score'] = max(0.0, symmetry_score)
                    else:
                        feature_vector['symmetry_score'] = 0.0
                else:
                    feature_vector['symmetry_score'] = 0.0
                    
        except Exception as e:
            self._logger.error(f"添加结构特征失败: {e}")
    #endregion
    
    #region 工具方法
    def _GetCentroid(self, contour: np.ndarray) -> Tuple[float, float]:
        """计算轮廓质心"""
        try:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = M["m10"] / M["m00"]
                cy = M["m01"] / M["m00"]
                return (cx, cy)
            else:
                return (0, 0)
        except:
            return (0, 0)
    
    def GetFeatureNames(self) -> List[str]:
        """获取所有特征名称"""
        return [
            'bbox', 'area', 'aspect_ratio', 'extent', 'centroid',
            'solidity', 'compactness', 'eccentricity', 'orientation',
            'edge_density', 'gradient_variance', 'gradient_mean', 'lbp_histogram',
            'hue_mean', 'saturation_mean', 'value_mean', 'saturation_std', 'hue_histogram',
            'lightness_mean', 'a_channel_mean', 'b_channel_mean',
            'border_contrast', 'connectivity', 'symmetry_score'
        ]
    #endregion
# -*- coding: utf-8 -*-
"""
统一视觉识别器

主要接口类，整合所有子模块提供统一的图像识别功能。
"""

import cv2
import numpy as np
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .recognition_config import UnifiedRecognitionConfig
from .image_pyramid import ImagePyramid
from .feature_extractor import FeatureExtractor
from .element_classifier import ElementClassifier
from .spatial_analyzer import SpatialAnalyzer
from .roi_detector import ROIDetector
from .advanced_cache import AdvancedCache

class FeatureCache:
    """多层特征缓存"""
    
    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._pyramid_cache = {}
        self._feature_cache = {}
        self._result_cache = {}
        self._access_times = {}
    
    def _GetImageHash(self, image: np.ndarray) -> str:
        """计算图像哈希值"""
        # 对图像进行快速哈希，使用更小的尺寸提升速度
        small_image = cv2.resize(image, (16, 16))
        # 转换为灰度图进一步减少计算量
        if len(small_image.shape) == 3:
            small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2GRAY)
        image_bytes = small_image.tobytes()
        return hashlib.md5(image_bytes).hexdigest()
    
    def GetCachedPyramid(self, image: np.ndarray) -> Optional[List[np.ndarray]]:
        """获取缓存的金字塔"""
        image_hash = self._GetImageHash(image)
        if image_hash in self._pyramid_cache:
            self._access_times[image_hash] = time.time()
            return self._pyramid_cache[image_hash]
        return None
    
    def CachePyramid(self, image: np.ndarray, pyramid: List[np.ndarray]):
        """缓存金字塔"""
        if len(self._pyramid_cache) >= self._max_size:
            self._EvictOldest()
        
        image_hash = self._GetImageHash(image)
        self._pyramid_cache[image_hash] = pyramid
        self._access_times[image_hash] = time.time()
    
    def GetCachedFeatures(self, region_id: str) -> Optional[Dict[str, Any]]:
        """获取缓存的特征"""
        if region_id in self._feature_cache:
            return self._feature_cache[region_id]
        return None
    
    def CacheFeatures(self, region_id: str, features: Dict[str, Any]):
        """缓存区域特征"""
        if len(self._feature_cache) >= self._max_size:
            self._EvictOldest()
        
        self._feature_cache[region_id] = features
    
    def GetCachedResults(self, image: np.ndarray) -> Optional[List[Dict[str, Any]]]:
        """获取缓存的结果"""
        image_hash = self._GetImageHash(image)
        if image_hash in self._result_cache:
            self._access_times[image_hash] = time.time()
            return self._result_cache[image_hash]
        return None
    
    def CacheResults(self, image: np.ndarray, results: List[Dict[str, Any]]):
        """缓存识别结果"""
        if len(self._result_cache) >= self._max_size:
            self._EvictOldest()
        
        image_hash = self._GetImageHash(image)
        self._result_cache[image_hash] = results
        self._access_times[image_hash] = time.time()
    
    def _EvictOldest(self):
        """淘汰最旧的缓存项"""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        
        # 从所有缓存中删除
        self._pyramid_cache.pop(oldest_key, None)
        self._result_cache.pop(oldest_key, None)
        self._access_times.pop(oldest_key, None)
    
    def Clear(self):
        """清空所有缓存"""
        self._pyramid_cache.clear()
        self._feature_cache.clear()
        self._result_cache.clear()
        self._access_times.clear()

class UnifiedVisualRecognizer:
    """统一视觉识别器 - 主要接口类"""
    
    def __init__(self, config: Optional[UnifiedRecognitionConfig] = None):
        """
        初始化统一视觉识别器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self._config = config or UnifiedRecognitionConfig()
        self._logger = logging.getLogger(__name__)
        
        # 初始化子模块
        self._InitializeModules()
        
        # 初始化高级缓存系统
        self._cache = None
        if self._config.performance.enable_caching:
            self._cache = AdvancedCache(
                max_size=self._config.performance.max_cache_size,
                max_memory_mb=min(512, self._config.performance.max_cache_size * 2),  # 动态内存限制
                ttl_seconds=3600,  # 1小时TTL
                enable_memory_monitoring=True
            )
        
        # 初始化ROI检测器
        self._roi_detector = None
        if self._config.performance.enable_roi_detection:
            self._roi_detector = ROIDetector(
                change_threshold=self._config.performance.roi_change_threshold,
                min_roi_size=self._config.performance.roi_min_size,
                max_roi_count=self._config.performance.roi_max_count,
                merge_distance=self._config.performance.roi_merge_distance
            )
        
        # 性能统计
        self._performance_stats = {
            'total_recognitions': 0,
            'cache_hits': 0,
            'roi_hits': 0,
            'average_time': 0.0,
            'last_recognition_time': 0.0,
            'average_roi_coverage': 0.0
        }
        
        self._logger.info("统一视觉识别器初始化完成")
    
    #region 初始化
    def _InitializeModules(self):
        """初始化子模块"""
        try:
            # 获取配置
            pyramid_config = self._config.GetPyramidConfig()
            seg_config = self._config.GetSegmentationConfig()
            spatial_config = self._config.GetSpatialConfig()
            
            # 初始化模块
            self._pyramid_processor = ImagePyramid(
                pyramid_levels=pyramid_config.levels,
                scale_factor=pyramid_config.scale_factor
            )
            
            self._feature_extractor = FeatureExtractor(
                min_area=seg_config.min_region_area,
                max_area=seg_config.max_region_area
            )
            
            self._classifier = ElementClassifier()
            
            self._spatial_analyzer = SpatialAnalyzer(
                overlap_threshold=spatial_config.overlap_threshold,
                semantic_distance_threshold=spatial_config.semantic_distance_threshold
            )
            
            # 同步分类阈值
            classification_config = self._config.GetClassificationConfig()
            if classification_config.thresholds:
                for element_type, threshold in classification_config.thresholds.items():
                    self._classifier.SetThreshold(element_type, threshold)
            
        except Exception as e:
            self._logger.error(f"初始化子模块失败: {e}")
            raise
    #endregion
    
    #region 主要接口
    def DetectClickableElements(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        统一检测接口 - 兼容现有API
        
        Args:
            image: 输入图像 (BGR格式)
            
        Returns:
            检测结果列表，每个元素包含type, bbox, confidence等信息
        """
        start_time = time.time()
        
        try:
            # 输入验证
            if image is None or image.size == 0:
                self._logger.error("输入图像无效")
                return []
            
            # 检查缓存
            if self._cache:
                cached_results = self._cache.get_cached_results(image)
                if cached_results is not None:
                    self._performance_stats['cache_hits'] += 1
                    self._logger.info("使用缓存结果")
                    return cached_results
            
            # ROI检测优化
            if self._roi_detector:
                rois = self._roi_detector.DetectROI(image)
                if not rois:  # 没有变化，返回空结果
                    self._logger.info("未检测到屏幕变化，跳过处理")
                    return []
                
                # 如果ROI覆盖面积较小，使用ROI处理
                total_area = image.shape[0] * image.shape[1]
                roi_area = sum(w * h for _, _, w, h in rois)
                roi_coverage = roi_area / total_area
                
                if roi_coverage < 0.7 and len(rois) <= 5:  # ROI优化阈值
                    self._performance_stats['roi_hits'] += 1
                    self._performance_stats['average_roi_coverage'] = (
                        (self._performance_stats['average_roi_coverage'] * (self._performance_stats['roi_hits'] - 1) + roi_coverage) / 
                        self._performance_stats['roi_hits']
                    )
                    return self._ProcessROIs(image, rois)
            
            # 全屏处理流程
            return self._ProcessFullScreen(image, start_time)
            
        except Exception as e:
            self._logger.error(f"检测失败: {e}")
            return []
    
    def _ProcessROIs(self, image: np.ndarray, rois: List[Tuple[int, int, int, int]]) -> List[Dict[str, Any]]:
        """处理ROI区域"""
        all_results = []
        
        for roi in rois:
            x, y, w, h = roi
            
            # 提取ROI图像
            roi_image = self._roi_detector.ExtractROIImage(image, roi)
            if roi_image.size == 0:
                continue
            
            # 对ROI进行识别
            roi_results = self._ProcessSingleROI(roi_image, x, y)
            
            # 调整坐标到全图坐标系
            for result in roi_results:
                if 'bbox' in result:
                    bbox = result['bbox']
                    result['bbox'] = (bbox[0] + x, bbox[1] + y, bbox[2], bbox[3])
            
            all_results.extend(roi_results)
        
        # 对所有结果进行空间关系优化
        if all_results:
            all_results = self._spatial_analyzer.OptimizeSpatialRelationships(all_results)
            all_results = self._PostProcessResults(all_results)
        
        self._logger.info(f"ROI处理完成: {len(rois)}个区域，检测到{len(all_results)}个元素")
        return all_results
    
    def _ProcessSingleROI(self, roi_image: np.ndarray, offset_x: int, offset_y: int) -> List[Dict[str, Any]]:
        """处理单个ROI区域"""
        try:
            # 1. 构建图像金字塔
            pyramid = self._pyramid_processor.BuildPyramid(roi_image)
            if not pyramid:
                return []
            
            # 2. 提取基础特征
            pyramid_features = self._pyramid_processor.ExtractBaseFeatures(pyramid)
            if not pyramid_features:
                return []
            
            # 3. 提取统一特征
            unified_features = self._feature_extractor.ExtractUnifiedFeatures(pyramid_features)
            if not unified_features:
                return []
            
            # 4. 元素分类
            classified_elements = self._classifier.ClassifyElements(unified_features)
            
            return classified_elements
            
        except Exception as e:
            self._logger.warning(f"ROI处理失败 ({offset_x}, {offset_y}): {e}")
            return []
    
    def _ProcessFullScreen(self, image: np.ndarray, start_time: float) -> List[Dict[str, Any]]:
        """全屏处理流程"""
        # 1. 构建图像金字塔
        pyramid = self._BuildPyramidWithCache(image)
        if not pyramid:
            self._logger.error("构建金字塔失败")
            return []
        
        # 2. 提取基础特征
        pyramid_features = self._pyramid_processor.ExtractBaseFeatures(pyramid)
        if not pyramid_features:
            self._logger.error("提取基础特征失败")
            return []
        
        # 3. 提取统一特征
        unified_features = self._ExtractUnifiedFeaturesParallel(pyramid_features)
        if not unified_features:
            self._logger.info("未检测到有效特征")
            return []
        
        # 4. 元素分类
        classified_elements = self._classifier.ClassifyElements(unified_features)
        if not classified_elements:
            self._logger.info("未分类出任何元素")
            return []
        
        # 5. 空间关系优化
        final_results = self._spatial_analyzer.OptimizeSpatialRelationships(classified_elements)
        
        # 6. 后处理
        final_results = self._PostProcessResults(final_results)
        
        # 缓存结果
        if self._cache:
            self._cache.cache_results(image, final_results)
        
        # 更新性能统计
        recognition_time = time.time() - start_time
        self._UpdatePerformanceStats(recognition_time)
        
        self._logger.info(f"全屏识别完成: 检测到{len(final_results)}个元素，耗时{recognition_time:.3f}秒")
        return final_results
    
    def DetectSingleType(self, element_type: str, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        单类型检测接口 - 兼容现有调试功能
        
        Args:
            element_type: 元素类型 ('button', 'icon', 'text', 'link', 'input')
            image: 输入图像
            
        Returns:
            指定类型的检测结果
        """
        try:
            # 检查元素类型是否支持
            supported_types = self._classifier.GetSupportedTypes()
            if element_type not in supported_types:
                self._logger.error(f"不支持的元素类型: {element_type}")
                return []
            
            # 使用统一检测然后过滤
            all_elements = self.DetectClickableElements(image)
            filtered_results = [elem for elem in all_elements if elem['type'] == element_type]
            
            self._logger.info(f"单类型检测({element_type}): 检测到{len(filtered_results)}个元素")
            return filtered_results
            
        except Exception as e:
            self._logger.error(f"单类型检测失败: {e}")
            return []
    
    def DetectMultipleTypes(self, element_types: List[str], image: np.ndarray) -> Dict[str, List[Dict[str, Any]]]:
        """
        多类型检测接口
        
        Args:
            element_types: 元素类型列表
            image: 输入图像
            
        Returns:
            按类型分组的检测结果字典
        """
        try:
            all_elements = self.DetectClickableElements(image)
            
            results = {}
            for element_type in element_types:
                results[element_type] = [elem for elem in all_elements if elem['type'] == element_type]
            
            return results
            
        except Exception as e:
            self._logger.error(f"多类型检测失败: {e}")
            return {element_type: [] for element_type in element_types}
    #endregion
    
    #region 优化方法
    def _BuildPyramidWithCache(self, image: np.ndarray) -> List[np.ndarray]:
        """带缓存的金字塔构建"""
        if self._cache:
            cached_pyramid = self._cache.get_cached_pyramid(image)
            if cached_pyramid is not None:
                return cached_pyramid
        
        pyramid = self._pyramid_processor.BuildPyramid(image)
        
        if self._cache and pyramid:
            self._cache.cache_pyramid(image, pyramid)
        
        return pyramid
    
    def _ExtractUnifiedFeaturesParallel(self, pyramid_features: Dict[int, Dict[str, np.ndarray]]) -> List[Dict[str, Any]]:
        """并行特征提取"""
        if not self._config.performance.parallel_feature_extraction:
            return self._feature_extractor.ExtractUnifiedFeatures(pyramid_features)
        
        try:
            max_workers = min(self._config.performance.max_threads, 4)
            
            # 如果金字塔层数较少，直接使用单线程
            if len(pyramid_features) <= 2:
                return self._feature_extractor.ExtractUnifiedFeatures(pyramid_features)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 按金字塔层级并行处理特征提取
                futures = {}
                for level, features in pyramid_features.items():
                    future = executor.submit(self._feature_extractor.ExtractLevelFeatures, level, features)
                    futures[level] = future
                
                # 收集结果
                level_results = {}
                for level, future in futures.items():
                    try:
                        level_results[level] = future.result(timeout=10)  # 10秒超时
                    except Exception as e:
                        self._logger.warning(f"层级{level}特征提取失败: {e}")
                        level_results[level] = []
                
                # 合并所有层级的结果
                all_features = []
                for level in sorted(level_results.keys()):
                    all_features.extend(level_results[level])
                
                return all_features
                
        except Exception as e:
            self._logger.error(f"并行特征提取失败，回退到单线程: {e}")
            return self._feature_extractor.ExtractUnifiedFeatures(pyramid_features)
    
    def _PostProcessResults(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """后处理结果"""
        try:
            processed_results = []
            
            for result in results:
                # 确保bbox格式正确
                bbox = result.get('bbox')
                if bbox and len(bbox) == 4:
                    x, y, w, h = bbox
                    # 确保坐标为正整数
                    x, y, w, h = max(0, int(x)), max(0, int(y)), max(1, int(w)), max(1, int(h))
                    result['bbox'] = (x, y, w, h)
                    
                    # 计算中心点
                    result['center'] = (x + w // 2, y + h // 2)
                    
                    # 添加面积信息
                    result['area'] = w * h
                    
                    # 确保置信度在有效范围内
                    confidence = result.get('confidence', 0)
                    result['confidence'] = max(0.0, min(1.0, float(confidence)))
                    
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self._logger.error(f"后处理失败: {e}")
            return results
    
    def _UpdatePerformanceStats(self, recognition_time: float):
        """更新性能统计"""
        self._performance_stats['total_recognitions'] += 1
        self._performance_stats['last_recognition_time'] = recognition_time
        
        # 计算平均时间（使用滑动平均）
        total = self._performance_stats['total_recognitions']
        old_avg = self._performance_stats['average_time']
        self._performance_stats['average_time'] = (old_avg * (total - 1) + recognition_time) / total
    #endregion
    
    #region 配置和管理接口
    def UpdateConfig(self, new_config: UnifiedRecognitionConfig):
        """
        更新配置
        
        Args:
            new_config: 新的配置对象
        """
        try:
            self._config = new_config
            self._InitializeModules()
            
            # 更新缓存设置
            if self._config.performance.enable_caching:
                if self._cache is None:
                    self._cache = FeatureCache(self._config.performance.max_cache_size)
            else:
                self._cache = None
            
            self._logger.info("配置更新完成")
            
        except Exception as e:
            self._logger.error(f"更新配置失败: {e}")
    
    def GetConfig(self) -> UnifiedRecognitionConfig:
        """获取当前配置"""
        return self._config
    
    def GetPerformanceStats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        stats = self._performance_stats.copy()
        
        # 添加缓存统计
        if self._cache:
            cache_hit_rate = 0.0
            if stats['total_recognitions'] > 0:
                cache_hit_rate = stats['cache_hits'] / stats['total_recognitions']
            stats['cache_hit_rate'] = cache_hit_rate
            
            # 添加高级缓存的详细统计
            cache_stats = self._cache.get_stats()
            stats.update({
                'cache_pyramid_hits': cache_stats.pyramid_hits,
                'cache_pyramid_misses': cache_stats.pyramid_misses,
                'cache_feature_hits': cache_stats.feature_hits,
                'cache_feature_misses': cache_stats.feature_misses,
                'cache_result_hits': cache_stats.result_hits,
                'cache_result_misses': cache_stats.result_misses,
                'cache_evictions': cache_stats.evictions,
                'cache_memory_usage_mb': cache_stats.memory_usage_mb,
                'cache_total_entries': cache_stats.total_entries
            })
        else:
            stats['cache_hit_rate'] = 0.0
        
        return stats
    
    def ClearCache(self):
        """清空缓存"""
        if self._cache:
            self._cache.clear()
            self._logger.info("缓存已清空")
    
    def ResetPerformanceStats(self):
        """重置性能统计"""
        self._performance_stats = {
            'total_recognitions': 0,
            'cache_hits': 0,
            'average_time': 0.0,
            'last_recognition_time': 0.0
        }
        self._logger.info("性能统计已重置")
    #endregion
    
    #region 调试和诊断接口
    def DiagnoseImage(self, image: np.ndarray) -> Dict[str, Any]:
        """
        诊断图像处理过程
        
        Args:
            image: 输入图像
            
        Returns:
            诊断信息字典
        """
        try:
            diagnosis = {
                'image_info': {
                    'shape': image.shape,
                    'dtype': str(image.dtype),
                    'size_mb': image.nbytes / (1024 * 1024)
                },
                'pyramid_info': {},
                'feature_count': 0,
                'classification_results': {},
                'processing_times': {}
            }
            
            # 1. 分析金字塔
            start_time = time.time()
            pyramid = self._pyramid_processor.BuildPyramid(image)
            diagnosis['processing_times']['pyramid'] = time.time() - start_time
            diagnosis['pyramid_info'] = self._pyramid_processor.GetPyramidInfo(pyramid)
            
            # 2. 分析特征提取
            start_time = time.time()
            pyramid_features = self._pyramid_processor.ExtractBaseFeatures(pyramid)
            unified_features = self._feature_extractor.ExtractUnifiedFeatures(pyramid_features)
            diagnosis['processing_times']['feature_extraction'] = time.time() - start_time
            diagnosis['feature_count'] = len(unified_features)
            
            # 3. 分析分类结果
            start_time = time.time()
            for element_type in self._classifier.GetSupportedTypes():
                type_results = self._classifier.ClassifySingleType(element_type, unified_features)
                diagnosis['classification_results'][element_type] = len(type_results)
            diagnosis['processing_times']['classification'] = time.time() - start_time
            
            return diagnosis
            
        except Exception as e:
            self._logger.error(f"图像诊断失败: {e}")
            return {'error': str(e)}
    
    def GetFeatureNames(self) -> List[str]:
        """获取所有特征名称"""
        return self._feature_extractor.GetFeatureNames()
    
    def GetSupportedElementTypes(self) -> List[str]:
        """获取支持的元素类型"""
        return self._classifier.GetSupportedTypes()
    #endregion
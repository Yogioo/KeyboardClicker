# -*- coding: utf-8 -*-
"""
统一识别配置

提供统一的配置管理，支持参数调整和性能优化选项。
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

@dataclass
class PyramidConfig:
    """图像金字塔配置"""
    levels: int = 4
    scale_factor: float = 0.5
    min_size: int = 32

@dataclass
class SegmentationConfig:
    """分割配置"""
    min_region_area: int = 50
    max_region_area: int = 100000
    edge_threshold_low: int = 50
    edge_threshold_high: int = 150
    morphology_kernel_size: int = 3

@dataclass
class ClassificationConfig:
    """分类配置"""
    thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.thresholds is None:
            self.thresholds = {
                'button': 0.4,
                'icon': 0.35,
                'text': 0.3,
                'link': 0.35,
                'input': 0.4
            }

@dataclass
class SpatialConfig:
    """空间分析配置"""
    overlap_threshold: float = 0.3
    semantic_distance_threshold: int = 50
    density_check_radius: int = 100
    max_nearby_elements: int = 10

@dataclass
class PerformanceConfig:
    """性能配置"""
    enable_caching: bool = True
    max_cache_size: int = 100
    parallel_feature_extraction: bool = True
    max_threads: int = 4
    memory_limit_mb: int = 512
    
    # ROI检测配置
    enable_roi_detection: bool = True
    roi_change_threshold: float = 0.05
    roi_min_size: int = 50
    roi_max_count: int = 8
    roi_merge_distance: int = 30
    roi_coverage_threshold: float = 0.7

class UnifiedRecognitionConfig:
    """统一识别配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，如果为None则使用默认配置
        """
        self._logger = logging.getLogger(__name__)
        
        # 初始化默认配置
        self.pyramid = PyramidConfig()
        self.segmentation = SegmentationConfig()
        self.classification = ClassificationConfig()
        self.spatial = SpatialConfig()
        self.performance = PerformanceConfig()
        
        # 如果提供了配置文件，尝试加载
        if config_file and os.path.exists(config_file):
            self.LoadFromFile(config_file)
    
    #region 配置加载和保存
    def LoadFromFile(self, config_file: str) -> bool:
        """
        从文件加载配置
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._UpdateFromDict(config_data)
            self._logger.info(f"从文件加载配置: {config_file}")
            return True
            
        except Exception as e:
            self._logger.error(f"加载配置文件失败: {e}")
            return False
    
    def SaveToFile(self, config_file: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            是否保存成功
        """
        try:
            config_data = self.ToDict()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._logger.info(f"配置已保存到文件: {config_file}")
            return True
            
        except Exception as e:
            self._logger.error(f"保存配置文件失败: {e}")
            return False
    
    def _UpdateFromDict(self, config_data: Dict[str, Any]):
        """从字典更新配置"""
        try:
            if 'pyramid' in config_data:
                pyramid_data = config_data['pyramid']
                self.pyramid = PyramidConfig(**pyramid_data)
            
            if 'segmentation' in config_data:
                seg_data = config_data['segmentation']
                self.segmentation = SegmentationConfig(**seg_data)
            
            if 'classification' in config_data:
                cls_data = config_data['classification']
                self.classification = ClassificationConfig(**cls_data)
            
            if 'spatial' in config_data:
                spatial_data = config_data['spatial']
                self.spatial = SpatialConfig(**spatial_data)
            
            if 'performance' in config_data:
                perf_data = config_data['performance']
                self.performance = PerformanceConfig(**perf_data)
                
        except Exception as e:
            self._logger.error(f"更新配置失败: {e}")
    
    def ToDict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'pyramid': asdict(self.pyramid),
            'segmentation': asdict(self.segmentation),
            'classification': asdict(self.classification),
            'spatial': asdict(self.spatial),
            'performance': asdict(self.performance)
        }
    #endregion
    
    #region 配置访问接口
    def GetPyramidConfig(self) -> PyramidConfig:
        """获取图像金字塔配置"""
        return self.pyramid
    
    def GetSegmentationConfig(self) -> SegmentationConfig:
        """获取分割配置"""
        return self.segmentation
    
    def GetClassificationConfig(self) -> ClassificationConfig:
        """获取分类配置"""
        return self.classification
    
    def GetSpatialConfig(self) -> SpatialConfig:
        """获取空间分析配置"""
        return self.spatial
    
    def GetPerformanceConfig(self) -> PerformanceConfig:
        """获取性能配置"""
        return self.performance
    #endregion
    
    #region 配置修改接口
    def SetClassificationThreshold(self, element_type: str, threshold: float):
        """
        设置分类阈值
        
        Args:
            element_type: 元素类型
            threshold: 阈值
        """
        if self.classification.thresholds is None:
            self.classification.thresholds = {}
        self.classification.thresholds[element_type] = threshold
    
    def SetOverlapThreshold(self, threshold: float):
        """设置重叠阈值"""
        self.spatial.overlap_threshold = threshold
    
    def SetSemanticDistanceThreshold(self, threshold: int):
        """设置语义距离阈值"""
        self.spatial.semantic_distance_threshold = threshold
    
    def SetMinRegionArea(self, area: int):
        """设置最小区域面积"""
        self.segmentation.min_region_area = area
    
    def SetMaxRegionArea(self, area: int):
        """设置最大区域面积"""
        self.segmentation.max_region_area = area
    
    def SetPyramidLevels(self, levels: int):
        """设置金字塔层数"""
        self.pyramid.levels = levels
    
    def SetScaleFactor(self, factor: float):
        """设置缩放因子"""
        self.pyramid.scale_factor = factor
    
    def EnableCaching(self, enabled: bool):
        """启用/禁用缓存"""
        self.performance.enable_caching = enabled
    
    def SetMaxCacheSize(self, size: int):
        """设置最大缓存大小"""
        self.performance.max_cache_size = size
    
    def EnableParallelProcessing(self, enabled: bool):
        """启用/禁用并行处理"""
        self.performance.parallel_feature_extraction = enabled
    
    def SetMaxThreads(self, threads: int):
        """设置最大线程数"""
        self.performance.max_threads = threads
    
    def EnableROIDetection(self, enabled: bool):
        """启用或禁用ROI检测"""
        self.performance.enable_roi_detection = enabled
    
    def SetROIChangeThreshold(self, threshold: float):
        """设置ROI变化检测阈值"""
        self.performance.roi_change_threshold = max(0.01, min(1.0, threshold))
    
    def SetROIMinSize(self, size: int):
        """设置ROI最小尺寸"""
        self.performance.roi_min_size = max(10, size)
    
    def SetROIMaxCount(self, count: int):
        """设置最大ROI数量"""
        self.performance.roi_max_count = max(1, min(20, count))
    
    def SetROIMergeDistance(self, distance: int):
        """设置ROI合并距离"""
        self.performance.roi_merge_distance = max(5, distance)
    
    def SetROICoverageThreshold(self, threshold: float):
        """设置ROI覆盖阈值"""
        self.performance.roi_coverage_threshold = max(0.1, min(1.0, threshold))
    #endregion
    
    #region 预设配置
    def LoadFastConfig(self):
        """加载快速识别配置"""
        # 金字塔配置 - 大幅减少层数和增大缩放因子以提高速度
        self.pyramid.levels = 1  # 只使用单层，避免多层处理开销
        self.pyramid.scale_factor = 0.8  # 更大的缩放因子
        self.pyramid.min_size = 64  # 进一步增大最小尺寸
        
        # 分割配置 - 大幅增大最小区域面积以减少候选区域
        self.segmentation.min_region_area = 300  # 大幅增加最小区域
        self.segmentation.max_region_area = 30000  # 减少最大区域
        self.segmentation.edge_threshold_low = 80  # 更高的边缘阈值
        self.segmentation.edge_threshold_high = 200
        self.segmentation.morphology_kernel_size = 1  # 最小核大小
        
        # 性能配置 - 禁用并行处理以避免开销
        self.performance.parallel_feature_extraction = False  # 禁用并行处理
        self.performance.max_threads = 1  # 单线程处理
        self.performance.enable_caching = True
        self.performance.max_cache_size = 50  # 减小缓存以节省内存
        self.performance.memory_limit_mb = 128  # 更严格的内存限制
        
        # 空间配置 - 大幅放宽约束以减少计算
        self.spatial.overlap_threshold = 0.5  # 更大的重叠阈值
        self.spatial.semantic_distance_threshold = 80  # 增大距离阈值
        self.spatial.density_check_radius = 60  # 减小检查半径
        self.spatial.max_nearby_elements = 5  # 大幅减少最大邻近元素数
        
        # 大幅降低分类阈值以快速通过
        self.classification.thresholds = {
            'button': 0.15,  # 更低的阈值
            'icon': 0.1,
            'text': 0.05,
            'link': 0.1,
            'input': 0.15
        }
        
        # ROI检测配置 - 启用以提高速度
        self.performance.enable_roi_detection = True
        self.performance.roi_change_threshold = 0.1  # 更高的变化阈值，减少ROI数量
        self.performance.roi_min_size = 100  # 更大的最小ROI尺寸
        self.performance.roi_max_count = 4  # 减少最大ROI数量
        self.performance.roi_merge_distance = 50  # 增大合并距离
        self.performance.roi_coverage_threshold = 0.8  # 更高的覆盖阈值
        
        self._logger.info("已加载极速识别配置")
    
    def LoadAccurateConfig(self):
        """加载精确识别配置"""
        self.pyramid.levels = 4
        self.pyramid.scale_factor = 0.5
        self.segmentation.min_region_area = 50
        self.segmentation.max_region_area = 100000
        self.performance.parallel_feature_extraction = False
        
        # 提高阈值以保证精度
        self.classification.thresholds = {
            'button': 0.5,
            'icon': 0.45,
            'text': 0.4,
            'link': 0.45,
            'input': 0.5
        }
        
        # ROI检测配置 - 精确模式
        self.performance.enable_roi_detection = True
        self.performance.roi_change_threshold = 0.02  # 更低的变化阈值，检测更细微变化
        self.performance.roi_min_size = 30  # 更小的最小ROI尺寸
        self.performance.roi_max_count = 12  # 更多的ROI数量
        self.performance.roi_merge_distance = 20  # 更小的合并距离
        self.performance.roi_coverage_threshold = 0.5  # 更低的覆盖阈值
        
        self._logger.info("已加载精确识别配置")
    
    def LoadBalancedConfig(self):
        """加载平衡配置（默认）"""
        self.__init__()  # 重置为默认配置
        self._logger.info("已加载平衡配置")
    #endregion
    
    #region 配置验证
    def ValidateConfig(self) -> List[str]:
        """
        验证配置参数的有效性
        
        Returns:
            错误信息列表，空列表表示配置有效
        """
        errors = []
        
        # 验证金字塔配置
        if self.pyramid.levels < 1 or self.pyramid.levels > 10:
            errors.append("金字塔层数必须在1-10之间")
        
        if self.pyramid.scale_factor <= 0 or self.pyramid.scale_factor >= 1:
            errors.append("缩放因子必须在0-1之间")
        
        if self.pyramid.min_size < 16:
            errors.append("最小尺寸不能小于16像素")
        
        # 验证分割配置
        if self.segmentation.min_region_area <= 0:
            errors.append("最小区域面积必须大于0")
        
        if self.segmentation.max_region_area <= self.segmentation.min_region_area:
            errors.append("最大区域面积必须大于最小区域面积")
        
        # 验证分类配置
        if self.classification.thresholds:
            for element_type, threshold in self.classification.thresholds.items():
                if threshold < 0 or threshold > 1:
                    errors.append(f"{element_type}的分类阈值必须在0-1之间")
        
        # 验证空间配置
        if self.spatial.overlap_threshold < 0 or self.spatial.overlap_threshold > 1:
            errors.append("重叠阈值必须在0-1之间")
        
        if self.spatial.semantic_distance_threshold <= 0:
            errors.append("语义距离阈值必须大于0")
        
        # 验证性能配置
        if self.performance.max_cache_size <= 0:
            errors.append("最大缓存大小必须大于0")
        
        if self.performance.max_threads <= 0:
            errors.append("最大线程数必须大于0")
        
        # 验证ROI检测配置
        if self.performance.roi_change_threshold < 0.01 or self.performance.roi_change_threshold > 1.0:
            errors.append("ROI变化阈值必须在0.01-1.0之间")
        
        if self.performance.roi_min_size < 10:
            errors.append("ROI最小尺寸不能小于10像素")
        
        if self.performance.roi_max_count < 1 or self.performance.roi_max_count > 20:
            errors.append("ROI最大数量必须在1-20之间")
        
        if self.performance.roi_merge_distance < 5:
            errors.append("ROI合并距离不能小于5像素")
        
        if self.performance.roi_coverage_threshold < 0.1 or self.performance.roi_coverage_threshold > 1.0:
            errors.append("ROI覆盖阈值必须在0.1-1.0之间")
        
        return errors
    
    def IsValid(self) -> bool:
        """检查配置是否有效"""
        return len(self.ValidateConfig()) == 0
    #endregion
    
    #region 配置迁移
    @staticmethod
    def MigrateFromOldConfig(old_config: Dict[str, Any]) -> 'UnifiedRecognitionConfig':
        """
        从旧配置迁移到新配置
        
        Args:
            old_config: 旧配置字典
            
        Returns:
            新的统一配置对象
        """
        new_config = UnifiedRecognitionConfig()
        
        try:
            # 迁移检测参数
            if 'detection' in old_config:
                detection = old_config['detection']
                
                # 迁移区域面积参数
                if 'min_area' in detection:
                    new_config.segmentation.min_region_area = detection['min_area']
                if 'max_area' in detection:
                    new_config.segmentation.max_region_area = detection['max_area']
                
                # 迁移边缘检测参数
                if 'edge_low' in detection:
                    new_config.segmentation.edge_threshold_low = detection['edge_low']
                if 'edge_high' in detection:
                    new_config.segmentation.edge_threshold_high = detection['edge_high']
            
            # 迁移分类阈值
            if 'thresholds' in old_config:
                new_config.classification.thresholds = old_config['thresholds'].copy()
            
            # 迁移性能参数
            if 'performance' in old_config:
                perf = old_config['performance']
                if 'enable_cache' in perf:
                    new_config.performance.enable_caching = perf['enable_cache']
                if 'parallel' in perf:
                    new_config.performance.parallel_feature_extraction = perf['parallel']
            
            logging.getLogger(__name__).info("配置迁移完成")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"配置迁移失败: {e}")
        
        return new_config
    #endregion
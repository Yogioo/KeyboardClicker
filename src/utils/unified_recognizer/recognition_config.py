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
    #endregion
    
    #region 预设配置
    def LoadFastConfig(self):
        """加载快速识别配置"""
        self.pyramid.levels = 3
        self.pyramid.scale_factor = 0.6
        self.segmentation.min_region_area = 100
        self.segmentation.max_region_area = 50000
        self.performance.parallel_feature_extraction = True
        self.performance.max_threads = 4
        
        # 降低阈值以提高速度
        self.classification.thresholds = {
            'button': 0.35,
            'icon': 0.3,
            'text': 0.25,
            'link': 0.3,
            'input': 0.35
        }
        
        self._logger.info("已加载快速识别配置")
    
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
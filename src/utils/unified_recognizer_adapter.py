# -*- coding: utf-8 -*-
"""
统一识别器适配器

为了在main.py中无缝替换FastVisualRecognizer，提供完全兼容的接口。
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Optional, Callable, Union
from PIL import Image

from .unified_recognizer import UnifiedVisualRecognizer, UnifiedRecognitionConfig
from .detection_config import detection_config

class UnifiedRecognizerAdapter:
    """统一识别器适配器 - 兼容FastVisualRecognizer接口"""
    
    def __init__(self):
        """初始化适配器"""
        # 初始化统一识别器
        self._config = UnifiedRecognitionConfig()
        self._config.LoadFastConfig()  # 使用快速配置以提升性能
        
        self._recognizer = UnifiedVisualRecognizer(self._config)
        
        # 回调函数
        self._on_recognition_callback: Optional[Callable] = None
        self._on_error_callback: Optional[Callable] = None
        self._on_progress_callback: Optional[Callable] = None
        
        # 兼容性配置
        self._detection_config = detection_config
        
        print("统一识别器适配器已初始化 - 使用新的统一算法")
    
    #region 回调函数设置（兼容FastVisualRecognizer）
    def set_recognition_callback(self, callback: Callable[[str], None]):
        """设置识别回调"""
        self._on_recognition_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """设置错误回调"""
        self._on_error_callback = callback
        
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """设置进度回调"""
        self._on_progress_callback = callback
    #endregion
    
    #region 图像处理工具方法
    def _get_image_from_source(self, image_source: Union[str, Image.Image, np.ndarray, None]) -> Optional[np.ndarray]:
        """从不同源获取图像并转换为numpy数组格式"""
        try:
            if image_source is None:
                # 如果没有提供图像源，截取全屏
                from .screenshot import ScreenshotTool
                screenshot_tool = ScreenshotTool()
                image_pil = screenshot_tool.capture_full_screen()
                if image_pil is None:
                    return None
                return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            
            elif isinstance(image_source, str):
                # 文件路径
                image = cv2.imread(image_source)
                return image
            
            elif isinstance(image_source, Image.Image):
                # PIL图像
                return cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
            
            elif isinstance(image_source, np.ndarray):
                # numpy数组
                return image_source.copy()
            
            else:
                raise ValueError(f"不支持的图像源类型: {type(image_source)}")
                
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"获取图像失败: {e}")
            return None
    
    def _convert_unified_results_to_legacy_format(self, unified_results: List[Dict]) -> List[Dict]:
        """将统一识别器的结果转换为兼容FastVisualRecognizer的格式"""
        legacy_results = []
        
        for result in unified_results:
            try:
                bbox = result['bbox']  # (x, y, w, h)
                x, y, w, h = bbox
                
                # 计算中心点
                center_x = x + w // 2
                center_y = y + h // 2
                
                # 转换为旧格式
                legacy_result = {
                    'type': result['type'],
                    'center_x': center_x,
                    'center_y': center_y,
                    'width': w,
                    'height': h,
                    'confidence': result['confidence'],
                    'bbox': bbox  # 保持原格式 (x, y, w, h)
                }
                
                legacy_results.append(legacy_result)
                
            except Exception as e:
                print(f"转换结果格式时出错: {e}, 结果: {result}")
                continue
        
        return legacy_results
    
    def _get_enabled_types_from_config(self) -> List[str]:
        """从配置中获取启用的检测类型"""
        enabled_types = []
        
        if self._detection_config.enable_button_detection:
            enabled_types.append('button')
        if self._detection_config.enable_link_detection:
            enabled_types.append('link')
        if self._detection_config.enable_input_detection:
            enabled_types.append('input')
        if self._detection_config.enable_icon_detection:
            enabled_types.append('icon')
        if self._detection_config.enable_text_detection:
            enabled_types.append('text')
        
        return enabled_types
    #endregion
    
    #region 主要检测接口（兼容FastVisualRecognizer）
    def detect_clickable_elements(self, image_source: Union[str, Image.Image, np.ndarray, None] = None,
                                include_types: Optional[List[str]] = None) -> List[Dict]:
        """检测所有可点击元素（主要接口）- 兼容FastVisualRecognizer
        
        Args:
            image_source: 图像源
            include_types: 包含的元素类型列表，如果为None则根据配置自动确定
            
        Returns:
            检测结果列表，每个结果包含: type, center_x, center_y, width, height, confidence, bbox
        """
        start_time = time.time()
        
        try:
            if self._on_progress_callback:
                self._on_progress_callback("开始检测可点击元素", 0.0)
            
            # 获取图像
            image = self._get_image_from_source(image_source)
            if image is None:
                if self._on_error_callback:
                    self._on_error_callback("无法获取有效图像")
                return []
            
            if self._on_progress_callback:
                self._on_progress_callback("图像获取完成，开始识别", 0.3)
            
            # 使用统一识别器进行检测
            unified_results = self._recognizer.DetectClickableElements(image)
            
            if self._on_progress_callback:
                self._on_progress_callback("识别完成，处理结果", 0.8)
            
            # 转换结果格式
            legacy_results = self._convert_unified_results_to_legacy_format(unified_results)
            
            # 根据配置过滤结果
            if include_types is None:
                include_types = self._get_enabled_types_from_config()
            
            if include_types:
                legacy_results = [r for r in legacy_results if r['type'] in include_types]
            
            # 不再需要调试模式处理，已简化
            
            if self._on_progress_callback:
                self._on_progress_callback("检测完成", 1.0)
            
            detection_time = time.time() - start_time
            
            if self._on_recognition_callback:
                message = f"统一识别器检测完成: {len(legacy_results)}个元素, 耗时{detection_time:.3f}秒"
                self._on_recognition_callback(message)
            
            return legacy_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"检测失败: {e}")
            return []
    
    def detect_single_type(self, element_type: str, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """单独检测指定类型的元素（调试功能）- 兼容FastVisualRecognizer
        
        Args:
            element_type: 要检测的元素类型 ('button', 'link', 'input', 'icon', 'text')
            image_source: 图像源
            
        Returns:
            检测结果列表
        """
        try:
            if self._on_progress_callback:
                self._on_progress_callback(f"开始单独检测{element_type}", 0.0)
            
            # 获取图像
            image = self._get_image_from_source(image_source)
            if image is None:
                if self._on_error_callback:
                    self._on_error_callback("无法获取有效图像")
                return []
            
            if self._on_progress_callback:
                self._on_progress_callback("图像获取完成，开始识别", 0.3)
            
            # 使用统一识别器的单类型检测
            unified_results = self._recognizer.DetectSingleType(element_type, image)
            
            if self._on_progress_callback:
                self._on_progress_callback("识别完成，处理结果", 0.8)
            
            # 转换结果格式
            legacy_results = self._convert_unified_results_to_legacy_format(unified_results)
            
            if self._on_progress_callback:
                self._on_progress_callback("检测完成", 1.0)
            
            if self._on_recognition_callback:
                message = f"单类型检测({element_type})完成: {len(legacy_results)}个元素"
                self._on_recognition_callback(message)
            
            return legacy_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"单类型检测失败: {e}")
            return []
    #endregion
    
    #region 兼容性方法（保持向后兼容）
    def detect_buttons(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测按钮 - 兼容性方法"""
        return self.detect_single_type('button', image_source)
    
    def detect_links(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测链接 - 兼容性方法"""
        return self.detect_single_type('link', image_source)
    
    def detect_input_fields(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测输入框 - 兼容性方法"""
        return self.detect_single_type('input', image_source)
    
    def detect_icons(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测图标 - 兼容性方法"""
        return self.detect_single_type('icon', image_source)
    
    def detect_text_regions(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测文本区域 - 兼容性方法"""
        return self.detect_single_type('text', image_source)
    #endregion
    
    #region 配置和统计接口
    def configure_detection_params(self, element_type: str, **kwargs):
        """配置检测参数 - 兼容性方法"""
        # 新的统一识别器有自己的配置系统，这里可以做一些适配
        print(f"配置检测参数: {element_type}, 参数: {kwargs}")
        # 可以根据需要调整统一识别器的配置
        
    def configure_performance(self, **kwargs):
        """配置性能参数 - 兼容性方法"""
        # 兼容旧的性能配置接口
        print(f"配置性能参数: {kwargs}")
        
        # 可以根据参数调整配置
        if 'use_parallel' in kwargs:
            # 根据并行设置调整配置
            pass
        if 'max_workers' in kwargs:
            # 根据最大工作线程调整配置
            pass
        
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return self._recognizer.GetPerformanceStats()
    
    def get_config(self) -> UnifiedRecognitionConfig:
        """获取当前配置"""
        return self._recognizer.GetConfig()
    
    def update_recognition_mode(self, mode: str = "balanced"):
        """更新识别模式"""
        try:
            if mode == "fast":
                self._config.LoadFastConfig()
            elif mode == "accurate":
                self._config.LoadAccurateConfig()
            else:
                self._config.LoadBalancedConfig()
            
            self._recognizer.UpdateConfig(self._config)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"识别模式已更新为: {mode}")
                
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"更新识别模式失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        self._recognizer.ClearCache()
        
    def reset_performance_stats(self):
        """重置性能统计"""
        self._recognizer.ResetPerformanceStats()
    #endregion
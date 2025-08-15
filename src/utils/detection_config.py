#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测参数配置模块
统一管理所有UI元素的检测参数
"""

from typing import List

class DetectionConfig:
    """检测参数配置类"""
    
    def __init__(self):
        """初始化检测参数
        
        这个类包含了所有UI元素检测的配置参数。
        用户可以根据实际需求调整这些参数来优化检测效果。
        """
        
        # ==================== 按钮检测参数 ====================
        # 按钮通常是矩形或圆角矩形，具有明显的边界和点击区域
        self.button_min_area = 200  # 最小按钮面积(像素²)，过小的区域不被认为是按钮
                                    # 建议值：100-500，值越小检测越敏感但误报率高
        
        self.button_max_area = 20000  # 最大按钮面积(像素²)，过大的区域不被认为是按钮
                                      # 建议值：20000-100000，根据屏幕分辨率调整
        
        self.button_aspect_ratio_range = (0.3, 6.0)  # 按钮长宽比范围(宽/高)
                                                      # 0.3表示很高的按钮，6.0表示很宽的按钮
                                                      # 建议值：(0.2, 8.0)，可根据UI设计风格调整
        
        self.button_confidence_threshold = 0.30  # 按钮检测置信度阈值(0-1)
                                                  # 值越高检测越严格，误报率低但可能漏检
                                                  # 建议值：0.3-0.5 (降低阈值增加检测率)
        
        # ==================== 链接检测参数 ====================
        # 链接通常是文本形式，具有下划线或特殊颜色
        self.link_min_area = 100  # 最小链接面积(像素²)
                                  # 建议值：50-200，太小可能检测到单个字符
        
        self.link_max_area = 10000  # 最大链接面积(像素²)
                                    # 建议值：5000-20000，避免检测到大段文本
        
        self.link_aspect_ratio_range = (1.5, 15.0)  # 链接长宽比范围
                                                     # 链接通常是横向的文本，比较狭长
                                                     # 建议值：(1.0, 20.0)
        
        self.link_confidence_threshold = 0.30  # 链接检测置信度阈值
                                                # 链接检测相对困难，阈值可以稍低
                                                # 建议值：0.25-0.4
        
        # ==================== 输入框检测参数 ====================
        # 输入框通常有明显的边框，内部可能有占位符文本
        self.input_min_area = 400  # 最小输入框面积(像素²)
                                   # 输入框需要足够大以容纳文本输入
                                   # 建议值：200-800
        
        self.input_max_area = 100000  # 最大输入框面积(像素²)
                                      # 避免检测到大的文本区域
                                      # 建议值：50000-200000
        
        self.input_aspect_ratio_range = (2.0, 15.0)  # 输入框长宽比范围
                                                      # 输入框通常是横向的矩形
                                                      # 建议值：(1.5, 20.0)
        
        self.input_confidence_threshold = 0.35  # 输入框检测置信度阈值
                                                 # 建议值：0.3-0.5
        
        # ==================== 图标检测参数 ====================
        # 图标通常是正方形或接近正方形的小图像
        self.icon_min_area = 64   # 最小图标面积(像素²) - 8x8像素起
                                  # 建议值：64-300 (提高最小值避免噪点)
        
        self.icon_max_area = 8000  # 最大图标面积(像素²)
                                   # 建议值：5000-10000 (增加最大值)
        
        self.icon_aspect_ratio_range = (0.6, 2.0)  # 图标长宽比范围
                                                    # 图标通常接近正方形
                                                    # 建议值：(0.5, 2.5)
        
        self.icon_confidence_threshold = 0.35  # 图标检测置信度阈值
                                                # 图标特征相对明显，可以设置较高阈值
                                                # 建议值：0.35-0.5 (适当降低提高检测率)
        
        # ==================== 文字区域检测参数 ====================
        # 文字区域包括标签、段落文本等
        self.text_min_area = 50   # 最小文字区域面积(像素²)
                                  # 单个字符或很短的文本，提高阈值避免噪点
                                  # 建议值：50-100 (提高最小值)
        
        self.text_max_area = 2000  # 最大文字区域面积(像素²)
                                    # 避免检测到整个页面的文本
                                    # 建议值：10000-50000
        
        self.text_aspect_ratio_range = (0.5, 30.0)  # 文字长宽比范围
                                                     # 文字可以是单行(很宽)或多行(较窄)
                                                     # 建议值：(0.5, 30.0)
        
        self.text_confidence_threshold = 0.2  # 文字检测置信度阈值
                                                # 文字检测相对容易，阈值可以较低
                                                # 建议值：0.2-0.35
        
        # ==================== 重复区域合并参数 ====================
        self.duplicate_iou_threshold = 0.3  # IoU(Intersection over Union)阈值
                                             # 用于合并重叠的检测区域
                                             # 值越高合并越严格，0.5表示重叠50%以上才合并
                                             # 建议值：0.3-0.7
        
        # ==================== 性能优化参数 ====================
        self.max_workers = 4  # 最大并行工作线程数
                              # 根据CPU核心数调整，通常设置为核心数的1-2倍
                              # 建议值：2-8
        
        self.roi_optimization = True  # ROI(Region of Interest)优化开关
                                      # 启用后只在感兴趣区域进行检测，提高性能
                                      # 建议：True(除非需要全屏检测)
        
        self.cache_enabled = True  # 检测结果缓存开关
                                   # 启用后相同区域的检测结果会被缓存，提高性能
                                   # 建议：True(除非内存受限)
        
        # ==================== 调试模式开关 ====================
        # 用于单独测试不同类型的UI元素检测
        self.debug_mode = True  # 调试模式总开关
        self.detect_buttons_only = False  # 仅检测按钮
        self.detect_links_only = False  # 仅检测链接
        self.detect_inputs_only = False  # 仅检测输入框
        self.detect_icons_only = False  # 仅检测图标
        self.detect_text_only = False  # 仅检测文字区域
        
        # 检测类型启用开关（正常模式下使用）
        self.enable_button_detection = True  # 启用按钮检测
        self.enable_link_detection = True  # 启用链接检测
        self.enable_input_detection = True  # 启用输入框检测
        self.enable_icon_detection = True  # 启用图标检测
        self.enable_text_detection = True  # 启用文字检测
    
    def get_element_params(self, element_type: str) -> dict:
        """获取指定元素类型的参数"""
        if element_type == 'button':
            return {
                'min_area': self.button_min_area,
                'max_area': self.button_max_area,
                'aspect_ratio_range': self.button_aspect_ratio_range,
                'confidence_threshold': self.button_confidence_threshold
            }
        elif element_type == 'link':
            return {
                'min_area': self.link_min_area,
                'max_area': self.link_max_area,
                'aspect_ratio_range': self.link_aspect_ratio_range,
                'confidence_threshold': self.link_confidence_threshold
            }
        elif element_type == 'input':
            return {
                'min_area': self.input_min_area,
                'max_area': self.input_max_area,
                'aspect_ratio_range': self.input_aspect_ratio_range,
                'confidence_threshold': self.input_confidence_threshold
            }
        elif element_type == 'icon':
            return {
                'min_area': self.icon_min_area,
                'max_area': self.icon_max_area,
                'aspect_ratio_range': self.icon_aspect_ratio_range,
                'confidence_threshold': self.icon_confidence_threshold
            }
        elif element_type == 'text':
            return {
                'min_area': self.text_min_area,
                'max_area': self.text_max_area,
                'aspect_ratio_range': self.text_aspect_ratio_range,
                'confidence_threshold': self.text_confidence_threshold
            }
        else:
            raise ValueError(f"未知的元素类型: {element_type}")
    
    def set_debug_mode(self, element_type: str = None):
        """设置调试模式，只检测指定类型的元素
        
        Args:
            element_type: 要单独检测的元素类型，None表示关闭调试模式
        """
        # 重置所有调试开关
        self.debug_mode = False
        self.detect_buttons_only = False
        self.detect_links_only = False
        self.detect_inputs_only = False
        self.detect_icons_only = False
        self.detect_text_only = False
        
        if element_type:
            self.debug_mode = True
            if element_type == 'button':
                self.detect_buttons_only = True
            elif element_type == 'link':
                self.detect_links_only = True
            elif element_type == 'input':
                self.detect_inputs_only = True
            elif element_type == 'icon':
                self.detect_icons_only = True
            elif element_type == 'text':
                self.detect_text_only = True
            else:
                raise ValueError(f"未知的调试元素类型: {element_type}")
    
    def get_enabled_detection_types(self) -> List[str]:
        """获取当前启用的检测类型列表"""
        enabled_types = []
        
        if self.debug_mode:
            # 调试模式下只返回单一类型
            if self.detect_buttons_only:
                enabled_types.append('button')
            elif self.detect_links_only:
                enabled_types.append('link')
            elif self.detect_inputs_only:
                enabled_types.append('input')
            elif self.detect_icons_only:
                enabled_types.append('icon')
            elif self.detect_text_only:
                enabled_types.append('text')
        else:
            # 正常模式下返回所有启用的类型
            if self.enable_button_detection:
                enabled_types.append('button')
            if self.enable_link_detection:
                enabled_types.append('link')
            if self.enable_input_detection:
                enabled_types.append('input')
            if self.enable_icon_detection:
                enabled_types.append('icon')
            if self.enable_text_detection:
                enabled_types.append('text')
        
        return enabled_types
    
    def toggle_detection_type(self, element_type: str, enabled: bool):
        """切换检测类型的启用状态"""
        if element_type == 'button':
            self.enable_button_detection = enabled
        elif element_type == 'link':
            self.enable_link_detection = enabled
        elif element_type == 'input':
            self.enable_input_detection = enabled
        elif element_type == 'icon':
            self.enable_icon_detection = enabled
        elif element_type == 'text':
            self.enable_text_detection = enabled
        else:
            raise ValueError(f"未知的元素类型: {element_type}")
    
    def update_element_params(self, element_type: str, **kwargs):
        """更新指定元素类型的参数"""
        if element_type == 'button':
            if 'min_area' in kwargs:
                self.button_min_area = kwargs['min_area']
            if 'max_area' in kwargs:
                self.button_max_area = kwargs['max_area']
            if 'aspect_ratio_range' in kwargs:
                self.button_aspect_ratio_range = kwargs['aspect_ratio_range']
            if 'confidence_threshold' in kwargs:
                self.button_confidence_threshold = kwargs['confidence_threshold']
        elif element_type == 'link':
            if 'min_area' in kwargs:
                self.link_min_area = kwargs['min_area']
            if 'max_area' in kwargs:
                self.link_max_area = kwargs['max_area']
            if 'aspect_ratio_range' in kwargs:
                self.link_aspect_ratio_range = kwargs['aspect_ratio_range']
            if 'confidence_threshold' in kwargs:
                self.link_confidence_threshold = kwargs['confidence_threshold']
        elif element_type == 'input':
            if 'min_area' in kwargs:
                self.input_min_area = kwargs['min_area']
            if 'max_area' in kwargs:
                self.input_max_area = kwargs['max_area']
            if 'aspect_ratio_range' in kwargs:
                self.input_aspect_ratio_range = kwargs['aspect_ratio_range']
            if 'confidence_threshold' in kwargs:
                self.input_confidence_threshold = kwargs['confidence_threshold']
        elif element_type == 'icon':
            if 'min_area' in kwargs:
                self.icon_min_area = kwargs['min_area']
            if 'max_area' in kwargs:
                self.icon_max_area = kwargs['max_area']
            if 'aspect_ratio_range' in kwargs:
                self.icon_aspect_ratio_range = kwargs['aspect_ratio_range']
            if 'confidence_threshold' in kwargs:
                self.icon_confidence_threshold = kwargs['confidence_threshold']
        elif element_type == 'text':
            if 'min_area' in kwargs:
                self.text_min_area = kwargs['min_area']
            if 'max_area' in kwargs:
                self.text_max_area = kwargs['max_area']
            if 'aspect_ratio_range' in kwargs:
                self.text_aspect_ratio_range = kwargs['aspect_ratio_range']
            if 'confidence_threshold' in kwargs:
                self.text_confidence_threshold = kwargs['confidence_threshold']
        else:
            raise ValueError(f"未知的元素类型: {element_type}")
    
    def print_config(self):
        """打印当前配置"""
        print("[配置] 当前检测参数配置：")
        print(f"  - 按钮: 面积{self.button_min_area}-{self.button_max_area}, 长宽比{self.button_aspect_ratio_range}, 置信度{self.button_confidence_threshold}")
        print(f"  - 图标: 面积{self.icon_min_area}-{self.icon_max_area}, 长宽比{self.icon_aspect_ratio_range}, 置信度{self.icon_confidence_threshold}")
        print(f"  - 文字: 面积{self.text_min_area}-{self.text_max_area}, 长宽比{self.text_aspect_ratio_range}, 置信度{self.text_confidence_threshold}")
        print(f"  - 链接: 面积{self.link_min_area}-{self.link_max_area}, 长宽比{self.link_aspect_ratio_range}, 置信度{self.link_confidence_threshold}")
        print(f"  - 输入框: 面积{self.input_min_area}-{self.input_max_area}, 长宽比{self.input_aspect_ratio_range}, 置信度{self.input_confidence_threshold}")
        print(f"  - 重复区域IoU阈值: {self.duplicate_iou_threshold}")

# 全局配置实例
detection_config = DetectionConfig()
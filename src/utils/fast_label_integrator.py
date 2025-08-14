#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速标签集成器
集成快速视觉识别与标签显示功能，替代OCR方案
性能目标：0-1秒内完成识别并显示标签
"""

import sys
import os
import time
import tkinter as tk
from typing import List, Dict, Optional, Callable
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.fast_visual_recognizer import FastVisualRecognizer
from src.utils.screenshot import ScreenshotTool
from src.utils.screen_labeler import ScreenLabeler
from src.utils.bounding_box_overlay import BoundingBoxOverlay
from src.utils.detection_config import detection_config

class FastLabelIntegrator:
    """快速标签集成器"""
    
    def __init__(self):
        """初始化快速标签集成器"""
        # 初始化各个组件
        self._recognizer = FastVisualRecognizer()
        self._screenshot_tool = ScreenshotTool()
        self._labeler = ScreenLabeler()
        self._bbox_overlay = BoundingBoxOverlay()
        
        # 当前识别结果和标签映射
        self._current_detections = []
        self._label_mapping = {}
        
        # 设置回调
        self._setup_callbacks()
        
        # 配置优化的识别参数
        self._optimize_recognition_settings()
    
    def _setup_callbacks(self):
        """设置组件回调"""
        self._screenshot_tool.set_screenshot_callback(self._on_screenshot)
        self._screenshot_tool.set_error_callback(self._on_error)
        
        self._recognizer.set_recognition_callback(self._on_recognition)
        self._recognizer.set_error_callback(self._on_error)
        self._recognizer.set_progress_callback(self._on_progress)
        
        self._labeler.SetCallback(self._on_label_success)
        self._labeler.SetErrorCallback(self._on_error)
    
    def _on_screenshot(self, msg):
        """截图回调"""
        print(f"[截图] {msg}")
    
    def _on_recognition(self, msg):
        """识别回调"""
        print(f"[识别] {msg}")
    
    def _on_label_success(self, msg):
        """标签成功回调"""
        print(f"[标签] {msg}")
    
    def _on_error(self, msg):
        """错误回调"""
        print(f"[错误] {msg}")
    
    def _on_progress(self, message, progress):
        """进度回调"""
        print(f"[进度] {message} ({progress*100:.1f}%)")
    
    def _optimize_recognition_settings(self):
        """优化识别设置以获取最佳性能"""
        try:
            # 启用所有性能优化
            self._recognizer.configure_performance(
                use_parallel=True,
                max_workers=4,
                roi_optimization=True,
                cache_enabled=True
            )
            
            # 使用统一配置文件的参数
            for element_type in ['button', 'icon', 'text', 'link', 'input']:
                params = detection_config.get_element_params(element_type)
                self._recognizer.configure_detection_params(
                    element_type, 
                    min_area=params['min_area'], 
                    max_area=params['max_area'], 
                    aspect_ratio_range=params['aspect_ratio_range']
                )
            
            # 打印当前配置
            detection_config.print_config()
            
        except Exception as e:
            self._on_error(f"识别参数优化失败: {e}")
    
    #region 主要功能接口
    def capture_and_recognize(self, save_screenshot: bool = True, region: Optional[tuple] = None,
                            include_types: Optional[List[str]] = None) -> bool:
        """截图并快速识别可点击元素"""
        try:
            start_time = time.time()
            
            # 1. 截图
            if region is None:
                # 全屏截图
                if save_screenshot:
                    screenshot_path = self._screenshot_tool.capture_and_save_full_screen("fast_recognition.png")
                    print(f"[截图] 全屏截图已保存: {screenshot_path}")
                else:
                    screenshot = self._screenshot_tool.capture_full_screen()
                    screenshot_path = None
            else:
                # 区域截图
                x, y, width, height = region
                if save_screenshot:
                    screenshot_path = self._screenshot_tool.capture_and_save_region(
                        x, y, width, height, "fast_region.png"
                    )
                    print(f"[截图] 区域截图已保存: {screenshot_path}")
                else:
                    screenshot = self._screenshot_tool.capture_region(x, y, width, height)
                    screenshot_path = None
            
            # 2. 快速识别可点击元素
            if save_screenshot and screenshot_path:
                elements = self._recognizer.detect_clickable_elements(screenshot_path, include_types)
            else:
                elements = self._recognizer.detect_clickable_elements(screenshot, include_types)
            
            # 3. 调整坐标（如果是区域截图）
            if region is not None:
                offset_x, offset_y = region[0], region[1]
                for element in elements:
                    element['center_x'] += offset_x
                    element['center_y'] += offset_y
                    # 更新bbox
                    x, y, w, h = element['bbox']
                    element['bbox'] = (x + offset_x, y + offset_y, w, h)
            
            self._current_detections = elements
            elapsed_time = time.time() - start_time
            
            print(f"[识别] 优化后的快速识别完成：发现 {len(elements)} 个可点击元素，耗时 {elapsed_time:.2f} 秒")
            
            return len(elements) > 0
            
        except Exception as e:
            self._on_error(f"快速识别失败: {e}")
            return False
    
    def show_bounding_boxes(self, duration: Optional[float] = 3.0, 
                          box_color: str = 'red', box_width: int = 2) -> bool:
        """显示识别结果的边界框"""
        try:
            if not self._current_detections:
                self._on_error("没有识别结果，请先执行快速识别")
                return False
            
            print(f"[边界框] 显示 {len(self._current_detections)} 个元素的边界框（优化后）")
            
            # 转换为边界框格式
            detections_for_bbox = []
            for detection in self._current_detections:
                detections_for_bbox.append({
                    'bbox': detection['bbox'],
                    'text': f"{detection['type']} ({detection['confidence']:.2f})"
                })
            
            # 显示边界框
            self._bbox_overlay.ShowBoundingBoxes(
                detections_for_bbox, 
                duration=duration,
                box_color=box_color,
                box_width=box_width
            )
            
            return True
            
        except Exception as e:
            self._on_error(f"显示边界框失败: {e}")
            return False
    
    def show_labels(self, max_labels: Optional[int] = None, 
                   duration: Optional[float] = None) -> bool:
        """为识别到的元素显示标签"""
        try:
            if not self._current_detections:
                self._on_error("没有识别结果，请先执行快速识别")
                return False
            
            # 按置信度排序
            detections_sorted = sorted(
                self._current_detections,
                key=lambda x: x['confidence'],
                reverse=True
            )
            
            if max_labels is not None:
                detections_to_label = detections_sorted[:max_labels]
            else:
                detections_to_label = detections_sorted
            
            # 使用ScreenLabeler的标签生成算法
            labels = self._labeler._GenerateLabelList(len(detections_to_label))
            
            # 为每个元素创建标签
            label_elements = []
            self._label_mapping.clear()
            
            for i, (detection, label) in enumerate(zip(detections_to_label, labels)):
                element = {
                    'center_x': detection['center_x'],
                    'center_y': detection['center_y'],
                    'text': label,
                    'type': detection['type']  # 保留原始类型信息
                }
                label_elements.append(element)
                
                # 保存标签映射
                self._label_mapping[label] = {
                    'detection': detection,
                    'element': element
                }
            
            # 显示标签
            success = self._labeler.ShowLabels(label_elements, duration)
            
            if success:
                print(f"[标签] 为 {len(label_elements)} 个高质量元素显示了标签")
                return True
            else:
                self._on_error("标签显示失败")
                return False
                
        except Exception as e:
            self._on_error(f"标签显示失败: {e}")
            return False
    
    def analyze_and_label(self, region: Optional[tuple] = None, 
                         duration: Optional[float] = None,
                         max_labels: Optional[int] = None,
                         show_boxes: bool = True,
                         include_types: Optional[List[str]] = None) -> bool:
        """一键分析：截图 => 快速识别 => 显示标签"""
        try:
            print(f"\n🚀 === 开始优化后的快速视觉识别流程 ===")
            print("✨ 使用优化的计算机视觉算法，无需OCR，高精度识别可点击元素")
            
            # 1. 截图并识别
            if not self.capture_and_recognize(region=region, include_types=include_types):
                return False
            
            # 2. 显示边界框（如果启用）
            if show_boxes:
                print("[流程] 首先显示元素边界框...")
                if self.show_bounding_boxes(duration=2.0):
                    print("[流程] 边界框显示2秒，然后显示标签...")
                    time.sleep(2)
                    self.hide_bounding_boxes()
            
            # 3. 显示标签
            if not self.show_labels(max_labels=max_labels, duration=duration):
                return False
            
            # 4. 输出结果摘要
            print(f"\n✅ === 优化后的快速识别完成 ===")
            print(f"识别结果: {len(self._current_detections)} 个可点击元素")
            
            # 统计各类型元素数量
            type_counts = {}
            for detection in self._current_detections:
                elem_type = detection['type']
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
            
            print("元素分布:", end=" ")
            for elem_type, count in type_counts.items():
                print(f"{elem_type}:{count}", end=" ")
            print()
            
            if max_labels is not None:
                displayed_count = min(len(self._current_detections), max_labels)
                print(f"显示标签: {displayed_count} 个（限制: {max_labels}）")
            else:
                print(f"显示标签: {len(self._label_mapping)} 个（无限制）")
            
            # 显示部分标签映射示例
            if self._label_mapping:
                print("\n标签映射示例:")
                for label, info in list(self._label_mapping.items())[:5]:  # 只显示前5个
                    detection = info['detection']
                    print(f"  {label}: {detection['type']} 置信度:{detection['confidence']:.2f} 位置:({detection['center_x']}, {detection['center_y']})")
                if len(self._label_mapping) > 5:
                    print(f"  ... 还有 {len(self._label_mapping) - 5} 个标签")
            
            return True
            
        except Exception as e:
            self._on_error(f"快速识别流程失败: {e}")
            return False
    #endregion
    
    #region 辅助功能
    def hide_bounding_boxes(self):
        """隐藏边界框"""
        try:
            self._bbox_overlay.HideBoundingBoxes()
            print("[边界框] 已隐藏")
        except Exception as e:
            self._on_error(f"隐藏边界框失败: {e}")
    
    def hide_labels(self):
        """隐藏所有标签"""
        try:
            self._labeler.HideLabels()
            self._label_mapping.clear()
            print("[标签] 已隐藏")
        except Exception as e:
            self._on_error(f"隐藏标签失败: {e}")
    
    def hide_all(self):
        """隐藏所有标签和边界框"""
        try:
            self.hide_labels()
            self.hide_bounding_boxes()
            print("[清理] 所有显示元素已隐藏")
        except Exception as e:
            self._on_error(f"清理失败: {e}")
    
    def get_detection_by_label(self, label: str) -> Optional[Dict]:
        """根据标签获取对应的识别结果"""
        return self._label_mapping.get(label, {}).get('detection')
    
    def get_current_detections(self) -> List[Dict]:
        """获取当前识别结果"""
        return self._current_detections.copy()
    
    def get_label_mappings(self) -> Dict:
        """获取标签映射"""
        return self._label_mapping.copy()
    
    def get_statistics(self) -> Dict:
        """获取识别统计信息"""
        try:
            if not self._current_detections:
                return {'total_elements': 0, 'message': '没有识别结果'}
            
            # 基本统计
            total = len(self._current_detections)
            
            # 按类型统计
            type_counts = {}
            confidences_by_type = {}
            
            for detection in self._current_detections:
                elem_type = detection['type']
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
                
                if elem_type not in confidences_by_type:
                    confidences_by_type[elem_type] = []
                confidences_by_type[elem_type].append(detection['confidence'])
            
            # 计算平均置信度
            avg_confidences = {}
            for elem_type, confidences in confidences_by_type.items():
                avg_confidences[elem_type] = sum(confidences) / len(confidences)
            
            # 整体平均置信度
            all_confidences = [d['confidence'] for d in self._current_detections]
            overall_avg_confidence = sum(all_confidences) / len(all_confidences)
            
            stats = {
                'total_elements': total,
                'type_counts': type_counts,
                'average_confidences': avg_confidences,
                'overall_average_confidence': overall_avg_confidence,
                'labels_displayed': len(self._label_mapping),
                'recognition_method': 'FastVisualRecognizer_Optimized'
            }
            
            return stats
            
        except Exception as e:
            self._on_error(f"获取统计信息失败: {e}")
            return {'error': str(e)}
    
    def clear_cache(self):
        """清空识别缓存"""
        try:
            self._recognizer.clear_cache()
            print("[缓存] 识别缓存已清空")
        except Exception as e:
            self._on_error(f"清空缓存失败: {e}")
    
    def configure_recognition(self, **kwargs):
        """配置识别参数"""
        try:
            # 性能配置
            if 'performance' in kwargs:
                perf = kwargs['performance']
                self._recognizer.configure_performance(**perf)
            
            # 检测参数配置
            for element_type in ['button', 'link', 'input', 'icon', 'text']:
                if element_type in kwargs:
                    params = kwargs[element_type]
                    self._recognizer.configure_detection_params(element_type, **params)
            
            print("[配置] 识别参数已更新")
            
        except Exception as e:
            self._on_error(f"配置识别参数失败: {e}")
    #endregion
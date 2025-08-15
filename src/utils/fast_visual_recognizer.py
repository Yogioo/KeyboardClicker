#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速视觉识别模块
专门用于快速识别可点击的UI元素，不依赖OCR
性能目标：0-1秒内完成全屏识别
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Callable, Union, Tuple
from PIL import Image
import pyautogui
import time
from concurrent.futures import ThreadPoolExecutor
import threading
from .detection_config import detection_config

class FastVisualRecognizer:
    """快速视觉识别器"""
    
    def __init__(self):
        """初始化快速视觉识别器"""
        self._on_recognition_callback: Optional[Callable] = None
        self._on_error_callback: Optional[Callable] = None
        self._on_progress_callback: Optional[Callable] = None
        
        # #region 识别参数配置 - 使用统一配置
        # 所有参数现在从detection_config获取
        self._config = detection_config
        
        # 性能优化参数
        self._use_parallel = self._config.max_workers > 1  # 是否使用并行处理
        self._max_workers = self._config.max_workers  # 最大工作线程数
        self._roi_optimization = self._config.roi_optimization  # ROI优化
        self._cache_enabled = self._config.cache_enabled  # 缓存启用
        
        # 缓存
        self._result_cache = {}
        self._cache_timeout = 60  # 缓存超时时间
        
        # 调试模式已移除
        self._debug_mode = False
        # #endregion
        
        # 初始化检查
        self._check_dependencies()
    
    #region 依赖检查和配置
    def _check_dependencies(self):
        """检查依赖组件"""
        try:
            # 检查OpenCV
            cv2.__version__
            if self._on_recognition_callback:
                self._on_recognition_callback("FastVisualRecognizer 初始化完成")
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"OpenCV 未正确安装: {e}")
    
    def set_recognition_callback(self, callback: Callable[[str], None]):
        """设置识别操作回调函数"""
        self._on_recognition_callback = callback
        
    def set_error_callback(self, callback: Callable[[str], None]):
        """设置错误回调函数"""
        self._on_error_callback = callback
        
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """设置进度回调函数"""
        self._on_progress_callback = callback
    
    def configure_detection_params(self, element_type: str, **kwargs):
        """配置检测参数
        
        Args:
            element_type: 元素类型 ('button', 'link', 'input', 'icon', 'text')
            **kwargs: 参数字典，可包含 min_area, max_area, aspect_ratio_range
        """
        # 直接更新统一配置文件中的参数
        self._config.update_element_params(element_type, **kwargs)
    
    def _get_element_params(self, element_type: str) -> dict:
        """获取元素参数的辅助方法"""
        return self._config.get_element_params(element_type)
    
    def configure_performance(self, use_parallel: bool = True, max_workers: int = 4, 
                            roi_optimization: bool = True, cache_enabled: bool = True):
        """配置性能参数"""
        self._use_parallel = use_parallel
        self._max_workers = max_workers
        self._roi_optimization = roi_optimization
        self._cache_enabled = cache_enabled
    #endregion
    
    #region 图像预处理
    def _get_image_from_source(self, image_source: Union[str, Image.Image, np.ndarray, None]) -> np.ndarray:
        """从不同来源获取图像"""
        try:
            if image_source is None:
                # 截取当前屏幕
                screenshot = pyautogui.screenshot()
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            elif isinstance(image_source, str):
                # 文件路径
                image = cv2.imread(image_source)
                if image is None:
                    raise FileNotFoundError(f"无法加载图像: {image_source}")
            elif isinstance(image_source, Image.Image):
                # PIL Image
                image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
            elif isinstance(image_source, np.ndarray):
                # numpy数组
                image = image_source
            else:
                raise ValueError("不支持的图像源类型")
                
            return image
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"获取图像失败: {e}")
            raise
    
    def _preprocess_for_edge_detection(self, image: np.ndarray) -> np.ndarray:
        """为边缘检测预处理图像"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Canny边缘检测（使用更敏感的参数以检测细小边缘）
        edges = cv2.Canny(blurred, 10, 50)
        
        return edges
    
    def _detect_color_based_edges(self, image: np.ndarray) -> np.ndarray:
        """基于颜色的边缘检测，专门检测按钮颜色"""
        try:
            # 转换到HSV颜色空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 定义按钮常见颜色范围（优化后）
            color_ranges = [
                # 绿色按钮（扩大范围以更好检测）
                ([35, 50, 50], [85, 255, 255]),  # 提高阈值，扩大范围
                # 蓝色按钮（优化范围）
                ([95, 50, 50], [135, 255, 255]),
                # 红色按钮（优化范围）
                ([0, 50, 50], [10, 255, 255]),
                ([170, 50, 50], [180, 255, 255]),
                # 橙色/黄色按钮
                ([10, 50, 50], [35, 255, 255]),
                # 紫色按钮
                ([130, 50, 50], [170, 255, 255]),
                # 添加灰色系按钮检测（低饱和度）
                ([0, 0, 100], [180, 50, 200])  # 灰色/白色按钮
            ]
            
            color_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            
            for lower, upper in color_ranges:
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(hsv, lower, upper)
                color_mask = cv2.bitwise_or(color_mask, mask)
            
            # 形态学操作清理噪声
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
            
            # 获取颜色区域的边缘
            color_edges = cv2.Canny(color_mask, 50, 150)
            
            return color_edges
            
        except Exception:
            # 如果颜色检测失败，返回空边缘
            return np.zeros(image.shape[:2], dtype=np.uint8)
    
    def _preprocess_for_color_analysis(self, image: np.ndarray) -> Dict:
        """为颜色分析预处理图像"""
        # 转换到不同颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        return {
            'bgr': image,
            'hsv': hsv,
            'lab': lab
        }
    
    def _extract_roi_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """提取感兴趣区域，优化性能"""
        if not self._roi_optimization:
            # 如果未启用ROI优化，返回整个图像
            height, width = image.shape[:2]
            return [(0, 0, width, height)]
        
        # 简单的ROI提取：基于梯度密度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算梯度
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient = np.sqrt(grad_x**2 + grad_y**2)
        
        # 将图像分块，计算每块的梯度密度
        height, width = image.shape[:2]
        block_size = 100
        roi_regions = []
        
        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                x2 = min(x + block_size, width)
                y2 = min(y + block_size, height)
                
                # 计算该块的梯度密度
                block_gradient = gradient[y:y2, x:x2]
                gradient_density = np.mean(block_gradient)
                
                # 如果梯度密度足够高，认为是感兴趣区域
                if gradient_density > 10:  # 阈值可调
                    roi_regions.append((x, y, x2 - x, y2 - y))
        
        return roi_regions if roi_regions else [(0, 0, width, height)]
    #endregion
    
    #region 缓存管理
    def _get_cache_key(self, image: np.ndarray, method: str) -> str:
        """生成缓存键"""
        # 简单的图像哈希
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        resized = cv2.resize(gray, (64, 64))
        image_hash = hash(resized.tobytes())
        return f"{method}_{image_hash}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """从缓存获取结果"""
        if not self._cache_enabled:
            return None
            
        if cache_key in self._result_cache:
            result, timestamp = self._result_cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                return result
            else:
                # 缓存过期，删除
                del self._result_cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, result: List[Dict]):
        """保存结果到缓存"""
        if self._cache_enabled:
            self._result_cache[cache_key] = (result, time.time())
    
    def clear_cache(self):
        """清空缓存"""
        self._result_cache.clear()
    #endregion
    
    #region 主要识别接口
    def detect_clickable_elements(self, image_source: Union[str, Image.Image, np.ndarray, None] = None,
                                include_types: Optional[List[str]] = None) -> List[Dict]:
        """检测所有可点击元素（主要接口）
        
        Args:
            image_source: 图像源
            include_types: 包含的元素类型列表，如果为None则根据配置自动确定
                          可选: ['button', 'link', 'input', 'icon', 'text']
        
        Returns:
            检测结果列表，每个结果包含: type, center_x, center_y, width, height, confidence, bbox
        """
        start_time = time.time()
        
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            
            # 根据配置确定要检测的类型
            if include_types is None:
                include_types = self._config.get_enabled_detection_types()
            
            if self._on_progress_callback:
                self._on_progress_callback("开始检测可点击元素", 0.0)
            
            all_elements = []
            total_tasks = len(include_types)
            
            # 简化并行处理（减少线程开销）
            if self._use_parallel and total_tasks > 2:  # 只有超过2个任务才使用并行
                with ThreadPoolExecutor(max_workers=min(self._max_workers, total_tasks)) as executor:
                    future_to_type = {}
                    
                    if 'button' in include_types:
                        future_to_type[executor.submit(self.detect_buttons, image)] = 'button'
                    if 'link' in include_types:
                        future_to_type[executor.submit(self.detect_links, image)] = 'link'
                    if 'input' in include_types:
                        future_to_type[executor.submit(self.detect_input_fields, image)] = 'input'
                    if 'icon' in include_types:
                        future_to_type[executor.submit(self.detect_icons, image)] = 'icon'
                    if 'text' in include_types:
                        future_to_type[executor.submit(self.detect_text_regions, image)] = 'text'
                    
                    completed = 0
                    for future in future_to_type:
                        try:
                            elements = future.result()
                            all_elements.extend(elements)
                            completed += 1
                            if self._on_progress_callback:
                                progress = completed / total_tasks * 0.8  # 80%用于检测
                                self._on_progress_callback(f"完成 {future_to_type[future]} 检测", progress)
                        except Exception as e:
                            if self._on_error_callback:
                                self._on_error_callback(f"{future_to_type[future]} 检测失败: {e}")
            else:
                # 串行处理
                if 'button' in include_types:
                    all_elements.extend(self.detect_buttons(image))
                    if self._on_progress_callback:
                        self._on_progress_callback("完成按钮检测", 0.2)
                        
                if 'link' in include_types:
                    all_elements.extend(self.detect_links(image))
                    if self._on_progress_callback:
                        self._on_progress_callback("完成链接检测", 0.4)
                        
                if 'input' in include_types:
                    all_elements.extend(self.detect_input_fields(image))
                    if self._on_progress_callback:
                        self._on_progress_callback("完成输入框检测", 0.6)
                        
                if 'icon' in include_types:
                    all_elements.extend(self.detect_icons(image))
                    if self._on_progress_callback:
                        self._on_progress_callback("完成图标检测", 0.7)
                        
                if 'text' in include_types:
                    all_elements.extend(self.detect_text_regions(image))
                    if self._on_progress_callback:
                        self._on_progress_callback("完成文字区域检测", 0.8)
            
            # 过滤低置信度的元素
            if self._on_progress_callback:
                self._on_progress_callback("过滤低质量检测", 0.85)
            filtered_elements = self._filter_low_confidence_elements(all_elements)
            
            # 合并重叠元素
            if self._on_progress_callback:
                self._on_progress_callback("合并重叠元素", 0.9)
            unique_elements = self._merge_overlapping_elements(filtered_elements)
            
            # 按置信度排序
            unique_elements.sort(key=lambda x: x['confidence'], reverse=True)
            
            elapsed_time = time.time() - start_time
            
            if self._on_recognition_callback:
                self._on_recognition_callback(
                    f"快速识别完成：检测到 {len(unique_elements)} 个可点击元素，耗时 {elapsed_time:.2f} 秒"
                )
            
            if self._on_progress_callback:
                self._on_progress_callback("识别完成", 1.0)
            
            return unique_elements
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"可点击元素检测失败: {e}")
            raise
    
    def detect_single_type(self, element_type: str, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """单独检测指定类型的元素（调试功能）
        
        Args:
            element_type: 要检测的元素类型 ('button', 'link', 'input', 'icon', 'text')
            image_source: 图像源
        
        Returns:
            检测结果列表
        """
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            
            if self._on_progress_callback:
                self._on_progress_callback(f"开始单独检测{element_type}", 0.0)
            
            # 根据类型调用相应的检测方法
            if element_type == 'button':
                elements = self.detect_buttons(image)
            elif element_type == 'link':
                elements = self.detect_links(image)
            elif element_type == 'input':
                elements = self.detect_input_fields(image)
            elif element_type == 'icon':
                elements = self.detect_icons(image)
            elif element_type == 'text':
                elements = self.detect_text_regions(image)
            else:
                raise ValueError(f"不支持的元素类型: {element_type}")
            
            if self._on_progress_callback:
                self._on_progress_callback(f"完成{element_type}检测", 0.8)
            
            # 过滤低置信度的元素
            filtered_elements = self._filter_low_confidence_elements(elements)
            
            # 按置信度排序
            filtered_elements.sort(key=lambda x: x['confidence'], reverse=True)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(
                    f"单独{element_type}检测完成：检测到 {len(filtered_elements)} 个元素"
                )
            
            if self._on_progress_callback:
                self._on_progress_callback("检测完成", 1.0)
            
            return filtered_elements
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"{element_type}检测失败: {e}")
            raise
    
    def detect_buttons(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测按钮元素"""
        try:
            # 获取图像
            if isinstance(image_source, np.ndarray):
                image = image_source
            else:
                image = self._get_image_from_source(image_source)
            
            # 检查缓存
            cache_key = self._get_cache_key(image, 'buttons')
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            button_results = []
            
            # 优化：直接处理整个图像，避免ROI的计算开销
            height, width = image.shape[:2]
            roi_regions = [(0, 0, width, height)]  # 使用整个图像
            
            for roi_x, roi_y, roi_w, roi_h in roi_regions:
                # 提取ROI
                roi_image = image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
                
                # 简化边缘检测（仅使用颜色边缘检测，速度更快）
                edges = self._detect_color_based_edges(roi_image)
                if np.sum(edges) == 0:  # 如果颜色检测没有结果，使用传统边缘检测
                    edges = self._preprocess_for_edge_detection(roi_image)
                
                # 形态学操作，连接断开的边缘
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                
                # 查找轮廓
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    if self._is_button_like_contour(contour, roi_image.shape):
                        # 获取边界矩形
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # 调整到全图坐标
                        abs_x = roi_x + x
                        abs_y = roi_y + y
                        
                        # 计算置信度
                        confidence = self._calculate_button_confidence(contour, roi_image, x, y, w, h)
                        
                        # 计算中心点
                        center_x = abs_x + w // 2
                        center_y = abs_y + h // 2
                        
                        button_result = {
                            'type': 'button',
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': w,
                            'height': h,
                            'confidence': confidence,
                            'bbox': (abs_x, abs_y, w, h)
                        }
                        button_results.append(button_result)
            
            # 保存到缓存
            self._save_to_cache(cache_key, button_results)
            
            return button_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"按钮检测失败: {e}")
            return []
    
    def _is_button_like_contour(self, contour: np.ndarray, image_shape: tuple) -> bool:
        """判断轮廓是否像按钮"""
        # 获取按钮参数
        params = self._get_element_params('button')
        
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        if area < params['min_area'] or area > params['max_area']:
            return False
        
        # 获取边界矩形
        x, y, w, h = cv2.boundingRect(contour)
        
        # 检查长宽比
        aspect_ratio = w / h if h > 0 else 0
        if not (params['aspect_ratio_range'][0] <= aspect_ratio <= params['aspect_ratio_range'][1]):
            return False
        
        # 检查轮廓的矩形度（轮廓面积与边界矩形面积的比例）
        rect_area = w * h
        extent = area / rect_area if rect_area > 0 else 0
        if extent < 0.25:  # 按钮应该相对填满其边界矩形（降低阈值以适应更多形状）
            return False
        
        # 检查轮廓的凸性（按钮通常比较规整）
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = area / hull_area
            if solidity < 0.5:  # 按钮应该相对较凸（降低阈值以适应更多形状）
                return False
        
        # 检查周长与面积的关系（过滤细长的线条）
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity < 0.08:  # 过滤过于细长的形状（降低阈值以接受更多形状）
                return False
        
        # 添加尺寸检查，避免过小的误检（降低限制以识别小按钮）
        if w < 12 or h < 8:  # 按钮应该有最小尺寸（适当提高以避免误检）
            return False
        
        return True
    
    def _calculate_button_confidence(self, contour: np.ndarray, roi_image: np.ndarray, 
                                   x: int, y: int, w: int, h: int) -> float:
        """计算按钮的置信度"""
        try:
            confidence = 0.0
            
            # 基础置信度：基于几何特征
            area = cv2.contourArea(contour)
            rect_area = w * h
            extent = area / rect_area if rect_area > 0 else 0
            confidence += extent * 0.25  # 矩形度贡献25%
            
            # 凸性贡献
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = area / hull_area
                confidence += solidity * 0.15  # 凸性贡献15%
            
            # 长宽比贡献（接近正方形或常见按钮比例得分更高）
            aspect_ratio = w / h if h > 0 else 0
            if 0.5 <= aspect_ratio <= 3.0:  # 常见按钮比例
                confidence += 0.15
            elif 0.3 <= aspect_ratio <= 5.0:  # 稍宽泛的比例
                confidence += 0.1
            
            # 边缘强度分析（优化）
            roi_edges = self._preprocess_for_edge_detection(roi_image)
            button_edges = roi_edges[y:y+h, x:x+w]
            edge_density = np.sum(button_edges > 0) / (w * h) if w * h > 0 else 0
            if 0.08 <= edge_density <= 0.4:  # 适中的边缘密度范围
                confidence += 0.2
            elif 0.05 <= edge_density <= 0.6:  # 次优范围
                confidence += 0.1
            
            # 颜色特征分析（优化后）
            if len(roi_image.shape) == 3:
                button_region = roi_image[y:y+h, x:x+w]
                color_score = self._analyze_button_color_features(button_region)
                confidence += color_score * 0.25  # 颜色特征贡献25%
                
                # 添加尺寸加权：更大的按钮通常更可靠
                size_score = min((w * h) / 5000, 0.15)  # 最多15%加权
                confidence += size_score
            
            return min(confidence, 1.0)  # 确保置信度不超过1
            
        except Exception:
            return 0.4  # 默认置信度
    
    def _analyze_button_color_features(self, button_region: np.ndarray) -> float:
        """分析按钮颜色特征"""
        try:
            if button_region.size == 0:
                return 0.0
            
            # 转换到HSV
            hsv = cv2.cvtColor(button_region, cv2.COLOR_BGR2HSV)
            
            # 计算颜色直方图
            hist_h = cv2.calcHist([hsv], [0], None, [180], [0, 180])
            hist_s = cv2.calcHist([hsv], [1], None, [256], [0, 256])
            hist_v = cv2.calcHist([hsv], [2], None, [256], [0, 256])
            
            color_score = 0.0
            
            # 检查是否有明显的色彩（非灰度）或灰色系
            if np.max(hist_s[30:]) > np.max(hist_s[:30]) * 2:  # 有饱和度
                color_score += 0.3
            elif np.max(hist_s[:50]) > np.max(hist_s[50:]):  # 低饱和度（灰色系）
                color_score += 0.2
            
            # 检查亮度分布（按钮通常有中等亮度）
            if np.max(hist_v[60:220]) > np.max(hist_v[:60]) + np.max(hist_v[220:]):
                color_score += 0.25
            # 高亮按钮检测
            elif np.max(hist_v[180:]) > np.max(hist_v[:180]) * 1.5:
                color_score += 0.15
            
            # 检查是否为按钮常见颜色
            # 获取主要颜色
            h_mean = np.mean(hsv[:,:,0])
            s_mean = np.mean(hsv[:,:,1])
            v_mean = np.mean(hsv[:,:,2])
            
            # 优化后的按钮颜色检测
            # 绿色按钮（35-85度，更精确的范围）
            if 35 <= h_mean <= 85 and s_mean > 40 and v_mean > 50:
                color_score += 0.4  # 绿色按钮更高权重
            # 蓝色按钮（95-135度）
            elif 95 <= h_mean <= 135 and s_mean > 40:
                color_score += 0.35
            # 红色按钮（0-10度或170-180度）
            elif (0 <= h_mean <= 10 or 170 <= h_mean <= 180) and s_mean > 40:
                color_score += 0.35
            # 橙色/黄色按钮（10-35度）
            elif 10 <= h_mean <= 35 and s_mean > 40:
                color_score += 0.3
            # 灰色按钮（低饱和度但有足够亮度）
            elif s_mean <= 50 and 100 <= v_mean <= 200:
                color_score += 0.2
            
            return min(color_score, 1.0)
            
        except Exception:
            return 0.2
    
    def detect_links(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测链接元素（启用简化版本）"""
        try:
            # 获取图像
            if isinstance(image_source, np.ndarray):
                image = image_source
            else:
                image = self._get_image_from_source(image_source)
            
            # 检查缓存
            cache_key = self._get_cache_key(image, 'links')
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            link_results = []
            
            # 使用简化的文字检测来找链接
            height, width = image.shape[:2]
            roi_image = image  # 直接使用整个图像
            
            # 使用梯度检测文字区域作为链接候选
            text_regions = self._detect_text_with_gradient(roi_image)
            
            # 获取链接参数
            link_params = self._get_element_params('link')
            
            # 筛选符合链接特征的区域
            for text_region in text_regions:
                x, y, w, h = text_region['bbox']
                aspect_ratio = w / h if h > 0 else 0
                area = w * h
                
                # 链接通常较长且面积适中
                if (link_params['min_area'] <= area <= link_params['max_area'] and
                    link_params['aspect_ratio_range'][0] <= aspect_ratio <= link_params['aspect_ratio_range'][1]):
                    
                    link_result = {
                        'type': 'link',
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'width': w,
                        'height': h,
                        'confidence': text_region['confidence'] * 0.8,  # 链接置信度稍低
                        'bbox': (x, y, w, h)
                    }
                    link_results.append(link_result)
            
            # 保存到缓存
            self._save_to_cache(cache_key, link_results)
            
            return link_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"链接检测失败: {e}")
            return []
    
    def detect_input_fields(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测输入框元素（启用简化版本）"""
        try:
            # 获取图像
            if isinstance(image_source, np.ndarray):
                image = image_source
            else:
                image = self._get_image_from_source(image_source)
            
            # 检查缓存
            cache_key = self._get_cache_key(image, 'input_fields')
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            input_results = []
            
            # 使用边缘检测来找输入框
            height, width = image.shape[:2]
            roi_image = image
            
            # 转换为灰度图
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY) if len(roi_image.shape) == 3 else roi_image
            
            # 边缘检测
            edges = cv2.Canny(gray, 20, 100)
            
            # 形态学操作，连接断开的边缘形成矩形
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
            kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
            edges_h = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_h)
            edges_combined = cv2.morphologyEx(edges_h, cv2.MORPH_CLOSE, kernel_v)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 获取输入框参数
            input_params = self._get_element_params('input')
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # 输入框通常是长方形，宽度大于高度
                if (input_params['min_area'] <= area <= input_params['max_area'] and
                    input_params['aspect_ratio_range'][0] <= aspect_ratio <= input_params['aspect_ratio_range'][1] and
                    w >= 40 and h >= 8):  # 输入框最小尺寸
                    
                    # 计算简单的置信度
                    confidence = 0.6
                    
                    # 如果有明显的边框特征，提高置信度
                    if self._has_input_border_features(roi_image, x, y, w, h):
                        confidence += 0.2
                    
                    input_result = {
                        'type': 'input',
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'width': w,
                        'height': h,
                        'confidence': min(confidence, 1.0),
                        'bbox': (x, y, w, h)
                    }
                    input_results.append(input_result)
            
            # 保存到缓存
            self._save_to_cache(cache_key, input_results)
            
            return input_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"输入框检测失败: {e}")
            return []
    
    def _has_input_border_features(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
        """检查是否有输入框边框特征"""
        try:
            if x < 0 or y < 0 or x + w >= image.shape[1] or y + h >= image.shape[0]:
                return False
                
            # 提取输入框区域
            input_region = image[y:y+h, x:x+w]
            gray = cv2.cvtColor(input_region, cv2.COLOR_BGR2GRAY) if len(input_region.shape) == 3 else input_region
            
            # 检查边缘（输入框通常有明显的边框）
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (w * h) if w * h > 0 else 0
            
            # 输入框边缘密度适中
            return 0.05 <= edge_density <= 0.4
            
        except Exception:
            return False
    
    def detect_icons(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测图标元素（简化版本）"""
        try:
            # 获取图像
            if isinstance(image_source, np.ndarray):
                image = image_source
            else:
                image = self._get_image_from_source(image_source)
            
            # 检查缓存
            cache_key = self._get_cache_key(image, 'icons')
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            icon_results = []
            
            # 简化：只使用轮廓检测，禁用角点检测以提高速度
            height, width = image.shape[:2]
            roi_image = image  # 直接使用整个图像
            
            # 只使用轮廓检测（更快）
            contour_icons = self._detect_icons_by_contour(roi_image)
            
            # 直接添加结果无需坐标转换
            for icon in contour_icons:
                x, y, w, h = icon['bbox']
                
                icon_result = {
                    'type': 'icon',
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'width': w,
                    'height': h,
                    'confidence': icon['confidence'],
                    'bbox': (x, y, w, h)
                }
                icon_results.append(icon_result)
            
            # 保存到缓存
            self._save_to_cache(cache_key, icon_results)
            
            return icon_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"图标检测失败: {e}")
            return []
    
    def _detect_icons_by_contour(self, roi_image: np.ndarray) -> List[Dict]:
        """基于轮廓检测图标"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY) if len(roi_image.shape) == 3 else roi_image
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150)
            
            # 形态学操作，填充小的间隙
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            icons = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # 过滤不符合图标特征的轮廓
                if not self._is_icon_like_contour(contour, x, y, w, h):
                    continue
                
                # 计算置信度
                confidence = self._calculate_icon_confidence(contour, roi_image, x, y, w, h)
                
                icons.append({
                    'bbox': (x, y, w, h),
                    'confidence': confidence
                })
            
            return icons
            
        except Exception:
            return []
    
    def _detect_icons_by_corners(self, roi_image: np.ndarray) -> List[Dict]:
        """基于角点检测图标"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY) if len(roi_image.shape) == 3 else roi_image
            
            # Harris角点检测
            corners = cv2.cornerHarris(gray, 2, 3, 0.04)
            
            # 膨胀角点以便后续处理
            corners = cv2.dilate(corners, None)
            
            # 设置角点阈值
            threshold = 0.01 * corners.max()
            corner_coords = np.where(corners > threshold)
            
            # 聚类相近的角点来形成潜在的图标区域
            icons = self._cluster_corners_to_icons(corner_coords, roi_image.shape)
            
            return icons
            
        except Exception:
            return []
    
    def _is_icon_like_contour(self, contour: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
        """判断轮廓是否像图标"""
        # 获取图标参数
        icon_params = self._get_element_params('icon')
        
        # 面积检查
        area = cv2.contourArea(contour)
        if area < icon_params['min_area'] or area > icon_params['max_area']:
            return False
        
        # 长宽比检查（图标通常接近正方形）
        aspect_ratio = w / h if h > 0 else 0
        if not (icon_params['aspect_ratio_range'][0] <= aspect_ratio <= icon_params['aspect_ratio_range'][1]):
            return False
        
        # 尺寸检查（图标通常不会太大也不会太小）- 提高最小限制避免噪点
        if w < 8 or h < 8 or w > 150 or h > 150:
            return False
        
        # 检查填充度（图标通常比较紧凑）
        rect_area = w * h
        extent = area / rect_area if rect_area > 0 else 0
        if extent < 0.15:  # 图标应该有一定的填充度（降低阈值）
            return False
        
        return True
    
    def _calculate_icon_confidence(self, contour: np.ndarray, roi_image: np.ndarray,
                                 x: int, y: int, w: int, h: int) -> float:
        """计算图标的置信度"""
        try:
            confidence = 0.0
            
            # 长宽比评分（越接近正方形得分越高）
            aspect_ratio = w / h if h > 0 else 0
            if 0.8 <= aspect_ratio <= 1.25:  # 接近正方形
                confidence += 0.3
            elif 0.6 <= aspect_ratio <= 1.5:  # 稍微偏离正方形
                confidence += 0.2
            
            # 尺寸评分（常见图标尺寸）
            size = min(w, h)
            if 16 <= size <= 48:  # 常见图标尺寸
                confidence += 0.2
            elif 12 <= size <= 64:  # 稍大的范围
                confidence += 0.1
            
            # 轮廓紧密度
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                compactness = (4 * np.pi * area) / (perimeter * perimeter)
                if compactness > 0.5:  # 图标通常比较紧密
                    confidence += 0.2
            
            # 颜色一致性分析
            if len(roi_image.shape) == 3 and x >= 0 and y >= 0 and x+w < roi_image.shape[1] and y+h < roi_image.shape[0]:
                icon_region = roi_image[y:y+h, x:x+w]
                
                # 计算颜色的标准差
                color_std = np.std(icon_region.reshape(-1, 3), axis=0)
                avg_std = np.mean(color_std)
                
                # 图标通常有相对一致的颜色或明显的对比
                if avg_std < 20:  # 颜色一致
                    confidence += 0.15
                elif avg_std > 50:  # 有对比色（如图标的边缘）
                    confidence += 0.1
            
            # 边缘强度分析
            if len(roi_image.shape) == 3:
                gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = roi_image
            
            if x >= 0 and y >= 0 and x+w < gray.shape[1] and y+h < gray.shape[0]:
                icon_region = gray[y:y+h, x:x+w]
                edges = cv2.Canny(icon_region, 50, 150)
                edge_density = np.sum(edges > 0) / (w * h) if w * h > 0 else 0
                
                # 图标通常有清晰的边缘
                if 0.1 <= edge_density <= 0.6:
                    confidence += 0.15
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.3  # 默认置信度
    
    def _cluster_corners_to_icons(self, corner_coords: tuple, image_shape: tuple) -> List[Dict]:
        """将角点聚类成潜在的图标区域"""
        try:
            if len(corner_coords[0]) == 0:
                return []
            
            # 将角点坐标转换为点列表
            points = list(zip(corner_coords[1], corner_coords[0]))  # (x, y) 格式
            
            icons = []
            cluster_distance = 50  # 聚类距离阈值
            
            # 简单的聚类算法
            used = [False] * len(points)
            
            for i, point in enumerate(points):
                if used[i]:
                    continue
                
                # 找到相近的点
                cluster = [point]
                used[i] = True
                
                for j, other_point in enumerate(points[i+1:], i+1):
                    if used[j]:
                        continue
                    
                    # 计算距离
                    distance = np.sqrt((point[0] - other_point[0])**2 + (point[1] - other_point[1])**2)
                    if distance < cluster_distance:
                        cluster.append(other_point)
                        used[j] = True
                
                # 如果聚类有足够的点，认为是潜在的图标
                if len(cluster) >= 4:  # 至少4个角点
                    # 计算边界框
                    x_coords = [p[0] for p in cluster]
                    y_coords = [p[1] for p in cluster]
                    
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    w = x_max - x_min
                    h = y_max - y_min
                    
                    # 检查是否符合图标尺寸
                    if (self._icon_min_area <= w * h <= self._icon_max_area and 
                        self._icon_aspect_ratio_range[0] <= w/h <= self._icon_aspect_ratio_range[1]):
                        
                        # 基于角点数量计算置信度
                        confidence = min(len(cluster) / 10.0, 0.8)  # 角点越多，置信度越高
                        
                        icons.append({
                            'bbox': (x_min, y_min, w, h),
                            'confidence': confidence
                        })
            
            return icons
            
        except Exception:
            return []
    
    def detect_text_regions(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """检测文字区域（启用简化版本）"""
        try:
            # 获取图像
            if isinstance(image_source, np.ndarray):
                image = image_source
            else:
                image = self._get_image_from_source(image_source)
            
            # 检查缓存
            cache_key = self._get_cache_key(image, 'text_regions')
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            text_results = []
            
            # 使用梯度分析检测文字区域（性能较好的方法）
            height, width = image.shape[:2]
            roi_image = image
            
            # 使用多种检测方法提高覆盖率
            gradient_regions = self._detect_text_with_gradient(roi_image)
            mser_regions = self._detect_text_with_mser(roi_image)
            
            # 合并两种方法的结果，去除重复
            all_regions = gradient_regions + mser_regions
            merged_regions = self._merge_duplicate_regions(all_regions)
            
            # 转换为标准格式
            for region in merged_regions:
                x, y, w, h = region['bbox']
                
                text_result = {
                    'type': 'text',
                    'center_x': x + w // 2,
                    'center_y': y + h // 2,
                    'width': w,
                    'height': h,
                    'confidence': region['confidence'],
                    'bbox': (x, y, w, h)
                }
                text_results.append(text_result)
            
            # 保存到缓存
            self._save_to_cache(cache_key, text_results)
            
            return text_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"文字区域检测失败: {e}")
            return []
    
    def _detect_text_with_mser(self, roi_image: np.ndarray) -> List[Dict]:
        """使用MSER检测文字区域"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY) if len(roi_image.shape) == 3 else roi_image
            
            # 创建MSER检测器（优化参数以检测更多小文字）
            mser = cv2.MSER_create(
                _min_area=2,       # 进一步降低最小区域面积
                _max_area=10000,   # 增加最大区域面积
                _delta=2,          # 进一步降低增量参数，提高敏感性
                _max_variation=0.7,  # 增加最大变化率
                _min_diversity=0.05  # 进一步降低最小多样性
            )
            
            # 检测MSER区域
            regions, _ = mser.detectRegions(gray)
            
            text_regions = []
            for region in regions:
                # 获取边界框
                x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
                
                # 过滤不合适的区域
                if not self._is_text_like_region(region, x, y, w, h, gray):
                    continue
                
                # 计算置信度
                confidence = self._calculate_text_confidence(region, roi_image, x, y, w, h)
                
                text_regions.append({
                    'bbox': (x, y, w, h),
                    'confidence': confidence
                })
            
            return text_regions
            
        except Exception:
            return []
    
    def _detect_text_with_gradient(self, roi_image: np.ndarray) -> List[Dict]:
        """使用梯度分析检测文字区域（增强版，支持高亮背景）"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY) if len(roi_image.shape) == 3 else roi_image
            
            text_regions = []
            
            # 方法1: 传统梯度检测
            gradient_regions = self._detect_with_standard_gradient(gray, roi_image)
            text_regions.extend(gradient_regions)
            
            # 方法2: 自适应阈值检测（针对高亮背景）
            adaptive_regions = self._detect_with_adaptive_threshold(gray, roi_image)
            text_regions.extend(adaptive_regions)
            
            # 方法3: 颜色空间分析（针对彩色高亮）
            if len(roi_image.shape) == 3:
                color_regions = self._detect_with_color_analysis(roi_image)
                text_regions.extend(color_regions)
            
            # 方法4: 局部对比度增强检测
            enhanced_regions = self._detect_with_contrast_enhancement(gray, roi_image)
            text_regions.extend(enhanced_regions)
            
            # 去除重复区域
            unique_regions = self._merge_duplicate_regions(text_regions)
            
            return unique_regions
            
        except Exception:
            return []
    
    def _detect_with_standard_gradient(self, gray: np.ndarray, roi_image: np.ndarray) -> List[Dict]:
        """标准梯度检测方法"""
        try:
            # 计算梯度
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            text_regions = []
            
            # 使用多个阈值进行检测
            thresholds = [8, 12, 18, 25, 35]  # 增加更低阈值
            for threshold in thresholds:
                _, gradient_binary = cv2.threshold(gradient_magnitude.astype(np.uint8), threshold, 255, cv2.THRESH_BINARY)
                
                # 形态学操作
                kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 1))
                kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
                
                connected_h = cv2.morphologyEx(gradient_binary, cv2.MORPH_CLOSE, kernel_horizontal)
                connected = cv2.morphologyEx(connected_h, cv2.MORPH_CLOSE, kernel_vertical)
                
                # 查找轮廓
                contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    
                    text_params = self._get_element_params('text')
                    if (area >= text_params['min_area'] and area <= text_params['max_area']):
                        aspect_ratio = w / h if h > 0 else 0
                        if (text_params['aspect_ratio_range'][0] <= aspect_ratio <= text_params['aspect_ratio_range'][1]):
                            confidence = self._calculate_text_confidence_from_contour(contour, roi_image, x, y, w, h)
                            confidence *= (1.0 - (threshold - 12) * 0.03)  # 阈值调整
                            
                            text_regions.append({
                                'bbox': (x, y, w, h),
                                'confidence': max(0.1, min(1.0, confidence)),
                                'method': 'gradient'
                            })
            
            return text_regions
        except Exception:
            return []
    
    def _detect_with_adaptive_threshold(self, gray: np.ndarray, roi_image: np.ndarray) -> List[Dict]:
        """自适应阈值检测（针对高亮背景）"""
        try:
            text_regions = []
            
            # 使用自适应阈值处理不均匀光照
            adaptive_thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
            )
            
            # 反向阈值（检测亮背景上的暗文字）
            adaptive_thresh_inv = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
            )
            
            # 处理两种阈值结果
            for thresh_img, method_suffix in [(adaptive_thresh, '_normal'), (adaptive_thresh_inv, '_inv')]:
                # 形态学操作连接文字
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
                connected = cv2.morphologyEx(thresh_img, cv2.MORPH_CLOSE, kernel)
                
                # 查找轮廓
                contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    
                    text_params = self._get_element_params('text')
                    if (area >= text_params['min_area'] and area <= text_params['max_area']):
                        aspect_ratio = w / h if h > 0 else 0
                        if (text_params['aspect_ratio_range'][0] <= aspect_ratio <= text_params['aspect_ratio_range'][1]):
                            # 特别检查是否在高亮区域
                            confidence = self._calculate_highlight_text_confidence(gray, x, y, w, h)
                            
                            text_regions.append({
                                'bbox': (x, y, w, h),
                                'confidence': confidence,
                                'method': 'adaptive' + method_suffix
                            })
            
            return text_regions
        except Exception:
            return []
    
    def _detect_with_color_analysis(self, roi_image: np.ndarray) -> List[Dict]:
        """颜色空间分析检测（针对彩色高亮）"""
        try:
            text_regions = []
            
            # 转换到LAB颜色空间（对亮度变化更敏感）
            lab = cv2.cvtColor(roi_image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0]  # 亮度通道
            
            # 检测亮度变化
            l_grad = cv2.Laplacian(l_channel, cv2.CV_64F)
            l_grad_abs = np.absolute(l_grad)
            
            # 多阈值检测亮度变化
            for threshold in [5, 10, 15]:
                _, l_binary = cv2.threshold(l_grad_abs.astype(np.uint8), threshold, 255, cv2.THRESH_BINARY)
                
                # 形态学操作
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
                connected = cv2.morphologyEx(l_binary, cv2.MORPH_CLOSE, kernel)
                
                contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    
                    text_params = self._get_element_params('text')
                    if (area >= text_params['min_area'] and area <= text_params['max_area']):
                        aspect_ratio = w / h if h > 0 else 0
                        if (text_params['aspect_ratio_range'][0] <= aspect_ratio <= text_params['aspect_ratio_range'][1]):
                            confidence = self._calculate_color_text_confidence(roi_image, x, y, w, h)
                            
                            text_regions.append({
                                'bbox': (x, y, w, h),
                                'confidence': confidence,
                                'method': 'color_lab'
                            })
            
            return text_regions
        except Exception:
            return []
    
    def _detect_with_contrast_enhancement(self, gray: np.ndarray, roi_image: np.ndarray) -> List[Dict]:
        """局部对比度增强检测"""
        try:
            text_regions = []
            
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # 在增强后的图像上进行边缘检测
            edges = cv2.Canny(enhanced, 30, 100)
            
            # 形态学操作连接边缘
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
            connected = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                text_params = self._get_element_params('text')
                if (area >= text_params['min_area'] and area <= text_params['max_area']):
                    aspect_ratio = w / h if h > 0 else 0
                    if (text_params['aspect_ratio_range'][0] <= aspect_ratio <= text_params['aspect_ratio_range'][1]):
                        confidence = self._calculate_enhanced_text_confidence(enhanced, x, y, w, h)
                        
                        text_regions.append({
                            'bbox': (x, y, w, h),
                            'confidence': confidence,
                            'method': 'enhanced'
                        })
            
            return text_regions
        except Exception:
            return []
    
    def _calculate_highlight_text_confidence(self, gray: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """计算高亮区域文本的置信度"""
        try:
            confidence = 0.3  # 基础置信度
            
            # 提取文本区域
            text_region = gray[y:y+h, x:x+w]
            if text_region.size == 0:
                return confidence
            
            # 检查是否在高亮区域（亮度较高且相对均匀）
            mean_brightness = np.mean(text_region)
            brightness_std = np.std(text_region)
            
            # 高亮区域特征：高亮度，低标准差
            if mean_brightness > 180 and brightness_std < 30:
                confidence += 0.3  # 高亮区域加分
            elif mean_brightness > 150 and brightness_std < 50:
                confidence += 0.2  # 中等高亮加分
            
            # 检查边缘对比度（即使在高亮背景下，文字边缘仍有对比度）
            edges = cv2.Canny(text_region, 20, 60)
            edge_density = np.sum(edges > 0) / (w * h) if w * h > 0 else 0
            
            if edge_density > 0.05:
                confidence += 0.2
            elif edge_density > 0.02:
                confidence += 0.1
            
            # 长宽比加分
            aspect_ratio = w / h if h > 0 else 0
            if 2.0 <= aspect_ratio <= 15.0:  # 文本行的典型比例
                confidence += 0.2
            
            return min(confidence, 1.0)
        except Exception:
            return 0.3
    
    def _calculate_color_text_confidence(self, roi_image: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """计算彩色文本的置信度"""
        try:
            confidence = 0.3
            
            text_region = roi_image[y:y+h, x:x+w]
            if text_region.size == 0:
                return confidence
            
            # 转换到HSV分析颜色特征
            hsv_region = cv2.cvtColor(text_region, cv2.COLOR_BGR2HSV)
            
            # 检查饱和度变化（文字区域通常有饱和度变化）
            s_channel = hsv_region[:, :, 1]
            s_std = np.std(s_channel)
            
            if s_std > 20:
                confidence += 0.2
            elif s_std > 10:
                confidence += 0.1
            
            # 检查亮度变化
            v_channel = hsv_region[:, :, 2]
            v_std = np.std(v_channel)
            
            if v_std > 15:
                confidence += 0.2
            elif v_std > 8:
                confidence += 0.1
            
            # 长宽比检查
            aspect_ratio = w / h if h > 0 else 0
            if 1.5 <= aspect_ratio <= 20.0:
                confidence += 0.2
            
            return min(confidence, 1.0)
        except Exception:
            return 0.3
    
    def _calculate_enhanced_text_confidence(self, enhanced: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """计算增强后图像的文本置信度"""
        try:
            confidence = 0.3
            
            text_region = enhanced[y:y+h, x:x+w]
            if text_region.size == 0:
                return confidence
            
            # 检查对比度增强效果
            contrast = np.std(text_region)
            if contrast > 30:
                confidence += 0.3
            elif contrast > 20:
                confidence += 0.2
            
            # 检查边缘强度
            edges = cv2.Canny(text_region, 50, 150)
            edge_density = np.sum(edges > 0) / (w * h) if w * h > 0 else 0
            
            if edge_density > 0.1:
                confidence += 0.2
            elif edge_density > 0.05:
                confidence += 0.1
            
            # 尺寸合理性
            if w >= 10 and h >= 8:  # 合理的文本尺寸
                confidence += 0.2
            
            return min(confidence, 1.0)
        except Exception:
            return 0.3
            
        except Exception:
            return []
    
    def _merge_duplicate_regions(self, regions: List[Dict]) -> List[Dict]:
        """合并重复的文字区域"""
        if not regions:
            return []
        
        # 按置信度排序，保留高置信度的区域
        sorted_regions = sorted(regions, key=lambda x: x['confidence'], reverse=True)
        merged = []
        
        for region in sorted_regions:
            x, y, w, h = region['bbox']
            is_duplicate = False
            
            for existing in merged:
                ex, ey, ew, eh = existing['bbox']
                # 计算重叠率
                overlap_x = max(0, min(x + w, ex + ew) - max(x, ex))
                overlap_y = max(0, min(y + h, ey + eh) - max(y, ey))
                overlap_area = overlap_x * overlap_y
                
                # 计算IoU (Intersection over Union)
                union_area = w * h + ew * eh - overlap_area
                if union_area > 0:
                    iou = overlap_area / union_area
                    if iou > self._config.duplicate_iou_threshold:  # 使用统一配置的IoU阈值
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                merged.append(region)
        
        return merged
    
    def _is_text_like_region(self, region: np.ndarray, x: int, y: int, w: int, h: int, gray: np.ndarray) -> bool:
        """判断区域是否像文字"""
        # 获取文本参数
        text_params = self._get_element_params('text')
        
        # 面积检查
        area = w * h
        if area < text_params['min_area'] or area > text_params['max_area']:
            if self._debug_mode:
                print(f"[调试] 文字区域面积不符合: {area}, 要求范围: {text_params['min_area']}-{text_params['max_area']}")
            return False
        
        # 长宽比检查
        aspect_ratio = w / h if h > 0 else 0
        if not (text_params['aspect_ratio_range'][0] <= aspect_ratio <= text_params['aspect_ratio_range'][1]):
            if self._debug_mode:
                print(f"[调试] 文字区域长宽比不符合: {aspect_ratio:.2f}, 要求范围: {text_params['aspect_ratio_range']}")
            return False
        
        # 放宽区域密度检查（支持更多类型的文字，包括高亮背景）
        if x >= 0 and y >= 0 and x+w < gray.shape[1] and y+h < gray.shape[0]:
            region_pixels = gray[y:y+h, x:x+w]
            
            # 计算暗色和亮色像素比例
            dark_density = np.sum(region_pixels < 128) / (w * h)
            light_density = np.sum(region_pixels > 128) / (w * h)
            
            # 放宽密度限制，支持高亮背景文字
            if dark_density < 0.05 and light_density < 0.05:  # 只过滤完全中性灰的区域
                if self._debug_mode:
                    print(f"[调试] 文字区域像素密度不符合: 暗色{dark_density:.2f}, 亮色{light_density:.2f}")
                return False
        
        if self._debug_mode:
            print(f"[调试] 文字区域通过检查: 面积{area}, 长宽比{aspect_ratio:.2f}, 位置({x},{y},{w},{h})")
        return True
    
    def _calculate_text_confidence(self, region: np.ndarray, roi_image: np.ndarray, 
                                 x: int, y: int, w: int, h: int) -> float:
        """计算文字区域的置信度"""
        try:
            confidence = 0.0
            
            # 基础置信度：基于区域大小
            area = w * h
            text_params = self._get_element_params('text')
            if text_params['min_area'] <= area <= text_params['max_area']:
                confidence += 0.3
            
            # 长宽比贡献
            aspect_ratio = w / h if h > 0 else 0
            if 1.0 <= aspect_ratio <= 10.0:  # 常见文字比例
                confidence += 0.2
            elif 0.5 <= aspect_ratio <= 15.0:
                confidence += 0.1
            
            # 边缘密度分析
            if len(roi_image.shape) == 3:
                gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = roi_image
            
            if x >= 0 and y >= 0 and x+w < gray.shape[1] and y+h < gray.shape[0]:
                text_region = gray[y:y+h, x:x+w]
                
                # 计算边缘密度
                edges = cv2.Canny(text_region, 50, 150)
                edge_density = np.sum(edges > 0) / (w * h) if w * h > 0 else 0
                if 0.05 <= edge_density <= 0.3:  # 文字有适当的边缘密度
                    confidence += 0.3
                
                # 像素分布分析
                hist = cv2.calcHist([text_region], [0], None, [256], [0, 256])
                # 文字区域通常有双峰分布（前景和背景）
                peaks = []
                for i in range(1, 255):
                    if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 10:
                        peaks.append(i)
                
                if len(peaks) >= 2:  # 有多个峰值，类似文字特征
                    confidence += 0.2
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.4  # 默认置信度
    
    def _calculate_text_confidence_from_contour(self, contour: np.ndarray, roi_image: np.ndarray,
                                              x: int, y: int, w: int, h: int) -> float:
        """基于轮廓计算文字置信度"""
        try:
            confidence = 0.0
            
            # 面积密度
            contour_area = cv2.contourArea(contour)
            rect_area = w * h
            density = contour_area / rect_area if rect_area > 0 else 0
            if 0.3 <= density <= 0.8:  # 文字通常有适中的密度
                confidence += 0.3
            
            # 长宽比
            aspect_ratio = w / h if h > 0 else 0
            if 1.0 <= aspect_ratio <= 8.0:
                confidence += 0.2
            
            # 轮廓复杂度（文字通常有一定的复杂度）
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                complexity = (perimeter * perimeter) / contour_area if contour_area > 0 else 0
                if 10 <= complexity <= 100:  # 适当的复杂度
                    confidence += 0.2
            
            # 位置权重（屏幕中心的文字更可能是重要内容）
            roi_height, roi_width = roi_image.shape[:2]
            center_x_ratio = (x + w/2) / roi_width if roi_width > 0 else 0.5
            center_y_ratio = (y + h/2) / roi_height if roi_height > 0 else 0.5
            
            # 距离中心越近，权重越高
            distance_from_center = abs(center_x_ratio - 0.5) + abs(center_y_ratio - 0.5)
            if distance_from_center < 0.3:
                confidence += 0.3
            elif distance_from_center < 0.5:
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.4
    #endregion
    
    #region 辅助方法
    def _merge_overlapping_elements(self, elements: List[Dict], overlap_threshold: float = 0.3) -> List[Dict]:
        """合并重叠的元素（优化版）"""
        if not elements:
            return []
        
        # 按置信度排序，保留高置信度的元素
        elements = sorted(elements, key=lambda x: x['confidence'], reverse=True)
        
        merged = []
        used = [False] * len(elements)
        
        for i, elem1 in enumerate(elements):
            if used[i]:
                continue
                
            current_group = [elem1]
            used[i] = True
            
            for j, elem2 in enumerate(elements[i+1:], i+1):
                if used[j]:
                    continue
                    
                # 计算重叠（优化：只合并相似类型的元素）
                if elem1['type'] == elem2['type'] or self._are_similar_types(elem1['type'], elem2['type']):
                    overlap = self._calculate_element_overlap(elem1['bbox'], elem2['bbox'])
                    if overlap > overlap_threshold:
                        current_group.append(elem2)
                        used[j] = True
            
            # 合并当前组
            if len(current_group) == 1:
                merged.append(current_group[0])
            else:
                merged_element = self._merge_element_group(current_group)
                merged.append(merged_element)
        
        return merged
    
    def _calculate_element_overlap(self, bbox1: Tuple, bbox2: Tuple) -> float:
        """计算两个边界框的重叠比例"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # 计算交集
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
            
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        
        # 使用IoU（Intersection over Union）更精确的重叠计算
        union = area1 + area2 - intersection
        return intersection / union if union > 0 else 0.0
    
    def _are_similar_types(self, type1: str, type2: str) -> bool:
        """判断两个类型是否相似，可以合并"""
        # 定义可以合并的相似类型组
        similar_groups = [
            {'button', 'icon'},  # 按钮和图标可以合并
            {'link', 'text'},    # 链接和文字可以合并
        ]
        
        for group in similar_groups:
            if type1 in group and type2 in group:
                return True
        return False
    
    def _merge_element_group(self, group: List[Dict]) -> Dict:
        """合并一组元素"""
        if len(group) == 1:
            return group[0]
        
        # 计算合并后的边界框
        x_values = [elem['bbox'][0] for elem in group]
        y_values = [elem['bbox'][1] for elem in group]
        x2_values = [elem['bbox'][0] + elem['bbox'][2] for elem in group]
        y2_values = [elem['bbox'][1] + elem['bbox'][3] for elem in group]
        
        x = min(x_values)
        y = min(y_values)
        x2 = max(x2_values)
        y2 = max(y2_values)
        w = x2 - x
        h = y2 - y
        
        # 选择置信度最高的元素类型（优化：优先选择按钮类型）
        best_element = max(group, key=lambda x: (x['type'] == 'button', x['confidence']))
        
        return {
            'type': best_element['type'],
            'center_x': x + w // 2,
            'center_y': y + h // 2,
            'width': w,
            'height': h,
            'confidence': min(best_element['confidence'] * 1.1, 1.0),  # 合并后提高置信度
            'bbox': (x, y, w, h)
        }
    
    def _filter_low_confidence_elements(self, elements: List[Dict], 
                                       min_confidence: float = 0.4) -> List[Dict]:
        """过滤低置信度的元素（使用统一配置的阈值）"""
        filtered = []
        for element in elements:
            # 使用统一配置中的置信度阈值
            try:
                params = self._get_element_params(element['type'])
                threshold = params['confidence_threshold']
            except (KeyError, ValueError):
                threshold = min_confidence
            
            if element['confidence'] >= threshold:
                filtered.append(element)
                
        return filtered
    
    def get_recognition_statistics(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> Dict:
        """获取识别统计信息"""
        try:
            start_time = time.time()
            elements = self.detect_clickable_elements(image_source)
            elapsed_time = time.time() - start_time
            
            # 按类型统计
            type_counts = {}
            confidences_by_type = {}
            
            for elem in elements:
                elem_type = elem['type']
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
                if elem_type not in confidences_by_type:
                    confidences_by_type[elem_type] = []
                confidences_by_type[elem_type].append(elem['confidence'])
            
            # 计算平均置信度
            avg_confidences = {}
            for elem_type, confidences in confidences_by_type.items():
                avg_confidences[elem_type] = sum(confidences) / len(confidences)
            
            stats = {
                'total_elements': len(elements),
                'detection_time': elapsed_time,
                'elements_per_second': len(elements) / elapsed_time if elapsed_time > 0 else 0,
                'type_counts': type_counts,
                'average_confidences': avg_confidences,
                'cache_size': len(self._result_cache)
            }
            
            return stats
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"获取统计信息失败: {e}")
            raise
    #endregion
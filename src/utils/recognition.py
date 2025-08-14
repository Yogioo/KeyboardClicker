#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕文字和按钮识别模块
提供OCR文字识别和UI按钮检测功能
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Dict, Optional, Callable, Union
from PIL import Image
import os
import pyautogui
import platform
from . import detection_config as _config

class ScreenRecognizer:
    """屏幕识别工具类"""
    
    def __init__(self):
        """初始化屏幕识别器"""
        self._screenshot_tool = None
        self._on_recognition_callback: Optional[Callable] = None
        self._on_error_callback: Optional[Callable] = None
        
        # 配置Tesseract OCR可执行文件路径
        self._configure_tesseract_path()
        
        # OCR配置
        self._tesseract_config = '--oem 3 --psm 6'  # 默认配置
        
        # 检查必要组件
        self._check_dependencies()
    
    #region Tesseract配置
    def _configure_tesseract_path(self):
        """配置Tesseract OCR可执行文件路径"""
        try:
            # 先尝试检查是否已经配置或在PATH中
            pytesseract.get_tesseract_version()
            return  # 如果已经可用，直接返回
        except:
            pass  # 如果不可用，继续配置
        
        # 根据操作系统配置默认路径
        system = platform.system().lower()
        
        if system == "windows":
            # Windows系统的常见安装路径
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', 'Administrator'))
            ]
        elif system == "darwin":  # macOS
            possible_paths = [
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
                "/usr/bin/tesseract"
            ]
        else:  # Linux和其他Unix系统
            possible_paths = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
                "/snap/bin/tesseract"
            ]
        
        # 尝试找到可用的Tesseract路径
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                try:
                    # 验证配置是否成功
                    pytesseract.get_tesseract_version()
                    if self._on_recognition_callback:
                        self._on_recognition_callback(f"Tesseract OCR 路径已配置: {path}")
                    return
                except Exception as e:
                    continue  # 如果这个路径不工作，尝试下一个
        
        # 如果所有路径都不工作，记录错误
        if self._on_error_callback:
            self._on_error_callback(
                "无法找到Tesseract OCR可执行文件。请确保已安装Tesseract OCR，"
                "或手动设置 pytesseract.pytesseract.tesseract_cmd 变量。"
            )
    #endregion
        
    #region 依赖检查
    def _check_dependencies(self):
        """检查依赖组件是否可用"""
        try:
            # 检查tesseract是否安装
            pytesseract.get_tesseract_version()
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"Tesseract OCR 未正确安装: {e}")
            
        try:
            # 检查OpenCV
            cv2.__version__
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"OpenCV 未正确安装: {e}")
    #endregion
    
    #region 回调函数管理
    def set_recognition_callback(self, callback: Callable[[str], None]):
        """设置识别操作回调函数"""
        self._on_recognition_callback = callback
        
    def set_error_callback(self, callback: Callable[[str], None]):
        """设置错误回调函数"""
        self._on_error_callback = callback
    #endregion
    
    #region 配置管理
    def set_tesseract_config(self, config: str):
        """设置Tesseract OCR配置"""
        self._tesseract_config = config
        
    def set_button_detection_params(self, min_area: int = 100, max_area: int = 50000, 
                                  aspect_ratio_range: tuple = (0.2, 5.0)):
        """设置按钮检测参数"""
        self._button_min_area = min_area
        self._button_max_area = max_area
        self._button_aspect_ratio_range = aspect_ratio_range
    #endregion
    
    #region 图像预处理
    def _get_image_from_source(self, image_source: Union[str, Image.Image, np.ndarray, None]) -> np.ndarray:
        """从不同来源获取图像并转换为OpenCV格式"""
        try:
            if image_source is None:
                # 如果没有提供图像源，则截取当前屏幕
                screenshot = pyautogui.screenshot()
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            elif isinstance(image_source, str):
                # 如果是文件路径
                if not os.path.exists(image_source):
                    raise FileNotFoundError(f"图像文件不存在: {image_source}")
                image = cv2.imread(image_source)
            elif isinstance(image_source, Image.Image):
                # 如果是PIL Image对象
                image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
            elif isinstance(image_source, np.ndarray):
                # 如果已经是numpy数组
                image = image_source
            else:
                raise ValueError("不支持的图像源类型")
                
            if image is None:
                raise ValueError("无法加载图像")
                
            return image
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"获取图像失败: {e}")
            raise Exception(f"获取图像失败: {e}")
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """为OCR预处理图像"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 应用自适应阈值
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    #endregion
    
    #region 文字识别功能
    def recognize_text(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """识别图像中的文字"""
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            
            # 预处理图像
            processed_image = self._preprocess_for_ocr(image)
            
            # 使用pytesseract进行OCR识别
            # 获取详细信息包括边界框
            data = pytesseract.image_to_data(processed_image, config=self._tesseract_config, 
                                           output_type=pytesseract.Output.DICT)
            
            text_results = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                # 过滤掉置信度较低的结果
                confidence = int(data['conf'][i])
                if confidence > 30:  # 置信度阈值
                    text = data['text'][i].strip()
                    if text:  # 只处理非空文本
                        x = data['left'][i]
                        y = data['top'][i]
                        width = data['width'][i]
                        height = data['height'][i]
                        
                        # 计算中心点
                        center_x = x + width // 2
                        center_y = y + height // 2
                        
                        text_result = {
                            'type': 'text',
                            'text': text,
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': width,
                            'height': height,
                            'confidence': confidence / 100.0,  # 转换为0-1范围
                            'bbox': (x, y, width, height)
                        }
                        text_results.append(text_result)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"文字识别完成，发现 {len(text_results)} 个文字区域")
                
            return text_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"文字识别失败: {e}")
            raise Exception(f"文字识别失败: {e}")
    
    def recognize_text_simple(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> str:
        """简单文字识别，返回完整文本字符串"""
        try:
            image = self._get_image_from_source(image_source)
            processed_image = self._preprocess_for_ocr(image)
            
            text = pytesseract.image_to_string(processed_image, config=self._tesseract_config)
            
            if self._on_recognition_callback:
                self._on_recognition_callback("简单文字识别完成")
                
            return text.strip()
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"简单文字识别失败: {e}")
            raise Exception(f"简单文字识别失败: {e}")
    #endregion
    
    #region 按钮识别功能
    def _preprocess_for_button_detection(self, image: np.ndarray) -> np.ndarray:
        """为按钮检测预处理图像"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        
        return edges
    
    def _is_button_like_contour(self, contour: np.ndarray, image_shape: tuple) -> bool:
        """判断轮廓是否像按钮"""
        # 获取按钮参数
        button_params = _config.get_element_params('button')
        
        # 计算轮廓面积
        area = cv2.contourArea(contour)
        if area < button_params['min_area'] or area > button_params['max_area']:
            return False
        
        # 获取边界矩形
        x, y, w, h = cv2.boundingRect(contour)
        
        # 检查长宽比
        aspect_ratio = w / h
        if not (button_params['aspect_ratio_range'][0] <= aspect_ratio <= button_params['aspect_ratio_range'][1]):
            return False
        
        # 检查轮廓的矩形度
        rect_area = w * h
        extent = area / rect_area
        if extent < 0.5:  # 轮廓应该相对填满其边界矩形
            return False
        
        # 检查轮廓的凸性（按钮通常比较规整）
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity = area / hull_area
            if solidity < 0.8:  # 按钮应该相对较凸
                return False
        
        return True
    
    def recognize_buttons(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """识别图像中的按钮"""
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            original_image = image.copy()
            
            # 预处理图像用于按钮检测
            edges = self._preprocess_for_button_detection(image)
            
            # 查找轮廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            button_results = []
            
            for contour in contours:
                if self._is_button_like_contour(contour, image.shape):
                    # 获取边界矩形
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算中心点
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # 尝试识别按钮区域内的文字
                    button_region = original_image[y:y+h, x:x+w]
                    button_text = ""
                    try:
                        # 对按钮区域进行OCR
                        button_gray = cv2.cvtColor(button_region, cv2.COLOR_BGR2GRAY)
                        button_text = pytesseract.image_to_string(
                            button_gray, 
                            config='--oem 3 --psm 8'  # 单词模式
                        ).strip()
                    except:
                        pass  # 如果OCR失败，就留空
                    
                    # 计算置信度（基于轮廓特征的简单评分）
                    area = cv2.contourArea(contour)
                    rect_area = w * h
                    extent = area / rect_area if rect_area > 0 else 0
                    confidence = min(extent, 1.0)  # 简单的置信度计算
                    
                    button_result = {
                        'type': 'button',
                        'text': button_text,
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': w,
                        'height': h,
                        'confidence': confidence,
                        'bbox': (x, y, w, h)
                    }
                    button_results.append(button_result)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"按钮识别完成，发现 {len(button_results)} 个按钮")
                
            return button_results
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"按钮识别失败: {e}")
            raise Exception(f"按钮识别失败: {e}")
    
    def recognize_buttons_advanced(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """高级按钮识别（使用多种方法组合）"""
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            
            # 方法1: 轮廓检测
            contour_buttons = self.recognize_buttons(image)
            
            # 方法2: 模板匹配（检测常见按钮样式）
            template_buttons = self._detect_buttons_by_template(image)
            
            # 合并结果并去重
            all_buttons = contour_buttons + template_buttons
            unique_buttons = self._merge_overlapping_detections(all_buttons)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"高级按钮识别完成，发现 {len(unique_buttons)} 个按钮")
                
            return unique_buttons
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"高级按钮识别失败: {e}")
            raise Exception(f"高级按钮识别失败: {e}")
    
    def _detect_buttons_by_template(self, image: np.ndarray) -> List[Dict]:
        """通过模板匹配检测按钮（预留接口）"""
        # 这里可以实现基于模板匹配的按钮检测
        # 目前返回空列表，未来可以扩展
        return []
    
    def _merge_overlapping_detections(self, detections: List[Dict], overlap_threshold: float = 0.5) -> List[Dict]:
        """合并重叠的检测结果"""
        if not detections:
            return []
        
        # 简单的重叠合并算法
        merged = []
        used = [False] * len(detections)
        
        for i, det1 in enumerate(detections):
            if used[i]:
                continue
                
            current_group = [det1]
            used[i] = True
            
            for j, det2 in enumerate(detections[i+1:], i+1):
                if used[j]:
                    continue
                    
                # 计算重叠面积
                overlap = self._calculate_overlap(det1['bbox'], det2['bbox'])
                if overlap > overlap_threshold:
                    current_group.append(det2)
                    used[j] = True
            
            # 合并当前组
            if len(current_group) == 1:
                merged.append(current_group[0])
            else:
                merged_detection = self._merge_detection_group(current_group)
                merged.append(merged_detection)
        
        return merged
    
    def _calculate_overlap(self, bbox1: tuple, bbox2: tuple) -> float:
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
        
        return intersection / min(area1, area2)
    
    def _merge_detection_group(self, group: List[Dict]) -> Dict:
        """合并一组检测结果"""
        if len(group) == 1:
            return group[0]
        
        # 计算平均边界框
        x_values = [det['bbox'][0] for det in group]
        y_values = [det['bbox'][1] for det in group]
        x2_values = [det['bbox'][0] + det['bbox'][2] for det in group]
        y2_values = [det['bbox'][1] + det['bbox'][3] for det in group]
        
        x = min(x_values)
        y = min(y_values)
        x2 = max(x2_values)
        y2 = max(y2_values)
        w = x2 - x
        h = y2 - y
        
        # 合并文字（取最长的）
        texts = [det['text'] for det in group if det['text']]
        merged_text = max(texts, key=len) if texts else ""
        
        # 取最高置信度
        max_confidence = max(det['confidence'] for det in group)
        
        return {
            'type': 'button',
            'text': merged_text,
            'center_x': x + w // 2,
            'center_y': y + h // 2,
            'width': w,
            'height': h,
            'confidence': max_confidence,
            'bbox': (x, y, w, h)
        }
    #endregion
    
    #region 组合识别功能
    def recognize_all(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> Dict:
        """识别图像中的所有文字和按钮"""
        try:
            # 获取图像（只获取一次，避免重复截图）
            image = self._get_image_from_source(image_source)
            
            # 并行识别文字和按钮
            text_results = self.recognize_text(image)
            button_results = self.recognize_buttons(image)
            
            result = {
                'text': text_results,
                'buttons': button_results,
                'total_items': len(text_results) + len(button_results),
                'text_count': len(text_results),
                'button_count': len(button_results)
            }
            
            if self._on_recognition_callback:
                self._on_recognition_callback(
                    f"完整识别完成，发现 {result['text_count']} 个文字区域和 {result['button_count']} 个按钮"
                )
                
            return result
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"完整识别失败: {e}")
            raise Exception(f"完整识别失败: {e}")
    
    def find_elements_by_text(self, target_text: str, 
                            image_source: Union[str, Image.Image, np.ndarray, None] = None) -> List[Dict]:
        """根据文字内容查找元素"""
        try:
            # 识别所有内容
            all_results = self.recognize_all(image_source)
            
            matching_elements = []
            
            # 搜索匹配的文字
            for text_item in all_results['text']:
                if target_text.lower() in text_item['text'].lower():
                    matching_elements.append(text_item)
            
            # 搜索匹配的按钮
            for button_item in all_results['buttons']:
                if target_text.lower() in button_item['text'].lower():
                    matching_elements.append(button_item)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"文字搜索完成，找到 {len(matching_elements)} 个匹配项")
                
            return matching_elements
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"文字搜索失败: {e}")
            raise Exception(f"文字搜索失败: {e}")
    
    def get_element_at_position(self, x: int, y: int,
                              image_source: Union[str, Image.Image, np.ndarray, None] = None) -> Optional[Dict]:
        """获取指定位置的元素"""
        try:
            # 识别所有内容
            all_results = self.recognize_all(image_source)
            
            # 检查所有元素
            all_elements = all_results['text'] + all_results['buttons']
            
            for element in all_elements:
                bbox_x, bbox_y, bbox_w, bbox_h = element['bbox']
                if (bbox_x <= x <= bbox_x + bbox_w and 
                    bbox_y <= y <= bbox_y + bbox_h):
                    return element
            
            return None
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"位置查找失败: {e}")
            raise Exception(f"位置查找失败: {e}")
    #endregion
    
    #region 实用工具方法
    def save_annotated_image(self, image_source: Union[str, Image.Image, np.ndarray, None] = None,
                           output_path: str = "annotated_recognition.png",
                           show_text: bool = True, show_buttons: bool = True) -> str:
        """保存带标注的识别结果图像"""
        try:
            # 获取图像
            image = self._get_image_from_source(image_source)
            annotated_image = image.copy()
            
            # 识别所有内容
            all_results = self.recognize_all(image)
            
            # 绘制文字标注
            if show_text:
                for text_item in all_results['text']:
                    x, y, w, h = text_item['bbox']
                    # 绘制绿色矩形框
                    cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    # 添加标签
                    label = f"Text: {text_item['text'][:10]}..."
                    cv2.putText(annotated_image, label, (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # 绘制按钮标注
            if show_buttons:
                for button_item in all_results['buttons']:
                    x, y, w, h = button_item['bbox']
                    # 绘制蓝色矩形框
                    cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    # 添加标签
                    label = f"Button"
                    if button_item['text']:
                        label += f": {button_item['text'][:10]}..."
                    cv2.putText(annotated_image, label, (x, y - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # 保存图像
            cv2.imwrite(output_path, annotated_image)
            
            if self._on_recognition_callback:
                self._on_recognition_callback(f"标注图像已保存: {output_path}")
                
            return output_path
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"保存标注图像失败: {e}")
            raise Exception(f"保存标注图像失败: {e}")
    
    def get_recognition_statistics(self, image_source: Union[str, Image.Image, np.ndarray, None] = None) -> Dict:
        """获取识别统计信息"""
        try:
            all_results = self.recognize_all(image_source)
            
            # 计算统计信息
            stats = {
                'total_elements': all_results['total_items'],
                'text_elements': all_results['text_count'],
                'button_elements': all_results['button_count'],
                'average_text_confidence': 0.0,
                'average_button_confidence': 0.0,
                'text_length_stats': {
                    'min': 0, 'max': 0, 'average': 0.0
                },
                'button_size_stats': {
                    'min_area': 0, 'max_area': 0, 'average_area': 0.0
                }
            }
            
            # 文字统计
            if all_results['text']:
                text_confidences = [item['confidence'] for item in all_results['text']]
                stats['average_text_confidence'] = sum(text_confidences) / len(text_confidences)
                
                text_lengths = [len(item['text']) for item in all_results['text']]
                stats['text_length_stats'] = {
                    'min': min(text_lengths),
                    'max': max(text_lengths),
                    'average': sum(text_lengths) / len(text_lengths)
                }
            
            # 按钮统计
            if all_results['buttons']:
                button_confidences = [item['confidence'] for item in all_results['buttons']]
                stats['average_button_confidence'] = sum(button_confidences) / len(button_confidences)
                
                button_areas = [item['width'] * item['height'] for item in all_results['buttons']]
                stats['button_size_stats'] = {
                    'min_area': min(button_areas),
                    'max_area': max(button_areas),
                    'average_area': sum(button_areas) / len(button_areas)
                }
            
            return stats
            
        except Exception as e:
            if self._on_error_callback:
                self._on_error_callback(f"获取统计信息失败: {e}")
            raise Exception(f"获取统计信息失败: {e}")
    #endregion
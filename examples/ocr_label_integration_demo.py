#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR文字识别与标签显示集成演示
基于已有模块实现：截图 => 识别文字与位置 => 在文字位置显示唯一标签
"""

import sys
import os
import signal
import time
import tkinter as tk
from contextlib import contextmanager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.screenshot import ScreenshotTool
from src.utils.recognition import ScreenRecognizer
from src.utils.screen_labeler import ScreenLabeler

# 全局中断标志
_interrupted = False

@contextmanager
def keyboard_interrupt_handler():
    """键盘中断处理上下文管理器"""
    global _interrupted
    _interrupted = False
    
    def signal_handler(signum, frame):
        global _interrupted
        _interrupted = True
        print("\n[中断] 检测到键盘中断，正在安全退出...")
        
    old_handler = signal.signal(signal.SIGINT, signal_handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, old_handler)

def countdown_with_interrupt(seconds, message=""):
    """可中断的倒计时"""
    global _interrupted
    for i in range(seconds, 0, -1):
        if _interrupted:
            print("\n操作已取消")
            return False
        print(f"{message}{i}秒...", end='\r')
        time.sleep(1)
    if message:
        print(f"{message}开始执行！")
    return True

class OCRLabelIntegrator:
    """OCR识别与标签显示集成器"""
    
    def __init__(self):
        # 初始化各个组件
        self._screenshot_tool = ScreenshotTool()
        self._recognizer = ScreenRecognizer()
        self._labeler = ScreenLabeler()
        
        # 当前识别结果和标签映射
        self._current_detections = []
        self._label_mapping = {}
        
        # 边界框显示
        self._bbox_windows = []
        self._bbox_root = None
        
        # 设置回调
        self._setup_callbacks()
        
        # 优化OCR参数以获取更多文字
        self._optimize_ocr_settings()
    
    def _setup_callbacks(self):
        """设置组件回调"""
        self._screenshot_tool.set_screenshot_callback(self._on_screenshot)
        self._screenshot_tool.set_error_callback(self._on_error)
        
        self._recognizer.set_recognition_callback(self._on_recognition)
        self._recognizer.set_error_callback(self._on_error)
        
        self._labeler.SetCallback(self._on_label_success)
        self._labeler.SetErrorCallback(self._on_error)
    
    def _on_screenshot(self, msg):
        print(f"[截图] {msg}")
    
    def _on_recognition(self, msg):
        print(f"[识别] {msg}")
    
    def _on_label_success(self, msg):
        print(f"[标签] {msg}")
    
    def _on_error(self, msg):
        print(f"[错误] {msg}")
    
    def _optimize_ocr_settings(self):
        """优化OCR设置以获取更多文字识别结果"""
        try:
            # 设置更宽松的Tesseract配置
            # --psm 6: 假设一个统一的文本块
            # --psm 8: 将图像视为单个单词
            # --psm 11: 稀疏文本，尽可能多地找到文字
            optimized_config = '--oem 3 --psm 11 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789一二三四五六七八九十'
            
            self._recognizer.set_tesseract_config(optimized_config)
            print("[优化] 已设置更宽松的OCR参数以检测更多文字")
            
        except Exception as e:
            self._on_error(f"OCR参数优化失败: {e}")
    
    def SetOCRLowConfidence(self, enable=True):
        """设置是否启用低置信度文字检测"""
        try:
            if enable:
                # 降低置信度阈值以获取更多结果
                print("[设置] 启用低置信度文字检测模式")
                self._low_confidence_mode = True
            else:
                print("[设置] 禁用低置信度文字检测模式") 
                self._low_confidence_mode = False
                
        except Exception as e:
            self._on_error(f"设置低置信度模式失败: {e}")
    
    def RecognizeWithMultipleMethods(self, image_source):
        """使用超级多种方法进行文字识别以获取最多结果"""
        try:
            all_results = []
            
            # 方法1: 标准识别
            print("[识别] 使用标准参数识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 6')
            results1 = self._recognizer.recognize_text(image_source)
            all_results.extend(results1)
            print(f"[识别] 标准方法识别到 {len(results1)} 个区域")
            
            # 方法2: 稀疏文本模式
            print("[识别] 使用稀疏文本模式识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 11')
            results2 = self._recognizer.recognize_text(image_source)
            all_results.extend(results2)
            print(f"[识别] 稀疏文本模式识别到 {len(results2)} 个区域")
            
            # 方法3: 单词级识别
            print("[识别] 使用单词级识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 8')
            results3 = self._recognizer.recognize_text(image_source)
            all_results.extend(results3)
            print(f"[识别] 单词级识别到 {len(results3)} 个区域")
            
            # 方法4: 字符级识别
            print("[识别] 使用字符级识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 10')
            results4 = self._recognizer.recognize_text(image_source)
            all_results.extend(results4)
            print(f"[识别] 字符级识别到 {len(results4)} 个区域")
            
            # 方法5: 无约束识别（最激进）
            print("[识别] 使用无约束模式识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 13')
            results5 = self._recognizer.recognize_text(image_source)
            all_results.extend(results5)
            print(f"[识别] 无约束模式识别到 {len(results5)} 个区域")
            
            # 方法6: 原始线条识别
            print("[识别] 使用原始线条模式识别...")
            self._recognizer.set_tesseract_config('--oem 3 --psm 4')
            results6 = self._recognizer.recognize_text(image_source)
            all_results.extend(results6)
            print(f"[识别] 原始线条模式识别到 {len(results6)} 个区域")
            
            # 方法7: 低置信度识别
            print("[识别] 使用低置信度模式识别...")
            results7 = self._recognize_with_low_confidence(image_source)
            all_results.extend(results7)
            print(f"[识别] 低置信度模式识别到 {len(results7)} 个区域")
            
            # 方法8: 多尺度识别
            print("[识别] 使用多尺度模式识别...")
            results8 = self._recognize_with_multiple_scales(image_source)
            all_results.extend(results8)
            print(f"[识别] 多尺度模式识别到 {len(results8)} 个区域")
            
            # 去重和合并结果
            unique_results = self._merge_overlapping_results(all_results)
            print(f"[识别] 合并去重后共 {len(unique_results)} 个唯一区域")
            
            return unique_results
            
        except Exception as e:
            self._on_error(f"多方法识别失败: {e}")
            return []
    
    def _merge_overlapping_results(self, results):
        """合并重叠的识别结果"""
        try:
            if not results:
                return []
            
            # 按位置去重（相近位置的结果合并）
            unique_results = []
            merge_threshold = 20  # 像素阈值
            
            for result in results:
                is_duplicate = False
                
                for existing in unique_results:
                    # 计算中心点距离
                    distance = ((result['center_x'] - existing['center_x'])**2 + 
                              (result['center_y'] - existing['center_y'])**2)**0.5
                    
                    if distance < merge_threshold:
                        # 如果距离很近，保留置信度更高的
                        if result['confidence'] > existing['confidence']:
                            unique_results.remove(existing)
                            unique_results.append(result)
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_results.append(result)
            
            # 按置信度排序
            unique_results.sort(key=lambda x: x['confidence'], reverse=True)
            
            return unique_results
            
        except Exception as e:
            self._on_error(f"结果合并失败: {e}")
            return results
    
    def _recognize_with_low_confidence(self, image_source):
        """使用极低置信度阈值进行识别"""
        try:
            # 临时修改识别器以支持低置信度
            import pytesseract
            from PIL import Image
            import cv2
            import numpy as np
            
            # 获取图像
            if isinstance(image_source, str):
                image = cv2.imread(image_source)
            else:
                # 假设是PIL图像或numpy数组
                if hasattr(image_source, 'save'):  # PIL Image
                    image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
                else:  # numpy array
                    image = image_source
            
            # 转换为PIL格式进行OCR
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 使用极低置信度配置
            config = '--oem 3 --psm 11 -c tessedit_char_confidence=1'
            
            # 获取详细OCR数据
            data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
            
            results = []
            n_boxes = len(data['level'])
            
            for i in range(n_boxes):
                confidence = float(data['conf'][i])
                text = data['text'][i].strip()
                
                # 极低的置信度阈值（接受几乎所有识别结果）
                if confidence > 1 and len(text) > 0:  # 只要置信度>1%且有文字
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # 过滤过小的区域
                    if w > 3 and h > 3:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        result = {
                            'type': 'text',
                            'text': text,
                            'center_x': center_x,
                            'center_y': center_y,
                            'width': w,
                            'height': h,
                            'confidence': confidence / 100.0,
                            'bbox': (x, y, w, h)
                        }
                        results.append(result)
            
            return results
            
        except Exception as e:
            self._on_error(f"低置信度识别失败: {e}")
            return []
    
    def _recognize_with_multiple_scales(self, image_source):
        """使用多种图像缩放进行识别"""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            # 获取原始图像
            if isinstance(image_source, str):
                original_image = cv2.imread(image_source)
            else:
                if hasattr(image_source, 'save'):  # PIL Image
                    original_image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
                else:
                    original_image = image_source
            
            all_results = []
            scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]  # 不同缩放比例
            
            for scale in scales:
                try:
                    # 缩放图像
                    if scale != 1.0:
                        height, width = original_image.shape[:2]
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        scaled_image = cv2.resize(original_image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                    else:
                        scaled_image = original_image.copy()
                    
                    # 转换为PIL格式
                    pil_image = Image.fromarray(cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB))
                    
                    # 使用稀疏文本模式识别缩放后的图像
                    self._recognizer.set_tesseract_config('--oem 3 --psm 11')
                    scale_results = self._recognizer.recognize_text(pil_image)
                    
                    # 调整坐标回原始尺寸
                    if scale != 1.0:
                        for result in scale_results:
                            result['center_x'] = int(result['center_x'] / scale)
                            result['center_y'] = int(result['center_y'] / scale)
                            result['width'] = int(result['width'] / scale)
                            result['height'] = int(result['height'] / scale)
                            x, y, w, h = result['bbox']
                            result['bbox'] = (int(x / scale), int(y / scale), int(w / scale), int(h / scale))
                    
                    all_results.extend(scale_results)
                    
                except Exception as e:
                    print(f"[警告] 缩放 {scale} 识别失败: {e}")
                    continue
            
            return all_results
            
        except Exception as e:
            self._on_error(f"多尺度识别失败: {e}")
            return []
    
    def RecognizeWithSuperAggressiveMode(self, image_source):
        """超级激进模式：使用所有可能的方法识别文字"""
        try:
            print("🚀 启动超级激进识别模式...")
            all_results = []
            
            # 先用所有标准方法
            standard_results = self.RecognizeWithMultipleMethods(image_source)
            all_results.extend(standard_results)
            print(f"[激进] 标准方法总计识别到 {len(standard_results)} 个区域")
            
            # 添加图像预处理变体识别
            preprocessed_results = self._recognize_with_image_variants(image_source)
            all_results.extend(preprocessed_results)
            print(f"[激进] 图像变体识别到 {len(preprocessed_results)} 个区域")
            
            # 添加极低阈值识别
            extreme_results = self._recognize_with_extreme_settings(image_source)
            all_results.extend(extreme_results)
            print(f"[激进] 极限设置识别到 {len(extreme_results)} 个区域")
            
            # 最终合并和去重
            unique_results = self._merge_overlapping_results(all_results)
            print(f"🎯 [激进] 超级模式最终识别到 {len(unique_results)} 个唯一区域")
            
            return unique_results
            
        except Exception as e:
            self._on_error(f"超级激进模式失败: {e}")
            return []
    
    def _recognize_with_image_variants(self, image_source):
        """使用各种图像预处理变体进行识别"""
        try:
            import cv2
            import numpy as np
            from PIL import Image, ImageEnhance, ImageFilter
            
            # 获取原始图像
            if isinstance(image_source, str):
                original_image = cv2.imread(image_source)
                pil_original = Image.open(image_source)
            else:
                if hasattr(image_source, 'save'):  # PIL Image
                    pil_original = image_source
                    original_image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
                else:
                    original_image = image_source
                    pil_original = Image.fromarray(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
            
            all_results = []
            
            # 变体1: 高对比度
            print("[变体] 处理高对比度图像...")
            try:
                enhancer = ImageEnhance.Contrast(pil_original)
                high_contrast = enhancer.enhance(2.0)
                results1 = self._single_recognize(high_contrast)
                all_results.extend(results1)
                print(f"    高对比度识别到 {len(results1)} 个区域")
            except: pass
            
            # 变体2: 锐化图像
            print("[变体] 处理锐化图像...")
            try:
                sharpened = pil_original.filter(ImageFilter.SHARPEN)
                results2 = self._single_recognize(sharpened)
                all_results.extend(results2)
                print(f"    锐化识别到 {len(results2)} 个区域")
            except: pass
            
            # 变体3: 亮度增强
            print("[变体] 处理亮度增强图像...")
            try:
                brightness = ImageEnhance.Brightness(pil_original)
                bright_image = brightness.enhance(1.5)
                results3 = self._single_recognize(bright_image)
                all_results.extend(results3)
                print(f"    亮度增强识别到 {len(results3)} 个区域")
            except: pass
            
            # 变体4: 二值化处理
            print("[变体] 处理二值化图像...")
            try:
                gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                binary_pil = Image.fromarray(binary)
                results4 = self._single_recognize(binary_pil)
                all_results.extend(results4)
                print(f"    二值化识别到 {len(results4)} 个区域")
            except: pass
            
            # 变体5: 自适应阈值
            print("[变体] 处理自适应阈值图像...")
            try:
                gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
                adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                adaptive_pil = Image.fromarray(adaptive)
                results5 = self._single_recognize(adaptive_pil)
                all_results.extend(results5)
                print(f"    自适应阈值识别到 {len(results5)} 个区域")
            except: pass
            
            # 变体6: 形态学操作
            print("[变体] 处理形态学操作图像...")
            try:
                gray = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
                kernel = np.ones((2,2), np.uint8)
                morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
                morph_pil = Image.fromarray(morph)
                results6 = self._single_recognize(morph_pil)
                all_results.extend(results6)
                print(f"    形态学操作识别到 {len(results6)} 个区域")
            except: pass
            
            return all_results
            
        except Exception as e:
            self._on_error(f"图像变体识别失败: {e}")
            return []
    
    def _single_recognize(self, pil_image):
        """对单个图像进行快速识别"""
        try:
            self._recognizer.set_tesseract_config('--oem 3 --psm 11')
            return self._recognizer.recognize_text(pil_image)
        except:
            return []
    
    def _recognize_with_extreme_settings(self, image_source):
        """使用极限设置进行识别"""
        try:
            import pytesseract
            from PIL import Image
            import cv2
            import numpy as np
            
            # 获取图像
            if isinstance(image_source, str):
                image = cv2.imread(image_source)
            else:
                if hasattr(image_source, 'save'):  # PIL Image
                    image = cv2.cvtColor(np.array(image_source), cv2.COLOR_RGB2BGR)
                else:
                    image = image_source
            
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 极限配置：允许所有字符，最低置信度
            extreme_configs = [
                '--oem 3 --psm 13 -c tessedit_char_confidence=0',
                '--oem 1 --psm 11 -c tessedit_char_confidence=0',
                '--oem 2 --psm 13 -c tessedit_char_confidence=0',
                '--oem 3 --psm 12 -c tessedit_char_confidence=0'
            ]
            
            all_results = []
            
            for config in extreme_configs:
                try:
                    data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
                    
                    for i in range(len(data['level'])):
                        confidence = float(data['conf'][i])
                        text = data['text'][i].strip()
                        
                        # 几乎接受所有结果
                        if confidence >= 0 and len(text) > 0:
                            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                            
                            if w > 1 and h > 1:  # 最小尺寸检查
                                result = {
                                    'type': 'text',
                                    'text': text,
                                    'center_x': x + w // 2,
                                    'center_y': y + h // 2,
                                    'width': w,
                                    'height': h,
                                    'confidence': max(0.01, confidence / 100.0),  # 确保最小置信度
                                    'bbox': (x, y, w, h)
                                }
                                all_results.append(result)
                except:
                    continue
            
            return all_results
            
        except Exception as e:
            self._on_error(f"极限设置识别失败: {e}")
            return []
    
    def ShowTextBoundingBoxes(self, duration=2.0):
        """显示文字识别的边界框"""
        try:
            if not self._current_detections:
                self._on_error("没有识别结果，请先执行截图识别")
                return False
            
            # 清理之前的边界框
            self.HideBoundingBoxes()
            
            # 创建根窗口（如果不存在）
            if self._bbox_root is None:
                self._bbox_root = tk.Tk()
                self._bbox_root.withdraw()  # 隐藏主窗口
            
            print(f"[边界框] 显示 {len(self._current_detections)} 个文字区域的边界框")
            
            # 为每个检测结果创建边界框窗口
            for detection in self._current_detections:
                bbox_window = self._create_bbox_window(detection)
                if bbox_window:
                    self._bbox_windows.append(bbox_window)
            
            # 如果指定了持续时间，则自动隐藏
            if duration and duration > 0:
                self._bbox_root.after(int(duration * 1000), self.HideBoundingBoxes)
            
            return True
            
        except Exception as e:
            self._on_error(f"显示边界框失败: {e}")
            return False
    
    def _create_bbox_window(self, detection):
        """创建单个边界框窗口"""
        try:
            x, y, w, h = detection['bbox']
            
            # 创建透明窗口
            bbox_window = tk.Toplevel(self._bbox_root)
            bbox_window.overrideredirect(True)  # 无边框
            bbox_window.attributes('-topmost', True)  # 置顶
            bbox_window.attributes('-alpha', 0.8)  # 透明度
            
            # 设置窗口位置和大小
            bbox_window.geometry(f"{w}x{h}+{x}+{y}")
            
            # 创建画布绘制空心矩形
            canvas = tk.Canvas(
                bbox_window, 
                width=w, 
                height=h,
                highlightthickness=0,
                bg='black'
            )
            canvas.pack()
            
            # 绘制空心矩形（红色边框，透明内部）
            canvas.create_rectangle(
                2, 2, w-2, h-2,
                outline='red',
                fill='',
                width=2
            )
            
            # 设置透明背景
            bbox_window.wm_attributes('-transparentcolor', 'black')
            
            return bbox_window
            
        except Exception as e:
            self._on_error(f"创建边界框窗口失败: {e}")
            return None
    
    def HideBoundingBoxes(self):
        """隐藏所有边界框"""
        try:
            for window in self._bbox_windows:
                try:
                    window.destroy()
                except:
                    pass
            self._bbox_windows.clear()
            
            if self._bbox_root:
                try:
                    self._bbox_root.quit()
                    self._bbox_root.destroy()
                    self._bbox_root = None
                except:
                    pass
            
            print("[边界框] 所有边界框已隐藏")
            
        except Exception as e:
            self._on_error(f"隐藏边界框失败: {e}")
    
    def CaptureAndRecognize(self, save_screenshot=True, region=None, use_multiple_methods=False, use_super_aggressive=False):
        """截图并识别文字"""
        try:
            # 1. 截图
            if region is None:
                # 全屏截图
                if save_screenshot:
                    screenshot_path = self._screenshot_tool.capture_and_save_full_screen("ocr_capture.png")
                    print(f"[截图] 全屏截图已保存: {screenshot_path}")
                else:
                    screenshot = self._screenshot_tool.capture_full_screen()
                    screenshot_path = None
            else:
                # 区域截图
                x, y, width, height = region
                if save_screenshot:
                    screenshot_path = self._screenshot_tool.capture_and_save_region(
                        x, y, width, height, "ocr_region.png"
                    )
                    print(f"[截图] 区域截图已保存: {screenshot_path}")
                else:
                    screenshot = self._screenshot_tool.capture_region(x, y, width, height)
                    screenshot_path = None
            
            # 2. 文字识别
            if use_super_aggressive:
                # 使用超级激进模式
                if save_screenshot and screenshot_path:
                    text_results = self.RecognizeWithSuperAggressiveMode(screenshot_path)
                else:
                    text_results = self.RecognizeWithSuperAggressiveMode(screenshot)
            elif use_multiple_methods:
                # 使用多种方法进行识别以获取更多结果
                if save_screenshot and screenshot_path:
                    text_results = self.RecognizeWithMultipleMethods(screenshot_path)
                else:
                    text_results = self.RecognizeWithMultipleMethods(screenshot)
            else:
                # 使用标准方法识别
                if save_screenshot and screenshot_path:
                    text_results = self._recognizer.recognize_text(screenshot_path)
                else:
                    text_results = self._recognizer.recognize_text(screenshot)
            
            # 3. 调整坐标（如果是区域截图）
            if region is not None:
                offset_x, offset_y = region[0], region[1]
                for result in text_results:
                    result['center_x'] += offset_x
                    result['center_y'] += offset_y
                    # 更新bbox
                    x, y, w, h = result['bbox']
                    result['bbox'] = (x + offset_x, y + offset_y, w, h)
            
            self._current_detections = text_results
            print(f"[识别] 共识别到 {len(text_results)} 个文字区域")
            
            return len(text_results) > 0
            
        except Exception as e:
            self._on_error(f"截图识别失败: {e}")
            return False
    
    def ShowTextLabels(self, max_labels=None, duration=None):
        """为识别到的文字显示标签"""
        try:
            if not self._current_detections:
                self._on_error("没有识别结果，请先执行截图识别")
                return False
            
            # 按置信度排序，如果有max_labels限制则应用
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
            
            # 为每个文字区域创建标签元素
            label_elements = []
            self._label_mapping.clear()
            
            for i, (detection, label) in enumerate(zip(detections_to_label, labels)):
                element = {
                    'center_x': detection['center_x'],
                    'center_y': detection['center_y'],
                    'text': label,  # 使用生成的标签而不是原文字
                    'type': 'text'
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
                print(f"[标签] 为 {len(label_elements)} 个文字区域显示了标签")
                return True
            else:
                self._on_error("标签显示失败")
                return False
                
        except Exception as e:
            self._on_error(f"标签显示失败: {e}")
            return False
    
    def AnalyzeAndLabel(self, region=None, duration=None, max_labels=None, show_boxes=True, use_multiple_methods=False, use_super_aggressive=False):
        """一键分析：截图 => 识别 => 显示标签"""
        try:
            if use_super_aggressive:
                print("\n🚀 === 开始超级激进OCR分析流程 ===")
                print("⚠️  警告：这将使用所有可能的识别方法，耗时较长但识别最全面")
            elif use_multiple_methods:
                print("\n=== 开始深度OCR分析流程（多方法识别）===")
            else:
                print("\n=== 开始OCR分析流程 ===")
            
            # 1. 截图并识别
            if not self.CaptureAndRecognize(region=region, use_multiple_methods=use_multiple_methods, use_super_aggressive=use_super_aggressive):
                return False
            
            # 2. 显示边界框（如果启用）
            if show_boxes:
                print("[流程] 首先显示文字边界框...")
                if self.ShowTextBoundingBoxes(duration=3.0):
                    print("[流程] 边界框显示3秒，然后显示标签...")
                    time.sleep(3)
                    self.HideBoundingBoxes()
            
            # 3. 显示标签
            if not self.ShowTextLabels(max_labels=max_labels, duration=duration):
                return False
            
            # 4. 输出结果摘要
            print(f"\n=== 分析完成 ===")
            print(f"识别结果: {len(self._current_detections)} 个文字区域")
            if max_labels is not None:
                displayed_count = min(len(self._current_detections), max_labels)
                print(f"显示标签: {displayed_count} 个（限制: {max_labels}）")
            else:
                print(f"显示标签: {len(self._label_mapping)} 个（无限制）")
            
            # 显示标签映射
            if self._label_mapping:
                print("\n标签映射:")
                for label, info in list(self._label_mapping.items())[:10]:  # 只显示前10个
                    detection = info['detection']
                    print(f"  {label}: '{detection['text']}' 置信度:{detection['confidence']:.2f} 位置:({detection['center_x']}, {detection['center_y']})")
            
            return True
            
        except Exception as e:
            self._on_error(f"分析流程失败: {e}")
            return False
    
    def HideLabels(self):
        """隐藏所有标签和边界框"""
        try:
            # 隐藏标签
            self._labeler.HideLabels()
            self._label_mapping.clear()
            
            # 隐藏边界框
            self.HideBoundingBoxes()
            
            print("[清理] 所有标签和边界框已隐藏")
        except Exception as e:
            self._on_error(f"隐藏标签失败: {e}")
    
    def GetDetectionByLabel(self, label):
        """根据标签获取对应的识别结果"""
        return self._label_mapping.get(label, {}).get('detection')
    
    def GetCurrentDetections(self):
        """获取当前识别结果"""
        return self._current_detections.copy()
    
    def GetLabelMappings(self):
        """获取标签映射"""
        return self._label_mapping.copy()

def demo_ocr_label_integration():
    """演示OCR识别与标签显示集成功能"""
    print("=== OCR文字识别与标签显示集成演示 ===")
    print("功能: 截图 => 识别文字与位置 => 在文字位置显示唯一标签")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    integrator = OCRLabelIntegrator()
    
    with keyboard_interrupt_handler():
        try:
            print("\n=== 演示1: 全屏文字识别与标签 ===")
            if countdown_with_interrupt(3, "全屏分析倒计时: "):
                if not _interrupted:
                    success = integrator.AnalyzeAndLabel(duration=5.0)
                    if success:
                        print("\n标签将显示5秒...")
                        time.sleep(5)
            
            if _interrupted:
                return
                
            print("\n=== 演示2: 屏幕中心区域分析 ===")
            if countdown_with_interrupt(2, "区域分析倒计时: "):
                if not _interrupted:
                    # 分析屏幕中心800x600区域
                    screen_width, screen_height = integrator._screenshot_tool.get_screen_size()
                    x = (screen_width - 800) // 2
                    y = (screen_height - 600) // 2
                    region = (x, y, 800, 600)
                    
                    success = integrator.AnalyzeAndLabel(region=region, duration=0)
                    if success:
                        print("\n标签永久显示，按Enter继续...")
                        input()
            
            if _interrupted:
                return
                
            print("\n=== 演示3: 深度识别模式 ===")
            print("使用多种OCR方法识别更多文字...")
            # 左上角区域
            region = (50, 50, 600, 400)
            success = integrator.AnalyzeAndLabel(
                region=region, 
                duration=3.0, 
                use_multiple_methods=True
            )
            if success:
                print(f"\n深度识别 {region} 完成，应该识别到更多文字！标签显示3秒...")
                time.sleep(3)
            
            # 清理标签
            integrator.HideLabels()
            
            print("\n=== 演示完成 ===")
            
        except KeyboardInterrupt:
            print("\n[中断] 演示被用户中断")
        except Exception as e:
            print(f"演示过程中发生错误: {e}")
        finally:
            # 确保清理
            try:
                integrator.HideLabels()
            except:
                pass

def interactive_demo():
    """交互式演示"""
    print("\n=== 交互式OCR标签演示 ===")
    print("提示: 在任何输入提示处，按 Ctrl+C 可以安全退出")
    
    integrator = OCRLabelIntegrator()
    
    with keyboard_interrupt_handler():
        while not _interrupted:
            try:
                print("\n请选择操作:")
                print("1. 全屏文字识别与标签")
                print("2. 屏幕中心区域分析")
                print("3. 自定义区域分析")
                print("4. 深度识别模式（多方法识别更多文字）")
                print("5. 🚀 超级激进模式（最全面识别，耗时长）")
                print("6. 仅截图识别（不显示标签）")
                print("7. 为当前识别结果显示标签")
                print("8. 显示当前识别结果的边界框")
                print("9. 查看当前识别结果")
                print("10. 隐藏所有标签和边界框")
                print("0. 退出")
                
                choice = input("请输入选择 (0-10): ").strip()
                
                if _interrupted:
                    break
                    
                if choice == '1':
                    duration = input("标签显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    print("进行全屏分析...")
                    integrator.AnalyzeAndLabel(duration=duration)
                    
                elif choice == '2':
                    width = int(input("区域宽度（默认800）: ") or "800")
                    height = int(input("区域高度（默认600）: ") or "600")
                    
                    screen_width, screen_height = integrator._screenshot_tool.get_screen_size()
                    x = (screen_width - width) // 2
                    y = (screen_height - height) // 2
                    region = (x, y, width, height)
                    
                    print(f"分析屏幕中心区域 {region}...")
                    integrator.AnalyzeAndLabel(region=region)
                    
                elif choice == '3':
                    x = int(input("区域X坐标: ") or "100")
                    y = int(input("区域Y坐标: ") or "100")
                    width = int(input("区域宽度: ") or "400")
                    height = int(input("区域高度: ") or "300")
                    max_labels = int(input("最大标签数（默认100）: ") or "100")
                    
                    region = (x, y, width, height)
                    print(f"分析自定义区域 {region}...")
                    integrator.AnalyzeAndLabel(region=region, max_labels=max_labels)
                    
                elif choice == '4':
                    print("深度识别模式：使用多种OCR方法识别更多文字...")
                    region_choice = input("区域类型（1=全屏，2=自定义）: ").strip()
                    if region_choice == '2':
                        x = int(input("X坐标: ") or "0")
                        y = int(input("Y坐标: ") or "0")
                        width = int(input("宽度: ") or "800")
                        height = int(input("高度: ") or "600")
                        region = (x, y, width, height)
                    else:
                        region = None
                    
                    duration = input("标签显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    
                    print("⚠️  深度识别需要较长时间，请耐心等待...")
                    success = integrator.AnalyzeAndLabel(
                        region=region, 
                        duration=duration, 
                        use_multiple_methods=True
                    )
                    if success:
                        print("✓ 深度识别完成！应该能检测到更多文字区域")
                    
                elif choice == '5':
                    print("🚀 超级激进模式：使用所有可能的识别方法...")
                    print("⚠️  注意：这个模式会使用多种图像预处理和极低置信度阈值")
                    print("⚠️  预计耗时：1-3分钟，但能识别到最多的文字")
                    
                    confirm = input("确认启动超级激进模式？(y/N): ").strip().lower()
                    if confirm != 'y':
                        print("已取消")
                        continue
                    
                    region_choice = input("区域类型（1=全屏，2=自定义）: ").strip()
                    if region_choice == '2':
                        x = int(input("X坐标: ") or "0")
                        y = int(input("Y坐标: ") or "0")
                        width = int(input("宽度: ") or "800")
                        height = int(input("高度: ") or "600")
                        region = (x, y, width, height)
                    else:
                        region = None
                    
                    duration = input("标签显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    
                    print("\n🚀 启动超级激进识别，请耐心等待...")
                    success = integrator.AnalyzeAndLabel(
                        region=region, 
                        duration=duration, 
                        use_super_aggressive=True
                    )
                    if success:
                        print("🎯 超级激进识别完成！这是能识别到的最多文字了！")
                    
                elif choice == '6':
                    region_choice = input("区域类型（1=全屏，2=自定义）: ").strip()
                    if region_choice == '2':
                        x = int(input("X坐标: ") or "0")
                        y = int(input("Y坐标: ") or "0")
                        width = int(input("宽度: ") or "800")
                        height = int(input("高度: ") or "600")
                        region = (x, y, width, height)
                    else:
                        region = None
                    
                    success = integrator.CaptureAndRecognize(region=region)
                    if success:
                        print("✓ 截图识别完成，使用选项7显示标签")
                    
                elif choice == '7':
                    max_labels = int(input("最大标签数（默认100）: ") or "100")
                    duration = input("显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    
                    integrator.ShowTextLabels(max_labels=max_labels, duration=duration)
                    
                elif choice == '8':
                    duration = input("边界框显示时长（秒，空=永久）: ").strip()
                    duration = float(duration) if duration else None
                    integrator.ShowTextBoundingBoxes(duration=duration)
                    
                elif choice == '9':
                    detections = integrator.GetCurrentDetections()
                    mappings = integrator.GetLabelMappings()
                    
                    if detections:
                        print(f"\n当前识别结果 ({len(detections)} 个):")
                        for i, detection in enumerate(detections[:10]):
                            print(f"  {i+1}. '{detection['text']}' - 置信度:{detection['confidence']:.2f} 位置:({detection['center_x']}, {detection['center_y']})")
                    else:
                        print("当前没有识别结果")
                        
                    if mappings:
                        print(f"\n当前标签映射 ({len(mappings)} 个):")
                        for label, info in list(mappings.items())[:10]:
                            detection = info['detection']
                            print(f"  {label}: '{detection['text']}'")
                    
                elif choice == '10':
                    integrator.HideLabels()
                    
                elif choice == '0':
                    print("退出演示")
                    break
                    
                else:
                    print("无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n[中断] 演示被用户中断")
                break
            except ValueError:
                print("输入格式错误，请重新输入")
            except Exception as e:
                print(f"操作失败: {e}")
                
        if _interrupted:
            print("\n[中断] 交互式演示已安全退出")
        
        # 清理
        try:
            integrator.HideLabels()
        except:
            pass

if __name__ == "__main__":
    print("🚀 OCR文字识别与标签显示集成演示程序（超强版）")
    print("功能流程: 截图 => 识别文字 => 显示边界框 => 显示唯一标签")
    print("识别模式:")
    print("  📊 标准模式：快速识别常见文字")
    print("  🔍 深度模式：使用8种方法识别更多文字")
    print("  🚀 超级激进模式：使用所有可能方法，识别最全面（耗时长）")
    print("新特性: ✓ 无标签数量上限 ✓ 边界框预览 ✓ 多尺度识别 ✓ 极低置信度阈值")
    print("依赖: ScreenshotTool + ScreenRecognizer + ScreenLabeler")
    print("提示: 按 Ctrl+C 可以随时安全退出")
    
    try:
        demo_type = input("\n选择演示类型 (1=自动演示, 2=交互式演示): ").strip()
        
        if demo_type == '1':
            demo_ocr_label_integration()
        elif demo_type == '2':
            interactive_demo()
        else:
            print("默认运行自动演示...")
            demo_ocr_label_integration()
            
    except KeyboardInterrupt:
        print("\n[中断] 程序已安全退出")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        print("\n可能的解决方案:")
        print("1. 确保已安装tesseract-ocr")
        print("2. 检查requirements.txt中的依赖是否已安装")
        print("3. 确保已有的模块文件存在且正常工作")
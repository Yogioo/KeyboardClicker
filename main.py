#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的键盘点击屏幕工具
只保留核心功能：截图识别 + 显示边界框/标签
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.utils.fast_label_integrator import FastLabelIntegrator
from src.gui.debug_config_gui import DebugConfigGUI
from src.utils.detection_config import detection_config
from src.utils.unified_recognizer_adapter import UnifiedRecognizerAdapter
from src.utils.optimized_bbox_overlay import OptimizedBoundingBoxOverlay
from src.utils.screenshot import ScreenshotTool

class SimpleKeyboardClickerApp:
    """简化的键盘点击应用"""
    
    def __init__(self):
        # 初始化快速识别集成器
        self.fast_integrator = FastLabelIntegrator()
        
        # 初始化调试配置GUI
        self.debug_config_gui = None
        
        # 初始化统一视觉识别器（用于单独检测）
        self.recognizer = UnifiedRecognizerAdapter()
        self.recognizer.set_recognition_callback(self._on_recognition_result)
        self.recognizer.set_error_callback(self._on_recognition_error)
        
        # 初始化边界框覆盖层和截图工具  
        self.bbox_overlay = OptimizedBoundingBoxOverlay()
        self.screenshot_tool = ScreenshotTool()
        
        # 创建GUI
        self._create_gui()
        
    def _create_gui(self):
        """创建简化的用户界面"""
        self.root = tk.Tk()
        self.root.title("快速识别工具 - 调试版")
        self.root.geometry("400x500")
        self.root.resizable(True, True)
        
        # 标题
        title_label = tk.Label(
            self.root, 
            text="快速视觉识别工具", 
            font=("Arial", 14, "bold"),
            fg="blue"
        )
        title_label.pack(pady=10)
        
        # 说明文本
        info_label = tk.Label(
            self.root,
            text="截图全屏并快速识别可点击元素",
            font=("Arial", 9),
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 基本功能标签页
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基本功能")
        
        # 基本功能按钮
        basic_button_frame = tk.Frame(basic_frame)
        basic_button_frame.pack(pady=20)
        
        # 按钮1：显示边界框
        self.show_boxes_btn = tk.Button(
            basic_button_frame,
            text="截图并显示边界框",
            command=self._show_bounding_boxes,
            bg="lightblue",
            font=("Arial", 10),
            width=20,
            height=2
        )
        self.show_boxes_btn.pack(pady=5)
        
        # 按钮2：显示标签
        self.show_labels_btn = tk.Button(
            basic_button_frame,
            text="截图并显示标签",
            command=self._show_labels,
            bg="lightgreen",
            font=("Arial", 10),
            width=20,
            height=2
        )
        self.show_labels_btn.pack(pady=5)
        
        # 调试功能标签页
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="调试功能")
        
        # 调试模式选择
        debug_mode_frame = ttk.LabelFrame(debug_frame, text="调试模式")
        debug_mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.debug_mode_var = tk.StringVar(value="normal")
        
        # 正常模式
        ttk.Radiobutton(
            debug_mode_frame, 
            text="正常模式（检测所有启用的元素）", 
            variable=self.debug_mode_var, 
            value="normal",
            command=self._on_debug_mode_changed
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 单独检测模式
        debug_options = [
            ("button", "仅检测按钮"),
            ("link", "仅检测链接"),
            ("input", "仅检测输入框"),
            ("icon", "仅检测图标"),
            ("text", "仅检测文字区域")
        ]
        
        for value, text in debug_options:
            ttk.Radiobutton(
                debug_mode_frame, 
                text=text, 
                variable=self.debug_mode_var, 
                value=value,
                command=self._on_debug_mode_changed
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 调试操作按钮
        debug_action_frame = ttk.LabelFrame(debug_frame, text="调试操作")
        debug_action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 单独检测按钮
        self.debug_detect_btn = tk.Button(
            debug_action_frame,
            text="执行调试检测",
            command=self._debug_detect,
            bg="orange",
            font=("Arial", 10),
            width=20,
            height=2
        )
        self.debug_detect_btn.pack(pady=10)
        
        # 配置参数按钮
        self.config_btn = tk.Button(
            debug_action_frame,
            text="打开配置界面",
            command=self._open_config,
            bg="lightcyan",
            font=("Arial", 10),
            width=20,
            height=2
        )
        self.config_btn.pack(pady=5)
        
        # 检测类型启用开关（正常模式）
        enable_frame = ttk.LabelFrame(debug_frame, text="检测类型启用开关（正常模式）")
        enable_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.enable_vars = {}
        enable_options = [
            ("button", "启用按钮检测", detection_config.enable_button_detection),
            ("link", "启用链接检测", detection_config.enable_link_detection),
            ("input", "启用输入框检测", detection_config.enable_input_detection),
            ("icon", "启用图标检测", detection_config.enable_icon_detection),
            ("text", "启用文字检测", detection_config.enable_text_detection)
        ]
        
        for element_type, text, default_value in enable_options:
            var = tk.BooleanVar(value=default_value)
            self.enable_vars[element_type] = var
            ttk.Checkbutton(
                enable_frame, 
                text=text, 
                variable=var,
                command=lambda et=element_type: self._on_enable_changed(et)
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root,
            text="就绪",
            font=("Arial", 9),
            fg="green"
        )
        self.status_label.pack(pady=10)
        
        # 隐藏按钮
        hide_frame = tk.Frame(self.root)
        hide_frame.pack()
        
        hide_btn = tk.Button(
            hide_frame,
            text="隐藏所有显示",
            command=self._hide_all,
            bg="lightcoral",
            font=("Arial", 8),
            width=15
        )
        hide_btn.pack()
    
    def _update_status(self, text, color="black"):
        """更新状态显示"""
        self.status_label.config(text=text, fg=color)
    
    def _on_debug_mode_changed(self):
        """调试模式改变时的回调"""
        mode = self.debug_mode_var.get()
        if mode == "normal":
            detection_config.set_debug_mode(None)
        else:
            detection_config.set_debug_mode(mode)
        
        self._update_status(f"调试模式已切换到: {mode}", "blue")
    
    def _on_enable_changed(self, element_type: str):
        """检测类型启用状态改变时的回调"""
        enabled = self.enable_vars[element_type].get()
        detection_config.toggle_detection_type(element_type, enabled)
        
        status = "启用" if enabled else "禁用"
        self._update_status(f"{element_type}检测已{status}", "blue")
    
    def _debug_detect(self):
        """执行调试检测"""
        try:
            import time
            total_operation_start = time.time()
            
            mode = self.debug_mode_var.get()
            print(f"\n{'='*60}")
            print(f"开始调试检测流程 - 模式: {mode}")
            print(f"{'='*60}")
            
            self._update_status("正在截图并执行调试检测...", "orange")
            
            # 截图阶段计时
            screenshot_start = time.time()
            print("=== 调试检测：开始截图 ===")
            screenshot = self.screenshot_tool.capture_full_screen()
            screenshot_time = time.time() - screenshot_start
            print(f"=== 调试检测：截图耗时 {screenshot_time:.3f} 秒 ===")
            
            if screenshot is None:
                self._update_status("截图失败", "red")
                messagebox.showerror("错误", "截图失败，无法进行检测")
                return
            
            # 检测阶段计时
            detection_start = time.time()
            print(f"=== 调试检测：开始{mode}模式检测 ===")
            
            if mode == "normal":
                # 正常模式：检测所有启用的类型
                elements = self.recognizer.detect_clickable_elements(screenshot)
                detection_type = "正常模式检测"
            else:
                # 单独检测模式
                elements = self.recognizer.detect_single_type(mode, screenshot)
                detection_type = f"单独{mode}检测"
            
            detection_time = time.time() - detection_start
            print(f"=== 调试检测：检测阶段耗时 {detection_time:.3f} 秒 ===")
            print(f"=== 调试检测：检测到 {len(elements)} 个元素 ===")
            
            # 结果显示阶段计时
            display_start = time.time()
            print("=== 调试检测：开始显示结果 ===")
            self._show_debug_results(elements, detection_type, screenshot, {
                'screenshot_time': screenshot_time,
                'detection_time': detection_time,
                'total_elements': len(elements),
                'mode': mode
            })
            display_time = time.time() - display_start
            print(f"=== 调试检测：结果显示耗时 {display_time:.3f} 秒 ===")
            
            # 总体性能报告
            total_operation_time = time.time() - total_operation_start
            print(f"\n{'='*60}")
            print(f"调试检测性能报告 - {mode}模式")
            print(f"{'='*60}")
            print(f"总耗时: {total_operation_time:.3f} 秒")
            print(f"  - 截图: {screenshot_time:.3f} 秒 ({screenshot_time/total_operation_time*100:.1f}%)")
            print(f"  - 检测: {detection_time:.3f} 秒 ({detection_time/total_operation_time*100:.1f}%)")
            print(f"  - 结果显示: {display_time:.3f} 秒 ({display_time/total_operation_time*100:.1f}%)")
            if len(elements) > 0:
                print(f"检测效率: {len(elements)/detection_time:.1f} 个元素/秒")
            print(f"{'='*60}")
                
        except Exception as e:
            self._update_status(f"调试检测失败: {e}", "red")
            messagebox.showerror("错误", f"调试检测失败: {e}")
    
    def _show_debug_results(self, elements, title, screenshot=None, performance_data=None):
        """显示调试检测结果（可视化）"""
        if not elements:
            self._update_status("未检测到任何元素", "orange")
            messagebox.showinfo("调试结果", "未检测到任何元素")
            return
        
        # 创建结果显示窗口
        result_window = tk.Toplevel(self.root)
        result_window.title(f"{title} - 检测结果")
        result_window.geometry("800x600")
        
        # 创建主框架
        main_frame = tk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 显示边界框按钮
        show_bbox_btn = tk.Button(
            button_frame,
            text="显示边界框",
            command=lambda: self._show_detection_bboxes(elements),
            bg="lightblue",
            font=("Arial", 10)
        )
        show_bbox_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 隐藏边界框按钮
        hide_bbox_btn = tk.Button(
            button_frame,
            text="隐藏边界框",
            command=self.bbox_overlay.HideBoundingBoxes,
            bg="lightcoral",
            font=("Arial", 10)
        )
        hide_bbox_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 保存截图按钮（如果有截图）
        if screenshot is not None:
            save_btn = tk.Button(
                button_frame,
                text="保存带标注的截图",
                command=lambda: self._save_annotated_screenshot(screenshot, elements, title),
                bg="lightgreen",
                font=("Arial", 10)
            )
            save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 创建文本框显示结果
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示检测结果
        result_text = f"{title}\n" + "="*50 + "\n\n"
        result_text += f"检测到 {len(elements)} 个元素:\n\n"
        
        # 添加性能信息
        if performance_data:
            result_text += "性能分析:\n" + "-"*30 + "\n"
            if 'screenshot_time' in performance_data:
                result_text += f"截图耗时: {performance_data['screenshot_time']:.3f} 秒\n"
            if 'detection_time' in performance_data:
                result_text += f"检测耗时: {performance_data['detection_time']:.3f} 秒\n"
            if 'total_elements' in performance_data and performance_data['total_elements'] > 0:
                if 'detection_time' in performance_data and performance_data['detection_time'] > 0:
                    efficiency = performance_data['total_elements'] / performance_data['detection_time']
                    result_text += f"检测效率: {efficiency:.1f} 个元素/秒\n"
            if 'mode' in performance_data:
                result_text += f"检测模式: {performance_data['mode']}\n"
            result_text += "\n检测详情:\n" + "-"*30 + "\n\n"
        
        for i, element in enumerate(elements, 1):
            result_text += f"{i}. 类型: {element['type']}\n"
            result_text += f"   位置: ({element['center_x']}, {element['center_y']})\n"
            result_text += f"   大小: {element['width']} x {element['height']}\n"
            result_text += f"   置信度: {element['confidence']:.3f}\n"
            result_text += f"   边界框: {element['bbox']}\n\n"
        
        text_widget.insert(tk.END, result_text)
        text_widget.config(state=tk.DISABLED)
        
        # 添加关闭按钮
        close_btn = tk.Button(
            main_frame,
            text="关闭",
            command=result_window.destroy,
            bg="lightgray",
            font=("Arial", 10)
        )
        close_btn.pack(pady=10)
        
        # 自动显示边界框
        self._show_detection_bboxes(elements)
        
        self._update_status(f"检测完成，找到 {len(elements)} 个元素", "green")
    
    def _show_detection_bboxes(self, elements):
        """显示检测结果的边界框"""
        try:
            # 转换元素格式为边界框覆盖层需要的格式
            detections = []
            for element in elements:
                detection = {
                    'bbox': element['bbox'],
                    'type': element['type'],
                    'confidence': element['confidence']
                }
                detections.append(detection)
            
            # 显示边界框
            success = self.bbox_overlay.ShowBoundingBoxes(
                detections, 
                duration=None,  # 永久显示，直到手动隐藏
                box_color='red',
                box_width=3,
                alpha=0.8
            )
            
            if success:
                self._update_status(f"已显示 {len(elements)} 个检测结果的边界框", "green")
            else:
                self._update_status("显示边界框失败", "red")
                
        except Exception as e:
            self._update_status(f"显示边界框失败: {e}", "red")
            messagebox.showerror("错误", f"显示边界框失败: {e}")
    
    def _save_annotated_screenshot(self, screenshot, elements, title):
        """保存带标注的截图"""
        try:
            import cv2
            import numpy as np
            from tkinter import filedialog
            import os
            from datetime import datetime
            
            # 处理不同类型的screenshot输入
            if isinstance(screenshot, np.ndarray):
                # 如果已经是numpy数组，直接使用
                annotated_img = screenshot.copy()
            else:
                # 如果是PIL图像，转换为numpy数组
                try:
                    from PIL import Image
                    if isinstance(screenshot, Image.Image):
                        # PIL图像转换为numpy数组 (RGB -> BGR for OpenCV)
                        annotated_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                    else:
                        raise ValueError(f"Unsupported screenshot type: {type(screenshot)}")
                except ImportError:
                    raise ValueError(f"PIL not available, cannot convert {type(screenshot)} to numpy array")
            
            # 确保图像是正确的格式
            if len(annotated_img.shape) != 3:
                raise ValueError(f"Screenshot must be a 3D array (H,W,C), got shape {annotated_img.shape}")
            
            # 定义颜色映射
            color_map = {
                'button': (0, 255, 0),      # 绿色
                'link': (255, 0, 0),        # 蓝色
                'input': (0, 255, 255),     # 黄色
                'icon': (255, 0, 255),      # 紫色
                'text': (255, 255, 0)       # 青色
            }
            
            # 在截图上绘制边界框和标签
            for i, element in enumerate(elements):
                try:
                    bbox = element['bbox']
                    # 验证bbox格式
                    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
                        print(f"警告: 元素 {i} 的bbox格式无效: {bbox}")
                        continue
                    
                    # 确保坐标是整数类型并且有效
                    x, y, w, h = int(float(bbox[0])), int(float(bbox[1])), int(float(bbox[2])), int(float(bbox[3]))
                    
                    # 验证坐标范围
                    if x < 0 or y < 0 or w <= 0 or h <= 0:
                        print(f"警告: 元素 {i} 的坐标无效: x={x}, y={y}, w={w}, h={h}")
                        continue
                    
                    element_type = element['type']
                    confidence = element['confidence']
                    
                    # 获取颜色
                    color = color_map.get(element_type, (128, 128, 128))  # 默认灰色
                    
                    # 绘制边界框
                    cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 2)
                    
                    # 绘制标签
                    label = f"{element_type}({confidence:.2f})"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    
                    # 绘制标签背景
                    cv2.rectangle(annotated_img, 
                                (x, y - label_size[1] - 10), 
                                (x + label_size[0], y), 
                                color, -1)
                    
                    # 绘制标签文字
                    cv2.putText(annotated_img, label, 
                            (x, y - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                            (255, 255, 255), 2)
                    
                except Exception as e:
                    print(f"绘制元素 {i} 时出错: {e}")
                    print(f"元素数据: {element}")
                    continue
            
            # 选择保存路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"debug_{title.replace(' ', '_')}_{timestamp}.png"
            
            file_path = filedialog.asksaveasfilename(
                title="保存带标注的截图",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                # 保存图片
                cv2.imwrite(file_path, annotated_img)
                self._update_status(f"截图已保存到: {file_path}", "green")
                messagebox.showinfo("保存成功", f"带标注的截图已保存到:\n{file_path}")
            
        except Exception as e:
            self._update_status(f"保存截图失败: {e}", "red")
            messagebox.showerror("错误", f"保存截图失败: {e}")
    
    def _open_config(self):
        """打开配置界面"""
        try:
            if self.debug_config_gui is None:
                self.debug_config_gui = DebugConfigGUI(
                    parent=self.root,
                    on_config_changed=self._on_config_changed
                )
            
            self.debug_config_gui.show_config_window()
            self._update_status("配置界面已打开", "blue")
            
        except Exception as e:
            self._update_status(f"打开配置界面失败: {e}", "red")
            messagebox.showerror("错误", f"打开配置界面失败: {e}")
    
    def _on_config_changed(self):
        """配置改变时的回调"""
        self._update_status("配置已更新", "green")
        
        # 更新界面上的启用状态
        for element_type, var in self.enable_vars.items():
            enabled = getattr(detection_config, f"enable_{element_type}_detection")
            var.set(enabled)
    
    def _on_recognition_result(self, message):
        """识别结果回调"""
        self._update_status(message, "green")
    
    def _on_recognition_error(self, error_message):
        """识别错误回调"""
        self._update_status(f"错误: {error_message}", "red")
        self.root.update()
    
    def _show_bounding_boxes(self):
        """截图全屏并显示边界框"""
        try:
            import time
            total_operation_start = time.time()
            print(f"\n{'='*60}")
            print(f"开始完整的边界框显示流程")
            print(f"{'='*60}")
            
            self._update_status("正在截图识别...", "orange")
            
            # 禁用按钮防止重复点击
            self.show_boxes_btn.config(state="disabled")
            self.show_labels_btn.config(state="disabled")
            
            # 执行快速识别（强制启用详细计时）
            recognition_start = time.time()
            print("=== 主程序：开始截图识别流程 ===")
            success = self.fast_integrator.capture_and_recognize(save_screenshot=False)
            recognition_time = time.time() - recognition_start
            print(f"=== 主程序：识别阶段总耗时 {recognition_time:.3f} 秒 ===")
            
            if success:
                detections = self.fast_integrator.get_current_detections()
                self._update_status(f"发现 {len(detections)} 个元素", "blue")
                
                # 显示边界框
                if len(detections) > 0:
                    # 统计分析计时
                    stats_start = time.time()
                    stats = self.fast_integrator.get_statistics()
                    print(f"\n=== 元素类型统计 ===")
                    if 'type_counts' in stats:
                        for elem_type, count in stats['type_counts'].items():
                            percentage = (count / stats['total_elements']) * 100 if stats['total_elements'] > 0 else 0
                            print(f"{elem_type}: {count}个 ({percentage:.1f}%)")
                    stats_time = time.time() - stats_start
                    
                    # 边界框显示计时
                    bbox_display_start = time.time()
                    print("=== 主程序：开始边界框显示 ===")
                    box_success = self.fast_integrator.show_bounding_boxes(
                        duration=None,  # 永久显示
                        box_color='red',
                        box_width=2
                    )
                    bbox_display_time = time.time() - bbox_display_start
                    print(f"=== 主程序：边界框显示耗时 {bbox_display_time:.3f} 秒 ===")
                    
                    if box_success:
                        self._update_status(f"边界框已显示 ({len(detections)} 个元素)", "green")
                    else:
                        self._update_status("边界框显示失败", "red")
                else:
                    self._update_status("未检测到可点击元素", "orange")
                    stats_time = 0
                    bbox_display_time = 0
            else:
                self._update_status("识别失败", "red")
                stats_time = 0
                bbox_display_time = 0
            
            # 总体性能报告
            total_operation_time = time.time() - total_operation_start
            print(f"\n{'='*60}")
            print(f"完整流程性能报告")
            print(f"{'='*60}")
            print(f"总耗时: {total_operation_time:.3f} 秒")
            if success and len(detections) > 0:
                print(f"  - 截图+识别: {recognition_time:.3f} 秒 ({recognition_time/total_operation_time*100:.1f}%)")
                print(f"  - 统计分析: {stats_time:.3f} 秒 ({stats_time/total_operation_time*100:.1f}%)")
                print(f"  - 边界框显示: {bbox_display_time:.3f} 秒 ({bbox_display_time/total_operation_time*100:.1f}%)")
                print(f"处理效率: {len(detections)/total_operation_time:.1f} 个元素/秒")
                print(f"{'='*60}")
                
        except Exception as e:
            self._update_status(f"错误: {str(e)[:30]}...", "red")
            print(f"显示边界框失败: {e}")
        finally:
            # 重新启用按钮
            self.show_boxes_btn.config(state="normal")
            self.show_labels_btn.config(state="normal")
    
    def _show_labels(self):
        """截图全屏并显示标签"""
        try:
            self._update_status("正在截图识别...", "orange")
            
            # 禁用按钮防止重复点击
            self.show_boxes_btn.config(state="disabled")
            self.show_labels_btn.config(state="disabled")
            
            # 执行快速识别
            success = self.fast_integrator.capture_and_recognize()
            
            if success:
                detections = self.fast_integrator.get_current_detections()
                self._update_status(f"发现 {len(detections)} 个元素", "blue")
                
                # 显示标签
                if len(detections) > 0:
                    label_success = self.fast_integrator.show_labels(
                        max_labels=50,  # 最多显示50个标签
                        duration=None   # 永久显示
                    )
                    if label_success:
                        self._update_status(f"标签已显示 ({len(detections)} 个元素)", "green")
                    else:
                        self._update_status("标签显示失败", "red")
                else:
                    self._update_status("未检测到可点击元素", "orange")
            else:
                self._update_status("识别失败", "red")
                
        except Exception as e:
            self._update_status(f"错误: {str(e)[:30]}...", "red")
            print(f"显示标签失败: {e}")
        finally:
            # 重新启用按钮
            self.show_boxes_btn.config(state="normal")
            self.show_labels_btn.config(state="normal")
    
    def _hide_all(self):
        """隐藏所有显示"""
        try:
            self.fast_integrator.hide_all()
            self._update_status("所有显示已隐藏", "gray")
        except Exception as e:
            self._update_status("隐藏失败", "red")
            print(f"隐藏失败: {e}")
    
    def run(self):
        """运行应用"""
        try:
            print("快速识别工具启动")
            print("功能1: 截图并显示边界框")
            print("功能2: 截图并显示标签")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("程序被用户中断")
            self._cleanup_and_exit()
        except Exception as e:
            print(f"程序运行出错: {e}")
            self._cleanup_and_exit()
        finally:
            self._cleanup_and_exit()
            
    def _cleanup_and_exit(self):
        """清理资源并退出"""
        try:
            self.fast_integrator.hide_all()
        except:
            pass
        try:
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
        except:
            pass

def main():
    """主函数"""
    try:
        app = SimpleKeyboardClickerApp()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
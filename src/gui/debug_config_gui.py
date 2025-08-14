#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试配置GUI模块
提供可视化的检测参数配置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from ..utils.detection_config import detection_config

class DebugConfigGUI:
    """调试配置GUI界面类"""
    
    def __init__(self, parent=None, on_config_changed: Optional[Callable] = None):
        """初始化调试配置界面
        
        Args:
            parent: 父窗口
            on_config_changed: 配置改变时的回调函数
        """
        self.parent = parent
        self.on_config_changed = on_config_changed
        self.config = detection_config
        
        # 创建配置窗口
        self.window = None
        self.config_vars = {}  # 存储所有配置变量
        
    def show_config_window(self):
        """显示配置窗口"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("检测参数调试配置")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个配置页面
        self._create_debug_mode_tab(notebook)
        self._create_button_config_tab(notebook)
        self._create_link_config_tab(notebook)
        self._create_input_config_tab(notebook)
        self._create_icon_config_tab(notebook)
        self._create_text_config_tab(notebook)
        self._create_performance_tab(notebook)
        
        # 创建底部按钮
        self._create_bottom_buttons(main_frame)
        
    def _create_debug_mode_tab(self, notebook):
        """创建调试模式标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="调试模式")
        
        # 调试模式选择
        debug_frame = ttk.LabelFrame(frame, text="调试模式选择")
        debug_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 调试模式变量
        self.debug_mode_var = tk.StringVar(value="normal")
        
        # 正常模式
        ttk.Radiobutton(
            debug_frame, 
            text="正常模式（检测所有启用的元素类型）", 
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
                debug_frame, 
                text=text, 
                variable=self.debug_mode_var, 
                value=value,
                command=self._on_debug_mode_changed
            ).pack(anchor=tk.W, padx=10, pady=2)
        
        # 检测类型启用开关（正常模式下使用）
        enable_frame = ttk.LabelFrame(frame, text="检测类型启用开关（正常模式）")
        enable_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.enable_vars = {}
        enable_options = [
            ("button", "启用按钮检测", self.config.enable_button_detection),
            ("link", "启用链接检测", self.config.enable_link_detection),
            ("input", "启用输入框检测", self.config.enable_input_detection),
            ("icon", "启用图标检测", self.config.enable_icon_detection),
            ("text", "启用文字检测", self.config.enable_text_detection)
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
    
    def _create_element_config_tab(self, notebook, element_type: str, display_name: str):
        """创建元素配置标签页的通用方法"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=display_name)
        
        # 获取当前参数
        params = self.config.get_element_params(element_type)
        
        # 面积参数
        area_frame = ttk.LabelFrame(frame, text="面积参数（像素²）")
        area_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 最小面积
        min_area_frame = ttk.Frame(area_frame)
        min_area_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(min_area_frame, text="最小面积:").pack(side=tk.LEFT)
        min_area_var = tk.IntVar(value=params['min_area'])
        self.config_vars[f"{element_type}_min_area"] = min_area_var
        ttk.Entry(min_area_frame, textvariable=min_area_var, width=10).pack(side=tk.RIGHT)
        
        # 最大面积
        max_area_frame = ttk.Frame(area_frame)
        max_area_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(max_area_frame, text="最大面积:").pack(side=tk.LEFT)
        max_area_var = tk.IntVar(value=params['max_area'])
        self.config_vars[f"{element_type}_max_area"] = max_area_var
        ttk.Entry(max_area_frame, textvariable=max_area_var, width=10).pack(side=tk.RIGHT)
        
        # 长宽比参数
        ratio_frame = ttk.LabelFrame(frame, text="长宽比范围")
        ratio_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 最小长宽比
        min_ratio_frame = ttk.Frame(ratio_frame)
        min_ratio_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(min_ratio_frame, text="最小长宽比:").pack(side=tk.LEFT)
        min_ratio_var = tk.DoubleVar(value=params['aspect_ratio_range'][0])
        self.config_vars[f"{element_type}_min_ratio"] = min_ratio_var
        ttk.Entry(min_ratio_frame, textvariable=min_ratio_var, width=10).pack(side=tk.RIGHT)
        
        # 最大长宽比
        max_ratio_frame = ttk.Frame(ratio_frame)
        max_ratio_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(max_ratio_frame, text="最大长宽比:").pack(side=tk.LEFT)
        max_ratio_var = tk.DoubleVar(value=params['aspect_ratio_range'][1])
        self.config_vars[f"{element_type}_max_ratio"] = max_ratio_var
        ttk.Entry(max_ratio_frame, textvariable=max_ratio_var, width=10).pack(side=tk.RIGHT)
        
        # 置信度参数
        conf_frame = ttk.LabelFrame(frame, text="置信度参数")
        conf_frame.pack(fill=tk.X, padx=5, pady=5)
        
        conf_param_frame = ttk.Frame(conf_frame)
        conf_param_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(conf_param_frame, text="置信度阈值 (0-1):").pack(side=tk.LEFT)
        conf_var = tk.DoubleVar(value=params['confidence_threshold'])
        self.config_vars[f"{element_type}_confidence"] = conf_var
        ttk.Entry(conf_param_frame, textvariable=conf_var, width=10).pack(side=tk.RIGHT)
        
        # 添加说明文本
        info_frame = ttk.LabelFrame(frame, text="参数说明")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_text = self._get_element_info_text(element_type)
        text_widget = tk.Text(info_frame, height=8, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
    
    def _create_button_config_tab(self, notebook):
        """创建按钮配置标签页"""
        self._create_element_config_tab(notebook, "button", "按钮配置")
    
    def _create_link_config_tab(self, notebook):
        """创建链接配置标签页"""
        self._create_element_config_tab(notebook, "link", "链接配置")
    
    def _create_input_config_tab(self, notebook):
        """创建输入框配置标签页"""
        self._create_element_config_tab(notebook, "input", "输入框配置")
    
    def _create_icon_config_tab(self, notebook):
        """创建图标配置标签页"""
        self._create_element_config_tab(notebook, "icon", "图标配置")
    
    def _create_text_config_tab(self, notebook):
        """创建文字配置标签页"""
        self._create_element_config_tab(notebook, "text", "文字配置")
    
    def _create_performance_tab(self, notebook):
        """创建性能配置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="性能配置")
        
        # 并行处理参数
        parallel_frame = ttk.LabelFrame(frame, text="并行处理")
        parallel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 最大工作线程数
        workers_frame = ttk.Frame(parallel_frame)
        workers_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(workers_frame, text="最大工作线程数:").pack(side=tk.LEFT)
        workers_var = tk.IntVar(value=self.config.max_workers)
        self.config_vars["max_workers"] = workers_var
        ttk.Entry(workers_frame, textvariable=workers_var, width=10).pack(side=tk.RIGHT)
        
        # 优化选项
        opt_frame = ttk.LabelFrame(frame, text="优化选项")
        opt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ROI优化
        roi_var = tk.BooleanVar(value=self.config.roi_optimization)
        self.config_vars["roi_optimization"] = roi_var
        ttk.Checkbutton(opt_frame, text="启用ROI优化", variable=roi_var).pack(anchor=tk.W, padx=10, pady=2)
        
        # 缓存启用
        cache_var = tk.BooleanVar(value=self.config.cache_enabled)
        self.config_vars["cache_enabled"] = cache_var
        ttk.Checkbutton(opt_frame, text="启用结果缓存", variable=cache_var).pack(anchor=tk.W, padx=10, pady=2)
        
        # 重复区域合并
        merge_frame = ttk.LabelFrame(frame, text="重复区域合并")
        merge_frame.pack(fill=tk.X, padx=5, pady=5)
        
        iou_frame = ttk.Frame(merge_frame)
        iou_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(iou_frame, text="IoU阈值 (0-1):").pack(side=tk.LEFT)
        iou_var = tk.DoubleVar(value=self.config.duplicate_iou_threshold)
        self.config_vars["duplicate_iou_threshold"] = iou_var
        ttk.Entry(iou_frame, textvariable=iou_var, width=10).pack(side=tk.RIGHT)
    
    def _create_bottom_buttons(self, parent):
        """创建底部按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 应用配置按钮
        ttk.Button(
            button_frame, 
            text="应用配置", 
            command=self._apply_config
        ).pack(side=tk.LEFT, padx=5)
        
        # 重置为默认值按钮
        ttk.Button(
            button_frame, 
            text="重置默认值", 
            command=self._reset_to_defaults
        ).pack(side=tk.LEFT, padx=5)
        
        # 关闭按钮
        ttk.Button(
            button_frame, 
            text="关闭", 
            command=self._close_window
        ).pack(side=tk.RIGHT, padx=5)
    
    def _get_element_info_text(self, element_type: str) -> str:
        """获取元素类型的说明文本"""
        info_texts = {
            "button": "按钮检测参数说明：\n" +
                     "• 最小面积：过小的区域不被认为是按钮，建议值100-500\n" +
                     "• 最大面积：过大的区域不被认为是按钮，建议值20000-100000\n" +
                     "• 长宽比：按钮的宽高比范围，建议值(0.2, 8.0)\n" +
                     "• 置信度：检测严格程度，值越高越严格，建议值0.3-0.5",
            
            "link": "链接检测参数说明：\n" +
                   "• 最小面积：避免检测到单个字符，建议值50-200\n" +
                   "• 最大面积：避免检测到大段文本，建议值5000-20000\n" +
                   "• 长宽比：链接通常是横向文本，建议值(1.0, 20.0)\n" +
                   "• 置信度：链接检测相对困难，可以稍低，建议值0.25-0.4",
            
            "input": "输入框检测参数说明：\n" +
                    "• 最小面积：输入框需要足够大以容纳文本，建议值200-800\n" +
                    "• 最大面积：避免检测到大的文本区域，建议值50000-200000\n" +
                    "• 长宽比：输入框通常是横向矩形，建议值(1.5, 20.0)\n" +
                    "• 置信度：输入框特征相对明显，建议值0.3-0.5",
            
            "icon": "图标检测参数说明：\n" +
                   "• 最小面积：图标通常较小，建议值100-300\n" +
                   "• 最大面积：避免检测到大图像，建议值3000-10000\n" +
                   "• 长宽比：图标通常接近正方形，建议值(0.5, 2.5)\n" +
                   "• 置信度：图标特征明显，可以设置较高，建议值0.35-0.5",
            
            "text": "文字检测参数说明：\n" +
                   "• 最小面积：单个字符或很短文本，建议值30-100\n" +
                   "• 最大面积：避免检测到整个页面文本，建议值10000-50000\n" +
                   "• 长宽比：文字可以是单行或多行，建议值(0.5, 30.0)\n" +
                   "• 置信度：文字检测相对容易，建议值0.2-0.35"
        }
        
        return info_texts.get(element_type, "暂无说明")
    
    def _on_debug_mode_changed(self):
        """调试模式改变时的回调"""
        mode = self.debug_mode_var.get()
        if mode == "normal":
            self.config.set_debug_mode(None)
        else:
            self.config.set_debug_mode(mode)
        
        if self.on_config_changed:
            self.on_config_changed()
    
    def _on_enable_changed(self, element_type: str):
        """检测类型启用状态改变时的回调"""
        enabled = self.enable_vars[element_type].get()
        self.config.toggle_detection_type(element_type, enabled)
        
        if self.on_config_changed:
            self.on_config_changed()
    
    def _apply_config(self):
        """应用配置"""
        try:
            # 更新所有元素类型的参数
            element_types = ["button", "link", "input", "icon", "text"]
            
            for element_type in element_types:
                # 获取参数
                min_area = self.config_vars[f"{element_type}_min_area"].get()
                max_area = self.config_vars[f"{element_type}_max_area"].get()
                min_ratio = self.config_vars[f"{element_type}_min_ratio"].get()
                max_ratio = self.config_vars[f"{element_type}_max_ratio"].get()
                confidence = self.config_vars[f"{element_type}_confidence"].get()
                
                # 验证参数
                if min_area >= max_area:
                    raise ValueError(f"{element_type}: 最小面积必须小于最大面积")
                if min_ratio >= max_ratio:
                    raise ValueError(f"{element_type}: 最小长宽比必须小于最大长宽比")
                if not 0 <= confidence <= 1:
                    raise ValueError(f"{element_type}: 置信度必须在0-1之间")
                
                # 更新配置
                self.config.update_element_params(
                    element_type,
                    min_area=min_area,
                    max_area=max_area,
                    aspect_ratio_range=(min_ratio, max_ratio),
                    confidence_threshold=confidence
                )
            
            # 更新性能参数
            self.config.max_workers = self.config_vars["max_workers"].get()
            self.config.roi_optimization = self.config_vars["roi_optimization"].get()
            self.config.cache_enabled = self.config_vars["cache_enabled"].get()
            self.config.duplicate_iou_threshold = self.config_vars["duplicate_iou_threshold"].get()
            
            messagebox.showinfo("成功", "配置已应用")
            
            if self.on_config_changed:
                self.on_config_changed()
                
        except ValueError as e:
            messagebox.showerror("参数错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"应用配置时发生错误: {e}")
    
    def _reset_to_defaults(self):
        """重置为默认值"""
        if messagebox.askyesno("确认", "确定要重置所有参数为默认值吗？"):
            # 重新创建配置对象以获取默认值
            from ..utils.detection_config import DetectionConfig
            default_config = DetectionConfig()
            
            # 复制默认值到当前配置
            for attr in dir(default_config):
                if not attr.startswith('_') and hasattr(self.config, attr):
                    setattr(self.config, attr, getattr(default_config, attr))
            
            # 关闭当前窗口并重新打开以刷新界面
            self._close_window()
            self.show_config_window()
            
            messagebox.showinfo("成功", "已重置为默认配置")
    
    def _close_window(self):
        """关闭窗口"""
        if self.window:
            self.window.destroy()
            self.window = None
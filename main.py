#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速视觉识别工具
核心功能：截图识别 + 显示边界框/标签
"""

import tkinter as tk
from tkinter import messagebox
from src.utils.fast_label_integrator import FastLabelIntegrator

class KeyboardClickerApp:
    """快速视觉识别应用"""
    
    def __init__(self):
        # 初始化快速识别集成器
        self._fast_integrator = FastLabelIntegrator()
        
        # 创建GUI
        self._create_gui()
        
    def _create_gui(self):
        """创建简化的用户界面"""
        self.root = tk.Tk()
        self.root.title("快速视觉识别工具")
        self.root.geometry("350x400")
        self.root.resizable(False, False)
        
        #region 标题区域
        title_frame = tk.Frame(self.root, bg="white")
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="快速视觉识别工具", 
            font=("Microsoft YaHei", 16, "bold"),
            fg="#2E86AB",
            bg="white"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="截图并快速识别屏幕上的可点击元素",
            font=("Microsoft YaHei", 9),
            fg="#666666",
            bg="white"
        )
        subtitle_label.pack(pady=(5, 0))
        #endregion
        
        #region 主要功能按钮
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.X, padx=30, pady=20)
        
        # 显示边界框按钮
        self._show_boxes_btn = tk.Button(
            main_frame,
            text="📦 显示边界框",
            command=self._ShowBoundingBoxes,
            bg="#A8DADC",
            font=("Microsoft YaHei", 12, "bold"),
            width=20,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self._show_boxes_btn.pack(pady=8)
        
        # 显示标签按钮
        self._show_labels_btn = tk.Button(
            main_frame,
            text="🏷️ 显示标签",
            command=self._ShowLabels,
            bg="#F1FAEE",
            font=("Microsoft YaHei", 12, "bold"),
            width=20,
            height=2,
            relief="flat",
            cursor="hand2"
        )
        self._show_labels_btn.pack(pady=8)
        
        # 隐藏所有按钮
        hide_btn = tk.Button(
            main_frame,
            text="❌ 隐藏所有显示",
            command=self._HideAll,
            bg="#E63946",
            fg="white",
            font=("Microsoft YaHei", 10),
            width=20,
            height=1,
            relief="flat",
            cursor="hand2"
        )
        hide_btn.pack(pady=8)
        
        # 临时调试按钮 - 显示检测配置状态
        debug_btn = tk.Button(
            main_frame,
            text="🔧 检查配置状态",
            command=self._CheckConfigStatus,
            bg="#6C757D",
            fg="white",
            font=("Microsoft YaHei", 9),
            width=20,
            height=1,
            relief="flat",
            cursor="hand2"
        )
        debug_btn.pack(pady=4)
        #endregion
        
        #region 状态区域
        status_frame = tk.Frame(self.root, bg="#F8F9FA")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self._status_label = tk.Label(
            status_frame,
            text="就绪",
            font=("Microsoft YaHei", 9),
            fg="#28A745",
            bg="#F8F9FA",
            pady=10
        )
        self._status_label.pack()
        #endregion
    
    def _UpdateStatus(self, text, color="#28A745"):
        """更新状态显示"""
        color_map = {
            "green": "#28A745",
            "red": "#DC3545", 
            "orange": "#FD7E14",
            "blue": "#007BFF",
            "gray": "#6C757D"
        }
        final_color = color_map.get(color, color)
        self._status_label.config(text=text, fg=final_color)
    
    def _ShowBoundingBoxes(self):
        """截图全屏并显示边界框"""
        try:
            self._UpdateStatus("正在截图识别...", "orange")
            
            # 禁用按钮防止重复点击
            self._show_boxes_btn.config(state="disabled")
            self._show_labels_btn.config(state="disabled")
            
            # 执行快速识别
            success = self._fast_integrator.capture_and_recognize(save_screenshot=False)
            
            if success:
                detections = self._fast_integrator.get_current_detections()
                self._UpdateStatus(f"发现 {len(detections)} 个元素", "blue")
                
                # 显示边界框
                if len(detections) > 0:
                    box_success = self._fast_integrator.show_bounding_boxes(
                        duration=None,  # 永久显示
                        box_color='red',
                        box_width=2
                    )
                    if box_success:
                        self._UpdateStatus(f"边界框已显示 ({len(detections)} 个元素)", "green")
                    else:
                        self._UpdateStatus("边界框显示失败", "red")
                else:
                    self._UpdateStatus("未检测到可点击元素", "orange")
            else:
                self._UpdateStatus("识别失败", "red")
                
        except Exception as e:
            self._UpdateStatus(f"错误: {str(e)[:20]}...", "red")
        finally:
            # 重新启用按钮
            self._show_boxes_btn.config(state="normal")
            self._show_labels_btn.config(state="normal")
    
    def _ShowLabels(self):
        """截图全屏并显示标签"""
        try:
            self._UpdateStatus("正在截图识别...", "orange")
            
            # 禁用按钮防止重复点击
            self._show_boxes_btn.config(state="disabled")
            self._show_labels_btn.config(state="disabled")
            
            # 执行快速识别
            success = self._fast_integrator.capture_and_recognize()
            
            if success:
                detections = self._fast_integrator.get_current_detections()
                self._UpdateStatus(f"发现 {len(detections)} 个元素", "blue")
                
                # 显示标签
                if len(detections) > 0:
                    label_success = self._fast_integrator.show_labels(
                        max_labels=50,  # 最多显示50个标签
                        duration=None   # 永久显示
                    )
                    if label_success:
                        self._UpdateStatus(f"标签已显示 ({len(detections)} 个元素)", "green")
                    else:
                        self._UpdateStatus("标签显示失败", "red")
                else:
                    self._UpdateStatus("未检测到可点击元素", "orange")
            else:
                self._UpdateStatus("识别失败", "red")
                
        except Exception as e:
            self._UpdateStatus(f"错误: {str(e)[:20]}...", "red")
        finally:
            # 重新启用按钮
            self._show_boxes_btn.config(state="normal")
            self._show_labels_btn.config(state="normal")
    
    def _HideAll(self):
        """隐藏所有显示"""
        try:
            self._fast_integrator.hide_all()
            self._UpdateStatus("所有显示已隐藏", "gray")
        except Exception as e:
            self._UpdateStatus("隐藏失败", "red")
    
    def _CheckConfigStatus(self):
        """检查当前检测配置状态"""
        try:
            from src.utils.detection_config import detection_config
            
            # 创建状态窗口
            status_window = tk.Toplevel(self.root)
            status_window.title("检测配置状态")
            status_window.geometry("500x400")
            status_window.resizable(False, False)
            
            # 创建文本显示区域
            text_frame = tk.Frame(status_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 获取配置状态信息
            status_text = "=== 检测配置状态 ===\n\n"
            
            # 获取启用的检测类型
            enabled_types = detection_config.get_enabled_detection_types()
            status_text += f"启用的检测类型 ({len(enabled_types)} 个):\n"
            if enabled_types:
                for i, detection_type in enumerate(enabled_types, 1):
                    params = detection_config.get_element_params(detection_type)
                    status_text += f"  {i}. {detection_type}\n"
                    status_text += f"     - 面积范围: {params['min_area']}-{params['max_area']}\n"
                    status_text += f"     - 长宽比: {params['aspect_ratio_range']}\n"
                    status_text += f"     - 置信度阈值: {params['confidence_threshold']}\n\n"
            else:
                status_text += "  ❌ 未启用任何检测类型！\n\n"
            
            # 性能配置
            status_text += "=== 性能配置 ===\n"
            status_text += f"并行处理: {'开启' if detection_config.max_workers > 1 else '关闭'} (工作线程: {detection_config.max_workers})\n"
            status_text += f"ROI优化: {'开启' if detection_config.roi_optimization else '关闭'}\n"
            status_text += f"缓存: {'开启' if detection_config.cache_enabled else '关闭'}\n"
            status_text += f"重复区域合并阈值: {detection_config.duplicate_iou_threshold}\n\n"
            
            text_widget.insert(tk.END, status_text)
            text_widget.config(state=tk.DISABLED)
            
            # 添加关闭按钮
            close_btn = tk.Button(
                status_window,
                text="关闭",
                command=status_window.destroy,
                bg="#6C757D",
                fg="white",
                font=("Microsoft YaHei", 10),
                width=10
            )
            close_btn.pack(pady=10)
            
            self._UpdateStatus("配置状态已显示", "blue")
            
        except Exception as e:
            self._UpdateStatus(f"检查配置失败: {str(e)[:20]}...", "red")
            messagebox.showerror("错误", f"检查配置状态失败: {e}")
    
    def Run(self):
        """运行应用"""
        try:
            print("快速视觉识别工具启动")
            print("功能: 截图并显示边界框/标签")
            self.root.protocol("WM_DELETE_WINDOW", self._OnClose)
            self.root.mainloop()
        except Exception as e:
            print(f"程序运行出错: {e}")
            self._CleanupAndExit()
            
    def _OnClose(self):
        """窗口关闭时的处理"""
        self._CleanupAndExit()
        
    def _CleanupAndExit(self):
        """清理资源并退出"""
        try:
            self._fast_integrator.hide_all()
        except:
            pass
        try:
            if hasattr(self, 'root'):
                self.root.quit()
                self.root.destroy()
        except:
            pass

def main():
    """主函数"""
    try:
        app = KeyboardClickerApp()
        app.Run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()
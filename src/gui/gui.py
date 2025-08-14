#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI界面模块
提供用户界面相关功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

class ClickerGUI:
    """点击工具GUI界面类"""
    
    def __init__(self, title: str = "键盘点击屏幕工具", size: str = "320x250"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(size)
        self.root.resizable(False, False)
        
        # 界面变量
        self.target_x = tk.StringVar(value="0")
        self.target_y = tk.StringVar(value="0")
        self.current_pos = tk.StringVar(value="当前位置: (0, 0)")
        self.status = tk.StringVar(value="状态: 待机")
        self.screen_info = tk.StringVar(value="屏幕信息: 检测中...")
        
        # 回调函数
        self.on_get_position: Optional[Callable] = None
        self.on_start_listening: Optional[Callable] = None
        self.on_stop_listening: Optional[Callable] = None
        self.on_position_update: Optional[Callable] = None
        self.on_refresh_screen: Optional[Callable] = None
        
        # UI控件引用
        self.start_btn = None
        self.stop_btn = None
        
        self._setup_ui()
        self._start_position_update()
        
    def _setup_ui(self):
        """创建用户界面"""
        # 当前鼠标位置显示
        tk.Label(self.root, textvariable=self.current_pos, font=("Arial", 10)).pack(pady=5)
        
        # 屏幕信息显示
        screen_frame = tk.Frame(self.root)
        screen_frame.pack(pady=2)
        tk.Label(screen_frame, textvariable=self.screen_info, font=("Arial", 8), fg="blue").pack(side=tk.LEFT)
        tk.Button(screen_frame, text="刷新", command=self._handle_refresh_screen, font=("Arial", 8)).pack(side=tk.RIGHT, padx=5)
        
        # 目标坐标设置
        coord_frame = tk.Frame(self.root)
        coord_frame.pack(pady=10)
        
        tk.Label(coord_frame, text="目标坐标:").grid(row=0, column=0, columnspan=2, pady=5)
        
        tk.Label(coord_frame, text="X:").grid(row=1, column=0, padx=5)
        tk.Entry(coord_frame, textvariable=self.target_x, width=8).grid(row=1, column=1, padx=5)
        
        tk.Label(coord_frame, text="Y:").grid(row=2, column=0, padx=5)
        tk.Entry(coord_frame, textvariable=self.target_y, width=8).grid(row=2, column=1, padx=5)
        
        # 获取当前位置按钮
        tk.Button(self.root, text="获取当前位置", command=self._handle_get_position).pack(pady=5)
        
        # 控制按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        self.start_btn = tk.Button(
            button_frame, 
            text="开始监听", 
            command=self._handle_start_listening, 
            bg="green", 
            fg="white"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame, 
            text="停止监听", 
            command=self._handle_stop_listening, 
            bg="red", 
            fg="white", 
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态显示
        tk.Label(self.root, textvariable=self.status, font=("Arial", 9)).pack(pady=5)
        
        # 使用说明
        help_frame = tk.Frame(self.root)
        help_frame.pack(pady=2)
        tk.Label(help_frame, text="按F1键触发点击", font=("Arial", 8), fg="gray").pack()
        tk.Label(help_frame, text="支持多屏幕环境", font=("Arial", 7), fg="green").pack()
        
    def _start_position_update(self):
        """开始位置更新循环"""
        self._update_position()
        
    def _update_position(self):
        """更新鼠标位置显示"""
        if self.on_position_update:
            try:
                x, y = self.on_position_update()
                self.current_pos.set(f"当前位置: ({x}, {y})")
            except:
                pass
        # 每100ms更新一次
        self.root.after(100, self._update_position)
        
    def _handle_get_position(self):
        """处理获取当前位置按钮点击"""
        if self.on_get_position:
            try:
                x, y = self.on_get_position()
                self.set_target_coordinates(x, y)
                messagebox.showinfo("成功", f"已设置目标坐标为: ({x}, {y})")
            except Exception as e:
                messagebox.showerror("错误", str(e))
                
    def _handle_start_listening(self):
        """处理开始监听按钮点击"""
        if self.on_start_listening:
            try:
                x, y = self.get_target_coordinates()
                success = self.on_start_listening(x, y)
                if success:
                    self.set_listening_state(True)
            except Exception as e:
                messagebox.showerror("错误", str(e))
                
    def _handle_stop_listening(self):
        """处理停止监听按钮点击"""
        if self.on_stop_listening:
            self.on_stop_listening()
            self.set_listening_state(False)
            
    def _handle_refresh_screen(self):
        """处理刷新屏幕信息按钮点击"""
        if self.on_refresh_screen:
            try:
                self.on_refresh_screen()
            except Exception as e:
                messagebox.showerror("错误", f"刷新屏幕信息失败: {e}")
            
    def get_target_coordinates(self) -> tuple[int, int]:
        """获取目标坐标"""
        try:
            x = int(self.target_x.get())
            y = int(self.target_y.get())
            return x, y
        except ValueError:
            raise ValueError("请输入有效的数字坐标")
            
    def set_target_coordinates(self, x: int, y: int):
        """设置目标坐标"""
        self.target_x.set(str(x))
        self.target_y.set(str(y))
        
    def update_status(self, status: str):
        """更新状态显示"""
        self.status.set(f"状态: {status}")
        
    def set_listening_state(self, is_listening: bool):
        """设置监听状态"""
        if is_listening:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
    def show_error(self, title: str, message: str):
        """显示错误消息"""
        messagebox.showerror(title, message)
        
    def show_info(self, title: str, message: str):
        """显示信息消息"""
        messagebox.showinfo(title, message)
        
    def set_get_position_callback(self, callback: Callable[[], tuple[int, int]]):
        """设置获取位置回调"""
        self.on_get_position = callback
        
    def set_start_listening_callback(self, callback: Callable[[int, int], bool]):
        """设置开始监听回调"""
        self.on_start_listening = callback
        
    def set_stop_listening_callback(self, callback: Callable[[], None]):
        """设置停止监听回调"""
        self.on_stop_listening = callback
        
    def set_position_update_callback(self, callback: Callable[[], tuple[int, int]]):
        """设置位置更新回调"""
        self.on_position_update = callback
        
    def set_refresh_screen_callback(self, callback: Callable[[], None]):
        """设置刷新屏幕信息回调"""
        self.on_refresh_screen = callback
        
    def update_screen_info(self, info: str):
        """更新屏幕信息显示"""
        self.screen_info.set(f"屏幕: {info}")
        
    def run(self):
        """运行GUI主循环"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
            
    def destroy(self):
        """销毁窗口"""
        self.root.destroy()
        
    def after(self, delay: int, callback: Callable):
        """延迟执行回调"""
        self.root.after(delay, callback)
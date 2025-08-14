#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕标签显示工具
用于在识别出的文字和按钮上方显示标签
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import List, Dict, Tuple, Callable, Optional


class ScreenLabeler:
    """屏幕标签显示器类"""
    
    def __init__(self):
        self._root = None
        self._labels = []  # 存储所有标签窗口
        self._current_labels = []  # 当前显示的标签序列
        self._display_thread = None
        self._is_displaying = False
        self._callback = None
        self._error_callback = None
        
    #region 回调设置
    def SetCallback(self, callback: Callable[[str], None]):
        """设置成功回调函数"""
        self._callback = callback
        
    def SetErrorCallback(self, error_callback: Callable[[str], None]):
        """设置错误回调函数"""
        self._error_callback = error_callback
    #endregion
        
    #region 标签生成算法
    def _GenerateLabel(self, index: int) -> str:
        """
        生成标签序列 A,B,C...Z,AA,AB,AC...AZ,BA,BB...
        :param index: 索引位置 (从0开始)
        :return: 生成的标签字符串
        """
        if index < 0:
            return "A"
            
        # 26进制转换
        result = ""
        index += 1  # 转换为1-based索引
        
        while index > 0:
            index -= 1  # 转换回0-based用于计算
            result = chr(ord('A') + (index % 26)) + result
            index //= 26
            
        return result
        
    def _GenerateLabelList(self, count: int) -> List[str]:
        """
        生成指定数量的标签列表
        :param count: 需要生成的标签数量
        :return: 标签列表
        """
        return [self._GenerateLabel(i) for i in range(count)]
    #endregion
    
    #region 标签窗口创建
    def _CreateLabelWindow(self, text: str, x: int, y: int) -> tk.Toplevel:
        """
        创建单个标签窗口
        :param text: 标签文字
        :param x: X坐标
        :param y: Y坐标 
        :return: 创建的窗口对象
        """
        # 创建顶层窗口
        label_window = tk.Toplevel(self._root)
        
        # 设置窗口属性
        label_window.overrideredirect(True)  # 无边框窗口
        label_window.attributes('-topmost', True)  # 置顶显示
        label_window.attributes('-alpha', 0.8)  # 半透明
        
        # 设置窗口背景色
        label_window.configure(bg='red')
        
        # 创建标签
        label = tk.Label(
            label_window,
            text=text,
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='red',
            padx=5,
            pady=2
        )
        label.pack()
        
        # 计算窗口位置 (标签显示在目标位置上方)
        label_window.update_idletasks()  # 更新窗口大小
        label_width = label_window.winfo_reqwidth()
        label_height = label_window.winfo_reqheight()
        
        # 标签位置在目标上方中央
        label_x = max(0, x - label_width // 2)
        label_y = max(0, y - label_height - 5)  # 上方5像素距离
        
        label_window.geometry(f"+{label_x}+{label_y}")
        
        return label_window
    #endregion
    
    #region 标签显示控制
    def ShowLabels(self, elements: List[Dict], duration: Optional[float] = None) -> bool:
        """
        显示标签
        :param elements: 元素列表，每个元素包含center_x, center_y等信息
        :param duration: 显示持续时间(秒)，None表示持续显示直到手动关闭
        :return: 是否成功显示
        """
        try:
            if self._is_displaying:
                self._CallErrorCallback("标签正在显示中，请先关闭当前标签")
                return False
                
            if not elements:
                self._CallErrorCallback("没有元素需要显示标签")
                return False
                
            # 在新线程中显示标签
            self._display_thread = threading.Thread(
                target=self._DisplayLabelsThread,
                args=(elements, duration),
                daemon=True
            )
            self._display_thread.start()
            
            return True
            
        except Exception as e:
            self._CallErrorCallback(f"显示标签失败: {e}")
            return False
    
    def _DisplayLabelsThread(self, elements: List[Dict], duration: Optional[float]):
        """标签显示线程"""
        try:
            self._is_displaying = True
            
            # 创建主窗口
            self._root = tk.Tk()
            self._root.withdraw()  # 隐藏主窗口
            
            # 生成标签序列
            self._current_labels = self._GenerateLabelList(len(elements))
            
            # 创建所有标签窗口
            self._labels = []
            for i, element in enumerate(elements):
                label_text = self._current_labels[i]
                x = element.get('center_x', 0)
                y = element.get('center_y', 0)
                
                label_window = self._CreateLabelWindow(label_text, x, y)
                self._labels.append(label_window)
            
            self._CallCallback(f"已显示 {len(self._labels)} 个标签")
            
            # 如果设置了持续时间，定时关闭
            if duration and duration > 0:
                self._root.after(int(duration * 1000), self.HideLabels)
            
            # 启动GUI主循环
            self._root.mainloop()
            
        except Exception as e:
            self._CallErrorCallback(f"显示标签线程错误: {e}")
        finally:
            self._is_displaying = False
    
    def HideLabels(self):
        """隐藏所有标签"""
        try:
            if self._root:
                # 销毁所有标签窗口
                for label_window in self._labels:
                    try:
                        label_window.destroy()
                    except:
                        pass
                
                # 关闭主窗口
                self._root.destroy()
                self._root = None
                
                self._labels.clear()
                self._current_labels.clear()
                
                self._CallCallback("已隐藏所有标签")
                
        except Exception as e:
            self._CallErrorCallback(f"隐藏标签失败: {e}")
    
    def IsDisplaying(self) -> bool:
        """检查是否正在显示标签"""
        return self._is_displaying
    #endregion
    
    #region 标签信息获取
    def GetDisplayedLabels(self) -> List[str]:
        """获取当前显示的标签列表"""
        return self._current_labels.copy()
    
    def GetLabelCount(self) -> int:
        """获取当前显示的标签数量"""
        return len(self._current_labels)
    
    def GetLabelByIndex(self, index: int) -> Optional[str]:
        """
        根据索引获取标签
        :param index: 索引位置
        :return: 标签字符串，如果索引无效则返回None
        """
        if 0 <= index < len(self._current_labels):
            return self._current_labels[index]
        return None
    #endregion
    
    #region 测试功能
    def TestLabelGeneration(self, count: int = 100) -> List[str]:
        """
        测试标签生成功能
        :param count: 测试生成的标签数量
        :return: 生成的标签列表
        """
        try:
            labels = self._GenerateLabelList(count)
            self._CallCallback(f"成功生成 {count} 个测试标签")
            return labels
        except Exception as e:
            self._CallErrorCallback(f"测试标签生成失败: {e}")
            return []
    
    def ShowTestLabels(self, count: int = 10, duration: float = 5.0):
        """
        显示测试标签
        :param count: 测试标签数量
        :param duration: 显示持续时间
        """
        # 创建测试元素
        test_elements = []
        for i in range(count):
            test_elements.append({
                'center_x': 100 + (i % 5) * 150,  # 5列布局
                'center_y': 100 + (i // 5) * 50,  # 每行50像素间距
                'text': f'测试元素{i+1}',
                'type': 'test'
            })
        
        self.ShowLabels(test_elements, duration)
    #endregion
    
    #region 回调处理
    def _CallCallback(self, message: str):
        """调用成功回调"""
        if self._callback:
            try:
                self._callback(message)
            except:
                pass
                
    def _CallErrorCallback(self, message: str):
        """调用错误回调"""
        if self._error_callback:
            try:
                self._error_callback(message)
            except:
                pass
    #endregion
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
点击功能模块
提供坐标点击和键盘监听功能
"""

import pyautogui
import keyboard
import threading
import time
from typing import Callable, Optional
try:
    import tkinter as tk
except ImportError:
    tk = None

class ClickerTool:
    """坐标点击工具类"""
    
    def __init__(self):
        self.is_listening = False
        self.target_x = 0
        self.target_y = 0
        self.on_click_callback: Optional[Callable] = None
        self.on_status_change: Optional[Callable] = None
        
        # 设置pyautogui安全模式
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # 多屏幕支持
        self.screen_info = self._get_screen_info()
        self.total_width = self.screen_info['total_width']
        self.total_height = self.screen_info['total_height']
        self.screen_bounds = self.screen_info['bounds']
        
    def set_target_position(self, x: int, y: int):
        """设置目标点击坐标"""
        self.target_x = x
        self.target_y = y
        
    def get_current_mouse_position(self):
        """获取当前鼠标位置（支持多屏幕）"""
        try:
            pos = pyautogui.position()
            # 确保坐标在有效范围内
            x, y = pos.x, pos.y
            
            # 如果坐标超出范围，尝试修正
            min_x, min_y, max_x, max_y = self.screen_bounds
            if x < min_x or x >= max_x or y < min_y or y >= max_y:
                # 坐标可能在扩展屏幕上，保持原值但记录警告
                if self.on_status_change:
                    self.on_status_change(f"检测到扩展屏幕坐标: ({x}, {y})")
            
            return x, y
        except Exception as e:
            raise Exception(f"获取鼠标位置失败: {e}")
            
    def set_target_to_current_position(self):
        """将目标坐标设置为当前鼠标位置"""
        x, y = self.get_current_mouse_position()
        self.set_target_position(x, y)
        return x, y
        
    def _get_screen_info(self) -> dict:
        """获取多屏幕信息"""
        try:
            if tk:
                # 使用tkinter获取屏幕信息
                root = tk.Tk()
                root.withdraw()  # 隐藏窗口
                
                # 获取所有屏幕的总尺寸
                total_width = root.winfo_screenwidth()
                total_height = root.winfo_screenheight()
                
                # 获取虚拟屏幕边界和偏移
                virtual_x = 0
                virtual_y = 0
                virtual_width = total_width
                virtual_height = total_height
                
                try:
                    # 尝试获取虚拟屏幕信息
                    virtual_width = root.winfo_vrootwidth()
                    virtual_height = root.winfo_vrootheight()
                    virtual_x = root.winfo_vrootx()
                    virtual_y = root.winfo_vrooty()
                    
                    if virtual_width > 0 and virtual_height > 0:
                        total_width = virtual_width
                        total_height = virtual_height
                except:
                    # 如果无法获取虚拟屏幕信息，尝试通过pyautogui获取
                    try:
                        import pyautogui
                        # 获取所有屏幕的边界
                        screens = pyautogui.getAllScreens() if hasattr(pyautogui, 'getAllScreens') else []
                        if screens:
                            min_x = min(screen.left for screen in screens)
                            min_y = min(screen.top for screen in screens)
                            max_x = max(screen.left + screen.width for screen in screens)
                            max_y = max(screen.top + screen.height for screen in screens)
                            virtual_x = min_x
                            virtual_y = min_y
                            total_width = max_x - min_x
                            total_height = max_y - min_y
                    except:
                        pass
                
                root.destroy()
                
                return {
                    'total_width': total_width,
                    'total_height': total_height,
                    'bounds': (virtual_x, virtual_y, virtual_x + total_width, virtual_y + total_height)
                }
            else:
                # 回退到pyautogui的屏幕尺寸
                size = pyautogui.size()
                return {
                    'total_width': size.width,
                    'total_height': size.height,
                    'bounds': (0, 0, size.width, size.height)
                }
        except Exception as e:
            # 如果获取失败，使用默认值
            size = pyautogui.size()
            return {
                'total_width': size.width,
                'total_height': size.height,
                'bounds': (0, 0, size.width, size.height)
            }
    
    def validate_coordinates(self, x: int, y: int) -> bool:
        """验证坐标有效性（支持多屏幕）"""
        # 检查坐标是否在所有屏幕范围内
        min_x, min_y, max_x, max_y = self.screen_bounds
        return min_x <= x < max_x and min_y <= y < max_y
        
    def perform_click(self, x: Optional[int] = None, y: Optional[int] = None):
        """执行点击操作（支持多屏幕）"""
        click_x = x if x is not None else self.target_x
        click_y = y if y is not None else self.target_y
        
        if not self.validate_coordinates(click_x, click_y):
            min_x, min_y, max_x, max_y = self.screen_bounds
            raise ValueError(f"坐标({click_x}, {click_y})超出屏幕范围({min_x}, {min_y}, {max_x}, {max_y})")
            
        try:
            # 通知状态变化
            if self.on_status_change:
                self.on_status_change(f"点击中 ({click_x}, {click_y})")
            
            # 确保pyautogui能处理多屏幕坐标
            # 对于负坐标或超大坐标，pyautogui可能需要特殊处理
            try:
                # 先尝试移动鼠标到目标位置
                pyautogui.moveTo(click_x, click_y, duration=0.1)
                # 然后执行点击
                pyautogui.click()
            except pyautogui.FailSafeException:
                raise Exception("触发了pyautogui安全模式，鼠标移动到了屏幕角落")
            except Exception as move_error:
                # 如果移动失败，尝试直接点击
                pyautogui.click(click_x, click_y)
            
            # 执行回调
            if self.on_click_callback:
                self.on_click_callback(click_x, click_y)
                
        except Exception as e:
            raise Exception(f"点击失败: {e}")
            
    def start_listening(self, hotkey: str = 'f1'):
        """开始监听指定热键"""
        if self.is_listening:
            return False
            
        if not self.validate_coordinates(self.target_x, self.target_y):
            min_x, min_y, max_x, max_y = self.screen_bounds
            raise ValueError(f"请先设置有效的目标坐标，当前屏幕范围: ({min_x}, {min_y}) 到 ({max_x}, {max_y})")
            
        self.is_listening = True
        
        # 通知状态变化
        if self.on_status_change:
            screen_info = f"屏幕范围: {self.total_width}x{self.total_height}"
            self.on_status_change(f"监听中 (按{hotkey.upper()}触发点击) - {screen_info}")
            
        # 在新线程中监听键盘
        threading.Thread(target=self._keyboard_listener, args=(hotkey,), daemon=True).start()
        return True
        
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        
        # 通知状态变化
        if self.on_status_change:
            self.on_status_change("待机")
            
    def _keyboard_listener(self, hotkey: str):
        """键盘监听线程"""
        while self.is_listening:
            try:
                if keyboard.is_pressed(hotkey):
                    self.perform_click()
                    # 防止重复触发
                    time.sleep(0.5)
                time.sleep(0.01)  # 减少CPU占用
            except Exception as e:
                # 监听过程中出错，停止监听
                self.stop_listening()
                if self.on_status_change:
                    self.on_status_change(f"监听错误: {e}")
                break
                
    def set_click_callback(self, callback: Callable[[int, int], None]):
        """设置点击回调函数"""
        self.on_click_callback = callback
        
    def set_status_callback(self, callback: Callable[[str], None]):
        """设置状态变化回调函数"""
        self.on_status_change = callback
        
    def is_listening_active(self) -> bool:
        """检查是否正在监听"""
        return self.is_listening
        
    def get_target_position(self) -> tuple[int, int]:
        """获取目标坐标"""
        return self.target_x, self.target_y
        
    def get_screen_info(self) -> dict:
        """获取屏幕信息"""
        return {
            'total_width': self.total_width,
            'total_height': self.total_height,
            'bounds': self.screen_bounds,
            'screen_count': self._estimate_screen_count()
        }
        
    def _estimate_screen_count(self) -> int:
        """估算屏幕数量"""
        try:
            # 基于总宽度和标准屏幕宽度估算
            standard_width = 1920  # 假设标准屏幕宽度
            if self.total_width >= standard_width * 2:
                return max(2, self.total_width // standard_width)
            return 1
        except:
            return 1
            
    def refresh_screen_info(self):
        """刷新屏幕信息（用于动态检测屏幕变化）"""
        self.screen_info = self._get_screen_info()
        self.total_width = self.screen_info['total_width']
        self.total_height = self.screen_info['total_height']
        self.screen_bounds = self.screen_info['bounds']
        
        if self.on_status_change:
            self.on_status_change(f"屏幕信息已刷新: {self.total_width}x{self.total_height}")
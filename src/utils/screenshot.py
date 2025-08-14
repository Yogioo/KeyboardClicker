#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图功能模块
提供桌面截图和图像保存功能
"""

import pyautogui
import os
from datetime import datetime
from typing import Optional, Callable
from PIL import Image

class ScreenshotTool:
    """截图工具类"""
    
    def __init__(self):
        self.default_save_path = "assets/screenshots"
        self.on_screenshot_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # 确保截图保存目录存在
        self._ensure_save_directory()
        
        # 设置pyautogui
        pyautogui.FAILSAFE = True
        
    def _ensure_save_directory(self):
        """确保截图保存目录存在"""
        if not os.path.exists(self.default_save_path):
            os.makedirs(self.default_save_path)
            
    def get_screen_size(self) -> tuple[int, int]:
        """获取屏幕尺寸"""
        try:
            return pyautogui.size()
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"获取屏幕尺寸失败: {e}")
            raise Exception(f"获取屏幕尺寸失败: {e}")
            
    def capture_full_screen(self) -> Image.Image:
        """捕获全屏截图"""
        try:
            screenshot = pyautogui.screenshot()
            if self.on_screenshot_callback:
                self.on_screenshot_callback("全屏截图完成")
            return screenshot
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"全屏截图失败: {e}")
            raise Exception(f"全屏截图失败: {e}")
            
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """捕获指定区域截图"""
        try:
            # 验证坐标和尺寸
            if not self._validate_region(x, y, width, height):
                raise ValueError("无效的截图区域参数")
                
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            if self.on_screenshot_callback:
                self.on_screenshot_callback(f"区域截图完成: ({x}, {y}, {width}, {height})")
            return screenshot
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"区域截图失败: {e}")
            raise Exception(f"区域截图失败: {e}")
            
    def _validate_region(self, x: int, y: int, width: int, height: int) -> bool:
        """验证截图区域参数"""
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return False
            
        screen_width, screen_height = self.get_screen_size()
        if x + width > screen_width or y + height > screen_height:
            return False
            
        return True
        
    def save_screenshot(self, image: Image.Image, filename: Optional[str] = None, 
                      save_path: Optional[str] = None) -> str:
        """保存截图到文件"""
        try:
            # 生成文件名
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            elif not filename.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                filename += '.png'
                
            # 确定保存路径
            if save_path is None:
                save_path = self.default_save_path
                
            # 确保保存目录存在
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                
            # 完整文件路径
            full_path = os.path.join(save_path, filename)
            
            # 保存图片
            image.save(full_path)
            
            if self.on_screenshot_callback:
                self.on_screenshot_callback(f"截图已保存: {full_path}")
                
            return full_path
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"保存截图失败: {e}")
            raise Exception(f"保存截图失败: {e}")
            
    def capture_and_save_full_screen(self, filename: Optional[str] = None, 
                                   save_path: Optional[str] = None) -> str:
        """捕获并保存全屏截图"""
        screenshot = self.capture_full_screen()
        return self.save_screenshot(screenshot, filename, save_path)
        
    def capture_and_save_region(self, x: int, y: int, width: int, height: int,
                              filename: Optional[str] = None, 
                              save_path: Optional[str] = None) -> str:
        """捕获并保存指定区域截图"""
        screenshot = self.capture_region(x, y, width, height)
        return self.save_screenshot(screenshot, filename, save_path)
        
    def get_all_screenshots(self, directory: Optional[str] = None) -> list[str]:
        """获取指定目录下的所有截图文件"""
        if directory is None:
            directory = self.default_save_path
            
        if not os.path.exists(directory):
            return []
            
        screenshot_files = []
        supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        
        try:
            for filename in os.listdir(directory):
                if filename.lower().endswith(supported_formats):
                    full_path = os.path.join(directory, filename)
                    screenshot_files.append(full_path)
                    
            # 按修改时间排序（最新的在前）
            screenshot_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return screenshot_files
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"获取截图文件列表失败: {e}")
            return []
            
    def delete_screenshot(self, file_path: str) -> bool:
        """删除指定的截图文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                if self.on_screenshot_callback:
                    self.on_screenshot_callback(f"截图已删除: {file_path}")
                return True
            else:
                if self.on_error_callback:
                    self.on_error_callback(f"文件不存在: {file_path}")
                return False
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"删除截图失败: {e}")
            return False
            
    def set_default_save_path(self, path: str):
        """设置默认保存路径"""
        self.default_save_path = path
        self._ensure_save_directory()
        
    def get_default_save_path(self) -> str:
        """获取默认保存路径"""
        return self.default_save_path
        
    def set_screenshot_callback(self, callback: Callable[[str], None]):
        """设置截图操作回调函数"""
        self.on_screenshot_callback = callback
        
    def set_error_callback(self, callback: Callable[[str], None]):
        """设置错误回调函数"""
        self.on_error_callback = callback
        
    def get_screenshot_info(self, file_path: str) -> dict:
        """获取截图文件信息"""
        try:
            if not os.path.exists(file_path):
                return {}
                
            stat = os.stat(file_path)
            with Image.open(file_path) as img:
                return {
                    'file_path': file_path,
                    'filename': os.path.basename(file_path),
                    'size_bytes': stat.st_size,
                    'created_time': datetime.fromtimestamp(stat.st_ctime),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime),
                    'width': img.width,
                    'height': img.height,
                    'format': img.format
                }
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"获取截图信息失败: {e}")
            return {}
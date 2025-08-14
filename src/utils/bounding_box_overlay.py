#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边界框覆盖层工具
用于在屏幕上显示检测结果的边界框
"""

import tkinter as tk
from typing import List, Dict, Optional, Any, Callable


class BoundingBoxOverlay:
    """边界框覆盖层工具类
    
    用于在屏幕上显示透明的红色边界框，标识检测到的区域
    """
    
    def __init__(self):
        # 边界框窗口列表
        self._bbox_windows = []
        # 根窗口
        self._bbox_root = None
        # 回调函数
        self._error_callback = None
        self._info_callback = None
    
    def SetErrorCallback(self, callback: Callable[[str], None]):
        """设置错误回调函数"""
        self._error_callback = callback
    
    def SetInfoCallback(self, callback: Callable[[str], None]):
        """设置信息回调函数"""
        self._info_callback = callback
    
    def _OnError(self, message: str):
        """内部错误处理"""
        if self._error_callback:
            self._error_callback(message)
        else:
            print(f"[BoundingBoxOverlay错误] {message}")
    
    def _OnInfo(self, message: str):
        """内部信息处理"""
        if self._info_callback:
            self._info_callback(message)
        else:
            print(f"[BoundingBoxOverlay] {message}")
    
    def ShowBoundingBoxes(self, detections: List[Dict[str, Any]], duration: Optional[float] = None, 
                         box_color: str = 'red', box_width: int = 2, alpha: float = 0.8) -> bool:
        """显示边界框
        
        Args:
            detections: 检测结果列表，每个元素应包含'bbox'字段 (x, y, width, height)
            duration: 显示持续时间(秒)，None表示永久显示
            box_color: 边界框颜色，默认'red'
            box_width: 边界框线宽，默认2
            alpha: 窗口透明度，默认0.8
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if not detections:
                self._OnError("没有检测结果数据")
                return False
            
            # 清理之前的边界框
            self.HideBoundingBoxes()
            
            # 创建根窗口（如果不存在）
            if self._bbox_root is None:
                self._bbox_root = tk.Tk()
                self._bbox_root.withdraw()  # 隐藏主窗口
            
            self._OnInfo(f"显示 {len(detections)} 个区域的边界框")
            
            # 为每个检测结果创建边界框窗口
            for detection in detections:
                bbox_window = self._CreateBboxWindow(detection, box_color, box_width, alpha)
                if bbox_window:
                    self._bbox_windows.append(bbox_window)
            
            # 强制更新所有窗口
            self._ForceUpdateWindows()
            
            # 如果指定了持续时间，则自动隐藏
            if duration and duration > 0:
                self._bbox_root.after(int(duration * 1000), self.HideBoundingBoxes)
            
            return True
            
        except Exception as e:
            self._OnError(f"显示边界框失败: {e}")
            return False
    
    def _CreateBboxWindow(self, detection: Dict[str, Any], box_color: str, 
                         box_width: int, alpha: float) -> Optional[tk.Toplevel]:
        """创建单个边界框窗口
        
        Args:
            detection: 检测结果，必须包含'bbox'字段
            box_color: 边界框颜色
            box_width: 边界框线宽
            alpha: 透明度
        
        Returns:
            创建的窗口对象，失败返回None
        """
        try:
            # 获取边界框坐标
            if 'bbox' not in detection:
                self._OnError("检测结果缺少bbox字段")
                return None
            
            x, y, w, h = detection['bbox']
            
            # 创建透明窗口
            bbox_window = tk.Toplevel(self._bbox_root)
            bbox_window.overrideredirect(True)  # 无边框
            bbox_window.attributes('-topmost', True)  # 置顶
            bbox_window.attributes('-alpha', alpha)  # 透明度
            
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
            
            # 绘制空心矩形
            canvas.create_rectangle(
                2, 2, w-2, h-2,
                outline=box_color,
                fill='',
                width=box_width
            )
            
            # 设置透明背景
            bbox_window.wm_attributes('-transparentcolor', 'black')
            
            return bbox_window
            
        except Exception as e:
            self._OnError(f"创建边界框窗口失败: {e}")
            return None
    
    def _ForceUpdateWindows(self):
        """强制更新所有窗口显示"""
        try:
            if self._bbox_root:
                self._bbox_root.update()
                self._bbox_root.update_idletasks()
            
            for window in self._bbox_windows:
                try:
                    window.update()
                    window.update_idletasks()
                    window.deiconify()  # 确保窗口显示
                    window.lift()       # 提升到前台
                except:
                    pass
                    
        except Exception as e:
            self._OnError(f"强制更新窗口失败: {e}")
    
    def HideBoundingBoxes(self):
        """隐藏所有边界框"""
        try:
            # 销毁所有边界框窗口
            for window in self._bbox_windows:
                try:
                    window.destroy()
                except:
                    pass
            self._bbox_windows.clear()
            
            # 销毁根窗口
            if self._bbox_root:
                try:
                    self._bbox_root.destroy()
                    self._bbox_root = None
                except:
                    pass
            
            self._OnInfo("所有边界框已隐藏")
            
        except Exception as e:
            self._OnError(f"隐藏边界框失败: {e}")
    
    def ShowBoundingBoxesFromCoords(self, coords_list: List[tuple], duration: Optional[float] = None,
                                   box_color: str = 'red', box_width: int = 2, alpha: float = 0.8) -> bool:
        """从坐标列表显示边界框
        
        Args:
            coords_list: 坐标列表，每个元素为(x, y, width, height)
            duration: 显示持续时间(秒)
            box_color: 边界框颜色
            box_width: 边界框线宽
            alpha: 透明度
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            # 将坐标转换为检测结果格式
            detections = []
            for i, coords in enumerate(coords_list):
                if len(coords) != 4:
                    self._OnError(f"坐标 {i} 格式错误，应为(x, y, width, height)")
                    continue
                
                detection = {
                    'bbox': coords,
                    'id': i
                }
                detections.append(detection)
            
            success = self.ShowBoundingBoxes(detections, duration, box_color, box_width, alpha)
            if success:
                self._ForceUpdateWindows()  # 额外强制更新
            return success
            
        except Exception as e:
            self._OnError(f"从坐标显示边界框失败: {e}")
            return False
    
    def ShowCustomBoundingBox(self, x: int, y: int, width: int, height: int, 
                             duration: Optional[float] = None, box_color: str = 'red', 
                             box_width: int = 2, alpha: float = 0.8) -> bool:
        """显示单个自定义边界框
        
        Args:
            x, y: 左上角坐标
            width, height: 宽度和高度
            duration: 显示持续时间(秒)
            box_color: 边界框颜色
            box_width: 边界框线宽
            alpha: 透明度
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        detection = {
            'bbox': (x, y, width, height),
            'id': 'custom'
        }
        success = self.ShowBoundingBoxes([detection], duration, box_color, box_width, alpha)
        if success:
            self._ForceUpdateWindows()  # 额外强制更新
        return success
    
    def GetActiveBoxCount(self) -> int:
        """获取当前活跃的边界框数量"""
        return len(self._bbox_windows)
    
    def IsShowing(self) -> bool:
        """检查是否正在显示边界框"""
        return len(self._bbox_windows) > 0
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.HideBoundingBoxes()
        except:
            pass


# #region 示例用法函数
def demo_bounding_box_overlay():
    """边界框覆盖层演示"""
    import time
    
    print("=== 边界框覆盖层演示 ===")
    
    # 创建边界框工具
    bbox_overlay = BoundingBoxOverlay()
    
    try:
        # 演示1: 显示多个边界框
        print("演示1: 显示多个检测结果的边界框")
        detections = [
            {'bbox': (100, 100, 200, 50), 'text': '检测结果1'},
            {'bbox': (300, 150, 150, 40), 'text': '检测结果2'},
            {'bbox': (50, 250, 180, 60), 'text': '检测结果3'}
        ]
        
        if bbox_overlay.ShowBoundingBoxes(detections, duration=3.0):
            print("边界框显示3秒...")
            time.sleep(3)
        
        # 演示2: 从坐标列表显示
        print("演示2: 从坐标列表显示边界框")
        coords = [(400, 100, 120, 30), (500, 200, 100, 25)]
        if bbox_overlay.ShowBoundingBoxesFromCoords(coords, duration=2.0, box_color='blue'):
            print("蓝色边界框显示2秒...")
            time.sleep(2)
        
        # 演示3: 自定义单个边界框
        print("演示3: 显示自定义边界框")
        if bbox_overlay.ShowCustomBoundingBox(600, 300, 200, 80, duration=2.0, 
                                            box_color='green', box_width=3):
            print("绿色粗边界框显示2秒...")
            time.sleep(2)
        
        print("演示完成")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    finally:
        # 确保清理
        bbox_overlay.HideBoundingBoxes()


if __name__ == "__main__":
    demo_bounding_box_overlay()
# #endregion
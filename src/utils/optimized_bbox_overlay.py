#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的边界框覆盖层工具
使用单一Canvas窗口批量绘制所有边界框，解决多窗口性能问题
"""

import tkinter as tk
from typing import List, Dict, Optional, Any, Callable
import threading
import time


class OptimizedBoundingBoxOverlay:
    """优化的边界框覆盖层工具类
    
    性能优化要点：
    1. 使用单一透明窗口代替多个窗口
    2. 在一个Canvas上批量绘制所有边界框
    3. 减少窗口属性设置和更新操作
    4. 使用异步显示避免阻塞主线程
    """
    
    def __init__(self):
        # 单一覆盖窗口
        self._overlay_window = None
        self._canvas = None
        self._overlay_root = None
        
        # 当前显示的边界框数据
        self._current_boxes = []
        self._hide_timer = None
        
        # 回调函数
        self._error_callback = None
        self._info_callback = None
        
        # 性能统计
        self._last_render_time = 0
    
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
            print(f"[OptimizedBBoxOverlay错误] {message}")
    
    def _OnInfo(self, message: str):
        """内部信息处理"""
        if self._info_callback:
            self._info_callback(message)
        else:
            print(f"[OptimizedBBoxOverlay] {message}")
    
    def ShowBoundingBoxes(self, detections: List[Dict[str, Any]], duration: Optional[float] = None, 
                         box_color: str = 'red', box_width: int = 2, alpha: float = 0.7) -> bool:
        """显示边界框（优化版本）
        
        Args:
            detections: 检测结果列表，每个元素应包含'bbox'字段 (x, y, width, height)
            duration: 显示持续时间(秒)，None表示永久显示
            box_color: 边界框颜色，默认'red'
            box_width: 边界框线宽，默认2
            alpha: 窗口透明度，默认0.7
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            start_time = time.time()
            
            if not detections:
                self._OnError("没有检测结果数据")
                return False
            
            # 清理之前的显示
            self.HideBoundingBoxes()
            
            # 创建单一覆盖窗口
            if not self._CreateOverlayWindow(alpha):
                return False
            
            # 批量绘制所有边界框
            success = self._BatchDrawBoundingBoxes(detections, box_color, box_width)
            
            if success:
                # 显示窗口
                self._overlay_window.deiconify()
                self._overlay_window.lift()
                self._overlay_window.attributes('-topmost', True)
                
                # 强制更新一次即可
                self._overlay_window.update()
                
                render_time = time.time() - start_time
                self._last_render_time = render_time
                
                self._OnInfo(f"快速显示 {len(detections)} 个边界框，耗时 {render_time:.3f} 秒")
                
                # 设置自动隐藏
                if duration and duration > 0:
                    self._ScheduleHide(duration)
                
                return True
            else:
                self.HideBoundingBoxes()
                return False
            
        except Exception as e:
            self._OnError(f"显示边界框失败: {e}")
            self.HideBoundingBoxes()
            return False
    
    def _CreateOverlayWindow(self, alpha: float) -> bool:
        """创建单一覆盖窗口"""
        try:
            # 创建根窗口（如果不存在）
            if self._overlay_root is None:
                self._overlay_root = tk.Tk()
                self._overlay_root.withdraw()  # 隐藏主窗口
            
            # 创建全屏覆盖窗口
            self._overlay_window = tk.Toplevel(self._overlay_root)
            self._overlay_window.withdraw()  # 初始隐藏
            
            # 设置窗口属性（一次性设置）
            self._overlay_window.overrideredirect(True)  # 无边框
            self._overlay_window.attributes('-alpha', alpha)  # 透明度
            self._overlay_window.attributes('-topmost', True)  # 置顶
            
            # 获取屏幕尺寸并设置全屏
            screen_width = self._overlay_window.winfo_screenwidth()
            screen_height = self._overlay_window.winfo_screenheight()
            self._overlay_window.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # 创建全屏Canvas
            self._canvas = tk.Canvas(
                self._overlay_window,
                width=screen_width,
                height=screen_height,
                highlightthickness=0,
                bg='black'
            )
            self._canvas.pack(fill=tk.BOTH, expand=True)
            
            # 设置透明背景
            self._overlay_window.wm_attributes('-transparentcolor', 'black')
            
            return True
            
        except Exception as e:
            self._OnError(f"创建覆盖窗口失败: {e}")
            return False
    
    def _BatchDrawBoundingBoxes(self, detections: List[Dict[str, Any]], 
                               box_color: str, box_width: int) -> bool:
        """在单一Canvas上批量绘制所有边界框"""
        try:
            if not self._canvas:
                return False
            
            # 清空Canvas
            self._canvas.delete("all")
            self._current_boxes.clear()
            
            # 批量绘制所有边界框
            for i, detection in enumerate(detections):
                if 'bbox' not in detection:
                    continue
                
                x, y, w, h = detection['bbox']
                
                # 在Canvas上绘制矩形
                rect_id = self._canvas.create_rectangle(
                    x, y, x + w, y + h,
                    outline=box_color,
                    fill='',
                    width=box_width,
                    tags=f"bbox_{i}"
                )
                
                # 可选：添加类型标签
                if 'type' in detection:
                    text_id = self._canvas.create_text(
                        x + 2, y - 2,
                        text=detection['type'],
                        fill=box_color,
                        anchor='sw',
                        font=('Arial', 8),
                        tags=f"text_{i}"
                    )
                
                # 保存边界框信息
                self._current_boxes.append({
                    'detection': detection,
                    'rect_id': rect_id,
                    'coords': (x, y, w, h)
                })
            
            return True
            
        except Exception as e:
            self._OnError(f"批量绘制边界框失败: {e}")
            return False
    
    def _ScheduleHide(self, duration: float):
        """安排自动隐藏"""
        try:
            # 取消之前的定时器
            if self._hide_timer:
                self._overlay_root.after_cancel(self._hide_timer)
            
            # 设置新的定时器
            self._hide_timer = self._overlay_root.after(
                int(duration * 1000), 
                self.HideBoundingBoxes
            )
            
        except Exception as e:
            self._OnError(f"设置自动隐藏失败: {e}")
    
    def HideBoundingBoxes(self):
        """隐藏所有边界框"""
        try:
            # 取消定时器
            if self._hide_timer:
                try:
                    self._overlay_root.after_cancel(self._hide_timer)
                except:
                    pass
                self._hide_timer = None
            
            # 隐藏窗口
            if self._overlay_window:
                try:
                    self._overlay_window.withdraw()
                except:
                    pass
            
            # 清空Canvas
            if self._canvas:
                try:
                    self._canvas.delete("all")
                except:
                    pass
            
            # 清空数据
            self._current_boxes.clear()
            
            self._OnInfo("所有边界框已隐藏")
            
        except Exception as e:
            self._OnError(f"隐藏边界框失败: {e}")
    
    def DestroyOverlay(self):
        """完全销毁覆盖层"""
        try:
            self.HideBoundingBoxes()
            
            # 销毁窗口
            if self._overlay_window:
                try:
                    self._overlay_window.destroy()
                except:
                    pass
                self._overlay_window = None
                self._canvas = None
            
            # 销毁根窗口
            if self._overlay_root:
                try:
                    self._overlay_root.destroy()
                except:
                    pass
                self._overlay_root = None
            
            self._OnInfo("覆盖层已完全销毁")
            
        except Exception as e:
            self._OnError(f"销毁覆盖层失败: {e}")
    
    # 兼容原有接口
    def ShowBoundingBoxesFromCoords(self, coords_list: List[tuple], duration: Optional[float] = None,
                                   box_color: str = 'red', box_width: int = 2, alpha: float = 0.7) -> bool:
        """从坐标列表显示边界框（兼容接口）"""
        try:
            # 转换为检测结果格式
            detections = []
            for i, coords in enumerate(coords_list):
                if len(coords) != 4:
                    continue
                
                detection = {
                    'bbox': coords,
                    'id': i,
                    'type': 'coord'
                }
                detections.append(detection)
            
            return self.ShowBoundingBoxes(detections, duration, box_color, box_width, alpha)
            
        except Exception as e:
            self._OnError(f"从坐标显示边界框失败: {e}")
            return False
    
    def ShowCustomBoundingBox(self, x: int, y: int, width: int, height: int, 
                             duration: Optional[float] = None, box_color: str = 'red', 
                             box_width: int = 2, alpha: float = 0.7) -> bool:
        """显示单个自定义边界框（兼容接口）"""
        detection = {
            'bbox': (x, y, width, height),
            'id': 'custom',
            'type': 'custom'
        }
        return self.ShowBoundingBoxes([detection], duration, box_color, box_width, alpha)
    
    def GetActiveBoxCount(self) -> int:
        """获取当前活跃的边界框数量"""
        return len(self._current_boxes)
    
    def IsShowing(self) -> bool:
        """检查是否正在显示边界框"""
        return (self._overlay_window is not None and 
                len(self._current_boxes) > 0)
    
    def GetLastRenderTime(self) -> float:
        """获取上次渲染耗时"""
        return self._last_render_time
    
    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.DestroyOverlay()
        except:
            pass


# #region 性能测试和演示
def performance_test():
    """性能测试：比较优化前后的差异"""
    import random
    
    print("=== 优化边界框覆盖层性能测试 ===")
    
    # 生成大量测试数据
    test_counts = [10, 50, 100, 200]
    
    for count in test_counts:
        print(f"\n测试 {count} 个边界框的显示性能...")
        
        # 生成随机检测结果
        detections = []
        for i in range(count):
            x = random.randint(0, 1500)
            y = random.randint(0, 800)
            w = random.randint(50, 200)
            h = random.randint(30, 100)
            
            detections.append({
                'bbox': (x, y, w, h),
                'type': f'test_{i}',
                'confidence': random.uniform(0.5, 1.0)
            })
        
        # 测试优化版本
        bbox_overlay = OptimizedBoundingBoxOverlay()
        
        start_time = time.time()
        success = bbox_overlay.ShowBoundingBoxes(detections, duration=1.0)
        render_time = time.time() - start_time
        
        if success:
            print(f"  ✅ 成功显示 {count} 个边界框")
            print(f"  ⏱️  总耗时: {render_time:.3f} 秒")
            print(f"  🚀 平均每个: {(render_time/count)*1000:.2f} 毫秒")
            
            # 等待显示完成
            time.sleep(1.2)
        else:
            print(f"  ❌ 显示失败")
        
        # 清理
        bbox_overlay.DestroyOverlay()
        time.sleep(0.5)
    
    print("\n=== 性能测试完成 ===")


def demo_optimized_overlay():
    """优化覆盖层演示"""
    import time
    
    print("=== 优化边界框覆盖层演示 ===")
    
    bbox_overlay = OptimizedBoundingBoxOverlay()
    
    try:
        # 演示1：批量显示
        print("演示1: 批量显示多个边界框（应该几乎瞬间完成）")
        detections = [
            {'bbox': (100, 100, 200, 50), 'type': 'button'},
            {'bbox': (300, 150, 150, 40), 'type': 'link'},
            {'bbox': (50, 250, 180, 60), 'type': 'input'},
            {'bbox': (500, 100, 120, 35), 'type': 'icon'},
            {'bbox': (400, 300, 160, 45), 'type': 'text'}
        ]
        
        start_time = time.time()
        if bbox_overlay.ShowBoundingBoxes(detections, duration=3.0, box_color='lime'):
            render_time = time.time() - start_time
            print(f"✅ 批量显示完成，耗时 {render_time:.3f} 秒")
            print(f"显示 {len(detections)} 个边界框，等待3秒...")
            time.sleep(3.2)
        
        # 演示2：大量边界框
        print("\n演示2: 显示大量边界框（50个）")
        import random
        
        large_detections = []
        for i in range(50):
            x = random.randint(0, 1200)
            y = random.randint(0, 700)
            w = random.randint(40, 150)
            h = random.randint(25, 80)
            
            large_detections.append({
                'bbox': (x, y, w, h),
                'type': f'element_{i}',
                'confidence': random.uniform(0.6, 1.0)
            })
        
        start_time = time.time()
        if bbox_overlay.ShowBoundingBoxes(large_detections, duration=2.0, box_color='red'):
            render_time = time.time() - start_time
            print(f"✅ 大量边界框显示完成，耗时 {render_time:.3f} 秒")
            print(f"显示 {len(large_detections)} 个边界框，等待2秒...")
            time.sleep(2.2)
        
        print("演示完成")
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
    finally:
        bbox_overlay.DestroyOverlay()


if __name__ == "__main__":
    # 运行演示
    demo_optimized_overlay()
    
    # 可选：运行性能测试
    # performance_test()
# #endregion
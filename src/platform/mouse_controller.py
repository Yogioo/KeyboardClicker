# -*- coding: utf-8 -*-
"""
鼠标控制器实现
使用pynput库实现精确的鼠标操作控制
"""

import time
import math
import threading
from typing import Tuple, Optional
from pynput import mouse
from pynput.mouse import Button, Listener

from .interfaces import IMouseController, MouseOperationError


class MouseController(IMouseController):
    """鼠标控制器实现"""
    
    def __init__(self):
        #region 私有属性初始化
        self._mouse = mouse.Controller()
        self._lock = threading.RLock()
        self._last_operation_time = 0
        self._operation_interval = 0.01  # 操作间隔10ms
        self._smooth_move_steps = 20  # 平滑移动步数
        #endregion
    
    #region 基础鼠标操作
    
    def MoveTo(self, x: int, y: int) -> bool:
        """移动鼠标到指定坐标"""
        try:
            with self._lock:
                # 验证坐标
                if not self._ValidateCoordinates(x, y):
                    raise MouseOperationError(f"无效的坐标: ({x}, {y})")
                
                # 控制操作频率
                self._WaitForOperationInterval()
                
                # 执行移动
                self._mouse.position = (x, y)
                
                # 验证移动结果
                actual_pos = self._mouse.position
                if abs(actual_pos[0] - x) > 2 or abs(actual_pos[1] - y) > 2:
                    raise MouseOperationError(f"鼠标移动失败，目标: ({x}, {y}), 实际: {actual_pos}")
                
                self._last_operation_time = time.time()
                return True
                
        except Exception as e:
            if isinstance(e, MouseOperationError):
                raise
            raise MouseOperationError(f"鼠标移动操作失败: {str(e)}")
    
    def LeftClick(self, x: int, y: int) -> bool:
        """执行左键单击"""
        return self._PerformClick(x, y, Button.left, "左键")
    
    def RightClick(self, x: int, y: int) -> bool:
        """执行右键单击"""
        return self._PerformClick(x, y, Button.right, "右键")
    
    def DoubleClick(self, x: int, y: int) -> bool:
        """执行双击"""
        try:
            # 移动到目标位置
            if not self.MoveTo(x, y):
                return False
            
            with self._lock:
                # 控制操作频率
                self._WaitForOperationInterval()
                
                # 执行双击
                self._mouse.click(Button.left, 2)
                
                self._last_operation_time = time.time()
                return True
                
        except Exception as e:
            raise MouseOperationError(f"双击操作失败: {str(e)}")
    
    def GetCursorPosition(self) -> Tuple[int, int]:
        """获取当前光标位置"""
        try:
            pos = self._mouse.position
            return (int(pos[0]), int(pos[1]))
        except Exception as e:
            raise MouseOperationError(f"获取光标位置失败: {str(e)}")
    
    def SmoothMoveTo(self, x: int, y: int, duration_ms: int = 100) -> bool:
        """平滑移动到指定位置"""
        try:
            with self._lock:
                # 验证坐标
                if not self._ValidateCoordinates(x, y):
                    raise MouseOperationError(f"无效的坐标: ({x}, {y})")
                
                # 获取起始位置
                start_pos = self.GetCursorPosition()
                start_x, start_y = start_pos
                
                # 如果已经在目标位置，直接返回
                if abs(start_x - x) <= 1 and abs(start_y - y) <= 1:
                    return True
                
                # 计算移动参数
                total_distance = math.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)
                steps = max(self._smooth_move_steps, int(total_distance / 10))
                step_duration = max(0.005, duration_ms / 1000 / steps)  # 最小5ms间隔
                
                # 执行平滑移动
                for i in range(1, steps + 1):
                    progress = i / steps
                    # 使用缓动函数 (ease-out)
                    eased_progress = 1 - (1 - progress) ** 2
                    
                    current_x = int(start_x + (x - start_x) * eased_progress)
                    current_y = int(start_y + (y - start_y) * eased_progress)
                    
                    self._mouse.position = (current_x, current_y)
                    time.sleep(step_duration)
                
                # 确保精确到达目标位置
                self._mouse.position = (x, y)
                
                self._last_operation_time = time.time()
                return True
                
        except Exception as e:
            if isinstance(e, MouseOperationError):
                raise
            raise MouseOperationError(f"平滑移动操作失败: {str(e)}")
    
    #endregion
    
    #region 私有辅助方法
    
    def _PerformClick(self, x: int, y: int, button: Button, button_name: str) -> bool:
        """执行点击操作的通用方法"""
        try:
            # 移动到目标位置
            if not self.MoveTo(x, y):
                return False
            
            with self._lock:
                # 控制操作频率
                self._WaitForOperationInterval()
                
                # 执行点击
                self._mouse.click(button, 1)
                
                self._last_operation_time = time.time()
                return True
                
        except Exception as e:
            raise MouseOperationError(f"{button_name}点击操作失败: {str(e)}")
    
    def _ValidateCoordinates(self, x: int, y: int) -> bool:
        """验证坐标是否有效"""
        # 基本范围检查 (假设最大分辨率为8K)
        if x < -100 or x > 8192 or y < -100 or y > 8192:
            return False
        return True
    
    def _WaitForOperationInterval(self) -> None:
        """等待操作间隔，避免操作过于频繁"""
        if self._last_operation_time > 0:
            elapsed = time.time() - self._last_operation_time
            if elapsed < self._operation_interval:
                time.sleep(self._operation_interval - elapsed)
    
    #endregion
    
    #region 高级功能
    
    def SetOperationInterval(self, interval_ms: float) -> None:
        """设置操作间隔"""
        with self._lock:
            self._operation_interval = max(0.001, interval_ms / 1000.0)  # 最小1ms
    
    def SetSmoothMoveSteps(self, steps: int) -> None:
        """设置平滑移动步数"""
        with self._lock:
            self._smooth_move_steps = max(5, min(100, steps))  # 5-100步
    
    def GetOperationStats(self) -> dict:
        """获取操作统计信息"""
        with self._lock:
            return {
                'last_operation_time': self._last_operation_time,
                'operation_interval_ms': self._operation_interval * 1000,
                'smooth_move_steps': self._smooth_move_steps,
                'current_position': self.GetCursorPosition()
            }
    
    #endregion
    
    #region 屏幕管理集成
    
    def ValidateScreenCoordinates(self, x: int, y: int, screen_width: int, screen_height: int) -> bool:
        """验证坐标是否在指定屏幕范围内"""
        return 0 <= x < screen_width and 0 <= y < screen_height
    
    def ClampToScreen(self, x: int, y: int, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """将坐标限制在屏幕范围内"""
        clamped_x = max(0, min(x, screen_width - 1))
        clamped_y = max(0, min(y, screen_height - 1))
        return (clamped_x, clamped_y)
    
    #endregion
    
    #region 测试和调试支持
    
    def TestMouseOperation(self) -> dict:
        """测试鼠标操作功能"""
        try:
            test_results = {}
            
            # 测试获取位置
            start_pos = self.GetCursorPosition()
            test_results['get_position'] = True
            
            # 测试移动
            test_x, test_y = start_pos[0] + 10, start_pos[1] + 10
            move_success = self.MoveTo(test_x, test_y)
            test_results['move_to'] = move_success
            
            # 恢复原位置
            self.MoveTo(start_pos[0], start_pos[1])
            test_results['restore_position'] = True
            
            return test_results
            
        except Exception as e:
            return {'error': str(e)}
    
    #endregion
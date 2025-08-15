# -*- coding: utf-8 -*-
"""
平台管理器 - 统一的平台操作门面
提供统一的接口来管理所有平台相关的操作
"""

import threading
import time
from typing import Callable, Dict, Optional, Tuple, Any
from contextlib import contextmanager

from .interfaces import (
    HotkeyModifier, 
    SystemMetrics, 
    IPlatformException,
    HotkeyRegistrationError,
    MouseOperationError,
    SystemResourceError
)
from .hotkey_manager import HotkeyManager
from .keyboard_listener import KeyboardListener
from .mouse_controller import MouseController
from .screen_manager import ScreenManager
from .system_manager import SystemManager


class PlatformManager:
    """平台管理器 - 统一管理所有平台操作"""
    
    def __init__(self):
        #region 组件初始化
        self._hotkey_manager = HotkeyManager()
        self._keyboard_listener = KeyboardListener()
        self._mouse_controller = MouseController()
        self._screen_manager = ScreenManager()
        self._system_manager = SystemManager()
        
        self._lock = threading.RLock()
        self._initialized = False
        self._error_recovery_enabled = True
        self._operation_timeout = 5.0  # 操作超时5秒
        #endregion
    
    #region 初始化和清理
    
    def Initialize(self) -> bool:
        """初始化平台管理器"""
        try:
            with self._lock:
                if self._initialized:
                    return True
                
                # 检查系统兼容性
                compatibility = self._system_manager.CheckSystemCompatibility()
                if not self._ValidateCompatibility(compatibility):
                    raise SystemResourceError("系统兼容性检查失败")
                
                # 设置系统优化
                self._system_manager.OptimizeForPerformance()
                
                # 注册错误恢复处理器
                if self._error_recovery_enabled:
                    self._SetupErrorRecovery()
                
                self._initialized = True
                return True
                
        except Exception as e:
            raise IPlatformException(f"平台管理器初始化失败: {str(e)}")
    
    def Cleanup(self) -> None:
        """清理所有资源"""
        try:
            with self._lock:
                if not self._initialized:
                    return
                
                # 停止所有活动
                self._hotkey_manager.UnregisterAll()
                self._keyboard_listener.StopListening()
                self._system_manager.StopResourceMonitoring()
                
                # 恢复系统设置
                self._system_manager.RestoreDefaultSettings()
                
                self._initialized = False
                
        except Exception:
            # 忽略清理异常，确保程序能正常退出
            pass
    
    #endregion
    
    #region 热键管理
    
    def RegisterActivationHotkey(self, callback: Callable[[], None]) -> bool:
        """注册激活热键 (Alt+G)"""
        try:
            return self._ExecuteWithErrorRecovery(
                lambda: self._hotkey_manager.RegisterHotkey(
                    'g', (HotkeyModifier.ALT,), callback
                ),
                "注册激活热键"
            )
        except Exception as e:
            raise HotkeyRegistrationError(f"注册激活热键失败: {str(e)}")
    
    def RegisterExitHotkey(self, callback: Callable[[], None]) -> bool:
        """注册退出热键 (Esc)"""
        try:
            return self._ExecuteWithErrorRecovery(
                lambda: self._hotkey_manager.RegisterHotkey(
                    'escape', (), callback
                ),
                "注册退出热键"
            )
        except Exception as e:
            raise HotkeyRegistrationError(f"注册退出热键失败: {str(e)}")
    
    def UnregisterAllHotkeys(self) -> None:
        """注销所有热键"""
        self._hotkey_manager.UnregisterAll()
    
    #endregion
    
    #region 键盘监听
    
    def StartKeyboardListening(self, handler: Callable[[str], None]) -> bool:
        """开始键盘监听"""
        try:
            self._keyboard_listener.RegisterKeyHandler(handler)
            return self._ExecuteWithErrorRecovery(
                lambda: self._keyboard_listener.StartListening(),
                "启动键盘监听"
            )
        except Exception as e:
            raise IPlatformException(f"启动键盘监听失败: {str(e)}")
    
    def StopKeyboardListening(self) -> None:
        """停止键盘监听"""
        self._keyboard_listener.StopListening()
    
    def IsKeyboardListening(self) -> bool:
        """检查是否正在监听键盘"""
        return self._keyboard_listener.IsListening()
    
    #endregion
    
    #region 鼠标控制
    
    def ClickAt(self, x: int, y: int, button: str = "left", smooth: bool = False) -> bool:
        """在指定位置点击"""
        try:
            # 验证坐标
            if not self._screen_manager.ValidateCoordinates(x, y):
                # 尝试修正坐标
                screen_rect = self._screen_manager.GetPrimaryScreenRect()
                x, y = self._screen_manager.ClampToScreen(x, y, screen_rect)
            
            # 执行点击
            if button.lower() == "left":
                return self._ExecuteWithErrorRecovery(
                    lambda: self._mouse_controller.LeftClick(x, y),
                    f"左键点击 ({x}, {y})"
                )
            elif button.lower() == "right":
                return self._ExecuteWithErrorRecovery(
                    lambda: self._mouse_controller.RightClick(x, y),
                    f"右键点击 ({x}, {y})"
                )
            else:
                raise MouseOperationError(f"不支持的鼠标按键: {button}")
                
        except Exception as e:
            raise MouseOperationError(f"鼠标点击操作失败: {str(e)}")
    
    def HoverAt(self, x: int, y: int, smooth: bool = True) -> bool:
        """移动到指定位置(悬停)"""
        try:
            # 验证坐标
            if not self._screen_manager.ValidateCoordinates(x, y):
                screen_rect = self._screen_manager.GetPrimaryScreenRect()
                x, y = self._screen_manager.ClampToScreen(x, y, screen_rect)
            
            # 执行移动
            if smooth:
                return self._ExecuteWithErrorRecovery(
                    lambda: self._mouse_controller.SmoothMoveTo(x, y),
                    f"平滑移动到 ({x}, {y})"
                )
            else:
                return self._ExecuteWithErrorRecovery(
                    lambda: self._mouse_controller.MoveTo(x, y),
                    f"移动到 ({x}, {y})"
                )
                
        except Exception as e:
            raise MouseOperationError(f"鼠标移动操作失败: {str(e)}")
    
    def GetCursorPosition(self) -> Tuple[int, int]:
        """获取当前光标位置"""
        return self._mouse_controller.GetCursorPosition()
    
    #endregion
    
    #region 屏幕管理
    
    def GetScreenRect(self) -> Tuple[int, int, int, int]:
        """获取主屏幕矩形"""
        return self._screen_manager.GetPrimaryScreenRect()
    
    def GetScreenDpi(self) -> float:
        """获取屏幕DPI缩放比例"""
        return self._screen_manager.GetScreenDpi()
    
    def ValidateCoordinates(self, x: int, y: int) -> bool:
        """验证坐标有效性"""
        return self._screen_manager.ValidateCoordinates(x, y)
    
    #endregion
    
    #region 系统监控
    
    def GetSystemMetrics(self) -> SystemMetrics:
        """获取系统性能指标"""
        return self._system_manager.GetSystemMetrics()
    
    def StartResourceMonitoring(self, callback: Callable[[SystemMetrics], None]) -> None:
        """开始资源监控"""
        self._system_manager.MonitorResourceUsage(callback)
    
    def StopResourceMonitoring(self) -> None:
        """停止资源监控"""
        self._system_manager.StopResourceMonitoring()
    
    #endregion
    
    #region 错误恢复机制
    
    def _SetupErrorRecovery(self) -> None:
        """设置错误恢复机制"""
        # 这里可以设置全局错误处理器
        pass
    
    def _ExecuteWithErrorRecovery(self, operation: Callable, operation_name: str) -> Any:
        """带错误恢复的操作执行"""
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                return self._ExecuteWithTimeout(operation, operation_name)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    # 最后一次尝试失败，抛出异常
                    raise e
                
                # 等待后重试
                time.sleep(retry_delay * (attempt + 1))
                
                # 尝试恢复操作
                self._AttemptRecovery(e, operation_name)
    
    def _ExecuteWithTimeout(self, operation: Callable, operation_name: str) -> Any:
        """带超时的操作执行"""
        result_container = []
        exception_container = []
        
        def target():
            try:
                result = operation()
                result_container.append(result)
            except Exception as e:
                exception_container.append(e)
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self._operation_timeout)
        
        if thread.is_alive():
            raise IPlatformException(f"操作超时: {operation_name}")
        
        if exception_container:
            raise exception_container[0]
        
        return result_container[0] if result_container else None
    
    def _AttemptRecovery(self, error: Exception, operation_name: str) -> None:
        """尝试从错误中恢复"""
        try:
            if isinstance(error, HotkeyRegistrationError):
                # 热键注册失败，尝试清理后重新注册
                self._hotkey_manager.UnregisterAll()
                time.sleep(0.1)
                
            elif isinstance(error, MouseOperationError):
                # 鼠标操作失败，尝试重置鼠标状态
                time.sleep(0.05)
                
            elif isinstance(error, SystemResourceError):
                # 系统资源错误，尝试清理资源
                self._system_manager.StopResourceMonitoring()
                time.sleep(0.1)
                
        except:
            # 忽略恢复操作中的异常
            pass
    
    def _ValidateCompatibility(self, compatibility: Dict[str, bool]) -> bool:
        """验证系统兼容性"""
        required_features = [
            'windows_supported',
            'python_version_ok',
            'pynput_available',
            'psutil_available'
        ]
        
        for feature in required_features:
            if not compatibility.get(feature, False):
                return False
        
        return True
    
    #endregion
    
    #region 状态管理
    
    def GetPlatformStatus(self) -> Dict[str, Any]:
        """获取平台状态信息"""
        try:
            with self._lock:
                return {
                    'initialized': self._initialized,
                    'error_recovery_enabled': self._error_recovery_enabled,
                    'keyboard_listening': self._keyboard_listener.IsListening(),
                    'hotkey_count': len(self._hotkey_manager._hotkeys) if hasattr(self._hotkey_manager, '_hotkeys') else 0,
                    'system_metrics': self._system_manager.GetSystemMetrics()._asdict(),
                    'screen_info': self._screen_manager.GetScreenInfo(),
                    'cursor_position': self._mouse_controller.GetCursorPosition()
                }
        except Exception as e:
            return {'error': str(e)}
    
    def SetErrorRecoveryEnabled(self, enabled: bool) -> None:
        """设置错误恢复开关"""
        with self._lock:
            self._error_recovery_enabled = enabled
    
    def SetOperationTimeout(self, timeout_seconds: float) -> None:
        """设置操作超时时间"""
        with self._lock:
            self._operation_timeout = max(1.0, min(30.0, timeout_seconds))
    
    #endregion
    
    #region 上下文管理器支持
    
    @contextmanager
    def managed_platform(self):
        """平台管理器上下文管理器"""
        try:
            self.Initialize()
            yield self
        finally:
            self.Cleanup()
    
    #endregion
    
    #region 资源清理
    
    def __del__(self):
        """析构函数"""
        try:
            self.Cleanup()
        except:
            pass
    
    #endregion